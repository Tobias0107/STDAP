"""
    This file describes the main class structure. (See UML outer_design).
    The other classes are defined in _classes.py
"""

# Import packages
import networkx as nx
import osmnx as ox

# Import classes and exceptions
from _classes import Neighborhood, CBS, Network
from Package_name.exceptions import Initializing_error


# Import Simulations
import Package_name.core._simulation_transit_distance as Sim_trans_dist


class simulator:
    """
        This is the main class that will act as a linking class allowing access to
        all methods important for simulating.
    """    
    
    def __init__(self, csv: str, geopackage:str) -> None:
        self.network = None
        self.kwb = CBS(csv, geopackage)

    def get_cities(self):
        pass

    def choose_city(self, city: str):
        self.network = Network(city)

    def Simulate_transit_dist_on_trans(self, fraction: float,
                                       demographic_groups: list[str],
                                       visual_options):
        """
            ### Input:
            fraction: \n
                The fraction of car-accessible streets to transform to pedestrian area.
            demographic_groups: \n
                A list of demographic groups to take into account during simulation.
            visual_options: \n
                The visual options (split into more parameters later)
            
            ### Simulation:
            See requirements
        """
        if (self.network == None):
            raise Initializing_error("City not yet initialized. Before running" \
            "this simulation, call 'choose_city' first. For details, see manual.")
        
        return Sim_trans_dist.run_simulation(self.network, self.kwb, fraction, demographic_groups, visual_options)
