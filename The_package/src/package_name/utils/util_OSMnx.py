"""
    All OSMnx related helper functions.
"""

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
    ox.settings.use_cache = True
    query = {'city': city, 'country': 'Netherlands'}
    place_gdf = ox.geocode_to_gdf(query)
    polygon = place_gdf.geometry.iloc[0]
    polygon = polygon.simplify(0.001)
    gdf = ox.features_from_polygon(polygon, tags=tags)
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
