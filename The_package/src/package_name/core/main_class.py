"""
    This file describes the main class structure. (See UML outer_design).
    The other classes are defined in _classes.py

    This class is mostly used as a header file, as well as for defining what
    functions should be public. All functionality should therefore be moved
    to different modules in the package (utils or core) 
"""


# Import packages
# none yet

# Import classes and exceptions
from _classes import Database, Network
from package_name.exceptions import Initializing_error


# Import Simulations from core
import package_name.core._simulation_transit_distance as Sim_trans_dist

# Import helper functions from utils 
# none yet


class simulator:
    """
        This is the main class that will act as a linking class allowing access to
        all methods important for simulating.
    """    
    
    def __init__(self, csv: str, geopackage:str) -> None:
        """ Initializes new instance of the simulator for the given datasets """
        self.database = Database(csv, geopackage)
        self.network = None

    def get_cities(self):
        """ Returns a list of cities available in the given datasets """
        return self.database.get_cities()

    def choose_city(self, city: str):
        """
            Tells the simulator what city to research.
            Should be called at least one before running a simulation.    
        """
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
            <Here a description of the exact simulation>
        """
        if (self.network == None):
            raise Initializing_error("City not yet initialized. Before running" \
            "this simulation, call 'choose_city' first. For details, see manual.")
        
        return Sim_trans_dist.run_simulation(self.network, self.database, fraction,
                                             demographic_groups, visual_options)
