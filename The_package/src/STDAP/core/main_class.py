"""
    This file contains the main class (Simulator).
"""

# Import classes and exceptions
from STDAP.core._classes import Database, Network
from STDAP.exceptions import Initializing_error

# Import Simulations from core
import STDAP.core._sim_trans_dist_single as Sim_trans_dist
import STDAP.core._sim_trans_dist_multiple as Sim_trans_dist_fn


class Simulator:
    """
        This is the main class that contains all simulating logic.
        The class contains two simulations.
        - One simulation visualizing the effects of a single pedestrianization
        - One simulation visualizing the effects of pedestrianization over a
            range of fractions pedestrianized

        Simulations can be run as follows:\n
        - sim = Simulator(datasets, options)
        - optional_cities = sim.get_cities()
        - sim.choose_city(optional_cities[x])
        - sim.Sim_trans_dist_single(simulation_options) OR Sim_trans_dist_multiple(simulation_options)
    """

    def __init__(self, csv: str, geopackage:str, store_in_file=False, storage_dir='network_cache/'):
        """
            ### Description:
                - Creates a new instance of the Simulator class
            ### Parameters:
                - csv:\n
                    The path to the CBS dataset called "Kerncijfers wijken en buurten xxxx" in csv format.
                    Link to possible datasets: "https://www.cbs.nl/nl-nl/reeksen/publicatie/kerncijfers-wijken-en-buurten"
                    Due to differences in csv columns, some datasets require column settings to be set.
                - geopackage:\n
                    The path to the CBS dataset called "Wijk- en buurtkaart 2025 versie 1" in geopackage format.
                    Link to dataset: "https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/wijk-en-buurtkaart-2025"
                - store_in_file:\n
                    If true, stores API network import in file for later use.
                - store_dir: \n
                    The directory to store and look for downloaded networks.    \
            ### Returns:
                - An instance of the Simulator class.
        """
        self.database = Database(csv, geopackage)
        self.network = None
        self.store_in_file = store_in_file
        self.storage_dir = storage_dir

    def get_cities(self, order_by="gm_naam", limit="342"):
        """
            ### Description:
                - Extracts available cities (gm_naam) from the given datasets.
            ### Parameters:
                - order_by:\n
                    The ordering of the cities. Default is by city name.
                - limit:\n
                    The limit in the number of cities to return. Default = all 342 cities.
            ### Returns:
                - A list of cities available in the given datasets.
        """
        return self.database.get_cities(order_by, limit)

    def choose_city(self, city: str):
        """
            ### Description:
                Tells the simulator what city to simulate.
                Should be called at least one before running a simulation.
            ### Parameters:
                - city:\n
                    The Dutch city name
            ### Returns:
                - None
        """
        self.network = Network(city, self.store_in_file, self.storage_dir)
        self.database.set_city(city)

    def Sim_trans_dist_single(self, fraction: float, *, use_population=True,
                              use_amenity=True, minimal_move=True, bus_network_redesign=False,
                              print_progress=True, saving_dir="results_sim_transit_dist/",
                              svg=False):
        """
            ### Description:
                Simulates the effects of pedestrianization to transit stop distance.
                Simulations may use a demand based, supply based or a hybrid method of pedestrianization.
                Simulations move transit stops by either redesigning the bus-network,
                or by moving transit stops to the nearest location that is not isolated or located on a dead end.
                The visualized results are stored in the saving_dir.
            ### Expects:
                - The city to be chosen. (.choose_city(city_name))
            ### Parameters:
                - network (Network)
                - database (Database)
                - f (float):\n
                    fraction of the car-accessible street length to transform to pedestrian
                - use_population (bool):\n
                    If true, factors in the population when pedestrianizing.
                    If False, use_amenity should be True.
                - use_amenity (bool):\n
                    If true, factors in the amenity when pedestrianizing.
                    If False, use_population should be True.
                - simple_move (bool):\n
                    If true, uses the minimal/iterative method to move transit stops.
                    simple_move xor bus_network_redesign should be true
                - bus_network_redesign (bool):\n
                    If true, uses the blank-slate method to move transit stops.
                    simple_move xor bus_network_redesign should be true
                - print_progress: \n
                    If True: Prints the progress of the simulation to stdout.
                    As simulations can take a long time this is highly recommended.
                - saving_dir: \n
                    The directory to save the results (if any).
                - svg: \n
                    If True: uses svg format for results, png otherwise.
            ### Returns:
                - The average results per demographic group in the form of a dictionary
        """
        if (self.network == None):
            raise Initializing_error("City not yet initialized. Before running" \
                "this simulation, call 'choose_city' first. For details, see manual.")

        return Sim_trans_dist.run_simulation(self.network, self.database, fraction, use_population,
                                             use_amenity, minimal_move, bus_network_redesign,
                                             print_progress, saving_dir, svg)

    def Sim_trans_dist_multiple(self, f_start, f_end, fn, *, use_population=True,
                                use_amenity=True, minimal_move=True, bus_network_redesign=False,
                                print_progress=True, saving_dir="results_sim_transit_dist/", svg=False):
        """
            ### Description:
                Simulates the effects of pedestrianization to transit stop distance over a range of fractions.
                Simulations may use a demand based, supply based or a hybrid method of pedestrianization.
                Simulations move transit stops by either redesigning the bus-network,
                or by moving transit stops to the nearest location that is not isolated or located on a dead end.
                The visualized results are stored in the saving_dir.
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
                                                use_amenity, minimal_move, bus_network_redesign,
                                                print_progress, saving_dir, svg)
