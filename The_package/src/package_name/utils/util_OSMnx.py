"""
    All OSMnx related helper functions.
"""

import osmnx as ox


def get_graph(city:str, network_type="drive"):
    """
    ### Returns: 
    projected(epsg:28992) osmnx graph of given city. Only car-accessible roads.
    ### Parameters:
    city: \n
        A city name of a city in the Netherlands, the name should be in Dutch.
    network_type: \n
        The type of roads to import: default = 'drive' (car-accessible).
    """
    ox.settings.bidirectional_network_types += network_type
    G = ox.graph_from_place(f"{city}, Netherlands", simplify=True, network_type=network_type)
    return ox.project_graph(G, to_crs="epsg:28992", to_latlong=False)

