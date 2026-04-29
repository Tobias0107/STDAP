"""
    All OSMnx related helper functions.
"""

import osmnx as ox


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
