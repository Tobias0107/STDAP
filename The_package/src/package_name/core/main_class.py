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
from package_name.core._classes import Database, Network
from package_name.exceptions import Initializing_error


# Import Simulations from core
import package_name.core._sim_trans_dist_single as Sim_trans_dist
import package_name.core._sim_trans_dist_multiple as Sim_trans_dist_fn

# Import helper functions from utils
# none yet


class simulator:
    """
        This is the main class that will act as a linking class allowing access to
        all methods important for simulating.
    """

    def __init__(self, csv: str, geopackage:str, store_in_file=False, storage_dir='network_cache/') -> None:
        """ Initializes new instance of the simulator for the given datasets """
        self.database = Database(csv, geopackage)
        self.network = None
        self.store_in_file = store_in_file
        self.storage_dir = storage_dir

    def get_cities(self):
        """ Returns a list of cities available in the given datasets """
        return self.database.get_cities()

    def choose_city(self, city: str):
        """
            Tells the simulator what city to research.
            Should be called at least one before running a simulation.
        """
        self.network = Network(city, self.store_in_file, self.storage_dir)
        self.database.set_city(city)

    def Sim_trans_dist_single(self, fraction: float, *, use_population=True,
                              use_amenity=True, minimal_move=True, blank_slate=False,
                              print_progress=True, saving_dir="results_sim_transit_dist/",
                              svg=False):
        """
            ### Description:
                <Here a short description of the simulation>
            ### Expects:
                - load_city method called previously
            ### Parameters:
                - network (Network)
                - database (Database)
                - f (float)\n
                    fraction of the car-accessible streets to transform to pedestrian
                - print_progress: \n
                    If True: Prints the progress of the simulation to stdout. As simulations can take
                    a long time this is highly recommended.
                - saving_dir: \n
                    The directory to save the results (if any).
            ### Returns:
                - The average results aper demographic group in the form of a dictionary
        """
        if (self.network == None):
            raise Initializing_error("City not yet initialized. Before running" \
                "this simulation, call 'choose_city' first. For details, see manual.")

        return Sim_trans_dist.run_simulation(self.network, self.database, fraction, use_population,
                                             use_amenity, minimal_move, blank_slate,
                                             print_progress, saving_dir, svg)

    def Sim_trans_dist_multiple(self, f_start, f_end, fn, *, use_population=True,
                                use_amenity=True, minimal_move=True, blank_slate=False,
                                print_progress=True, saving_dir="results_sim_transit_dist/", svg=False):
        """
            ### Description:
                <Here a short description of the simulation>
            ### Expects:
                - load_city method called previously
            ### Parameters:
                - network (Network)
                - database (Database)
                - f (float)\n
                    fraction of the car-accessible streets to transform to pedestrian
                - print_progress: \n
                    If True: Prints the progress of the simulation to stdout. As simulations can take
                    a long time this is highly recommended.
                - saving_dir: \n
                    The directory to save the results (if any).
            ### Returns:
                - The average results aper demographic group in the form of a dictionary
        """
        if (self.network == None):
            raise Initializing_error("City not yet initialized. Before running" \
                "this simulation, call 'choose_city' first. For details, see manual.")

        return Sim_trans_dist_fn.run_simulation(self.network, self.database, f_start, f_end, fn, use_population,
                                                use_amenity, minimal_move, blank_slate,
                                                print_progress, saving_dir, svg)
