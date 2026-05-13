"""
    All OSMnx related helper functions.
"""

import requests
import time
import osmnx as ox
import duckdb as db

def get_graph(city:str, project=True, network_type="drive"):
    """
    ### Returns:
    - projected(epsg:28992) osmnx graph of given city. Only car-accessible roads.
    ### Side effects:
    - None
    ### Parameters:
    - city: \n
        A city name of a city in the Netherlands, the name should be in Dutch.
    - network_type: \n
        The type of roads to import: default = 'drive' (car-accessible).
    """
    # if network_type not in ox.settings.bidirectional_network_types:
    #     ox.settings.bidirectional_network_types.append(network_type)
    G = ox.graph_from_place(f"{city}, Netherlands", simplify=True, retain_all=True, network_type=network_type)
    if project:
        return ox.project_graph(G, to_crs="epsg:28992", to_latlong=False)
    else:
        return G

def get_features(city:str, amenity=True, public_transport=True, project=True):
    """
    ### Returns:
    - GeoDataFrame containing the public_transport and/or the amenities
    ### Side effects:
    - If amenity and public_transport are both False, it will raise an ValueError
    ### Parameters:
    - amenity:\n
        If True: Includes all amenity features
    - public_transport:\n
        If True: Includes public all public transport features
    """
    if amenity and public_transport:
        tags = {"amenity": True, "public_transport": True}
    elif amenity and not public_transport:
        tags = {"amenity": True}
    elif not amenity and public_transport:
        tags = {"public_transport": True}
    else:
        raise ValueError("amenity and public_transport can not be both False.")
    gdf = ox.features_from_place(f"{city}, Netherlands", tags=tags)  # pyright: ignore[reportArgumentType]
    if project:
        return ox.projection.project_gdf(gdf, to_crs="epsg:28992", to_latlong=False)
    else:
        return gdf

def count_bus_routes(city: str, conn: db.DuckDBPyConnection):
    """
    ### Note:
    Might fail, therefore, has 10 retries with exponential waiting time (2^i).
    ### Description:
    Queries the overpass api directly to count the number of bus-routes in the city
    ### Returns:
    - bus-route count (int) OR None if all attempts failed.
    ### Side effects:
    - None
    ### Parameters:
    - city:\n
        The city to count the bus_routes of
    - conn: \n
        A duckdb connection used to quickly parse json
    """
    headers = {
        'User-Agent': 'SimulateTransitDist/1.0 (purespamtobias@gmail.com)',
        'Accept-Language': 'en'
    }
    query = f"""
    [out:json][timeout:60];
    area[name="Amsterdam"][admin_level=8]->.searchArea;

    relation["type"="route"]["route"="bus"](area.searchArea);

    out body;
    """
    # API call (obtain json)
    data = None
    for i in range(1, 6):
        try:
            response = requests.post("https://overpass-api.de/api/interpreter", data={'data': query.encode('utf-8')}, headers=headers)
            response.raise_for_status()
            data = response.json()
            break
        except Exception as e:
            print(f"Importing bus routes {city} failed. Waiting {2**i} seconds before retry.")
            time.sleep(2**i)
    if not data: raise Exception(f"All tries of obtaining bus line count for {city} failed")

    # parse json to count
    count = conn.sql("""
        SELECT count(DISTINCT e.tags.ref) AS cnt
        FROM (
            SELECT unnest(elements) AS e
            FROM read_json(data)
        )
        WHERE e.type = 'relation'
        AND e.tags.route = 'bus';
    """).fetchone()[0] # type: ignore

    return count
