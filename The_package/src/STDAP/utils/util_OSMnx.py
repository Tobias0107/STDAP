"""
    All OSMnx related helper functions.
"""

import requests
import time
import osmnx as ox
import duckdb as db

tags = {
    "tourism": [
        "hotel",
        "hostel",
        "guest_house",
        "motel",
        "museum",
        "gallery",
        "attraction",
        "viewpoint",
        "artwork",
        "camp_site",
        "theme_park",
        "zoo",
        "aquarium",
        "picnic_site",
        "information"
    ],
    "leisure": [
        "park",
        "garden",
        "nature_reserve",
        "playground",
        "sports_centre",
        "stadium",
        "fitness_centre",
        "swimming_pool",
        "golf_course",
        "marina",
        "water_park",
        "amusement_arcade"
    ],
    "amenity": [
        "cinema",
        "theatre",
        "arts_centre",
        "library",
        "community_centre",
        "nightclub",
        "casino",
        "restaurant",
        "cafe",
        "bar",
        "pub",
        "fast_food",
        "food_court",
        "ice_cream",
        "biergarten",
        "place_of_worship",
        "university",
        "college",
        "school",
        "hospital",
        "clinic",
        "pharmacy",
        "doctors",
        "dentist",
        "bank",
        "atm",
        "post_office"
    ],
    "historic": [
        "castle",
        "monument",
        "memorial",
        "ruins",
        "archaeological_site"
    ],
    "natural": [
        "beach",
        "peak",
        "waterfall",
        "cave_entrance",
        "hot_spring"
    ],
    "office": True,
    "craft": True,
    "shop": True,
    "public_transport": True
}

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
    ox.settings.use_cache = False
    query = {'city': city, 'country': 'Netherlands'}
    place_gdf = ox.geocode_to_gdf(query)
    polygon = place_gdf.geometry.iloc[0]







    polygon = polygon.simplify(0.001)
    G = ox.graph_from_polygon(polygon, simplify=True, retain_all=True, network_type=network_type)
    if project:
        return ox.project_graph(G, to_crs="epsg:28992", to_latlong=False)
    else:
        return G

def get_features(city:str, project=True):
    """
    ### Returns:
    - GeoDataFrame containing the public_transport and/or the amenities
    ### Side effects:
    - If amenity and public_transport are both False, it will raise an ValueError
    ### Parameters:
    """
    # ox.settings.log_console = True
    ox.settings.use_cache = True
    query = {'city': city, 'country': 'Netherlands'}
    place_gdf = ox.geocode_to_gdf(query)
    polygon = place_gdf.geometry.iloc[0]
    polygon = polygon.simplify(0.001)
    gdf = ox.features_from_polygon(polygon, tags=tags)

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
