"""
    This file contains all functions related to the simulation of the transit
    distance after removing <fraction> edges.
"""
# Imports 
from _classes import Neighborhood, CBS, Network


def run_simulation(network:Network, kwb:CBS, f: float, dem_grps: list[str], vis_opt):
    """
        Runs the simulation: remove <f> percent of the edges from network and
        analyse effect on distance to the transit points. For details please
        see main function, or manual.  
    """
    # Store information about neighborhoods (5 points + demographic data)
    # key = neighborhood name, value = Neighborhood class
    neighborhoods: dict[str, Neighborhood] = dict()
    
    # TO-DO: add information to neighborhoods 

    # For every node in the network, add an attribute containing the neighborhood.
    


