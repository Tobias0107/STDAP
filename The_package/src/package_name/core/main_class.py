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
        self.database.set_city(city)

    def Simulate_transit_dist_on_trans(self, fraction: float, *,
                   gender=True, age=True, ethnicity=True, SES=True,
                   save_old_network=True, save_new_network=True,
                   color_new_network=True, save_bar_diagram=True,
                   print_progress=True, saving_dir="results_sim_transit_dist/"):
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
                - gender: \n
                    If True: displays simulation results for gender
                - age: \n
                    If True: displays simulation results for age
                - ethnicity: \n
                    If True: displays simulation results for ethnicity
                - SES: \n
                    If True: displays simulation results for Social Economic Status (SES)
                - Save_old_network: \n
                    If True: saves the network pre-transformation in png format
                - Save_new_network: \n
                    If True: saves the network after transformation in png format
                - color_new_network: \n
                    If True: gives colors to neighborhoods in the network based on the
                    average calculated new distance one has to travel to transit.
                    Red = Big increase (relative to other neighborhoods)
                    Orange = Small increase (relative to other neighborhoods)
                    Yellow = Practically remains the same
                    Light green = Distance is slightly decreased
                    Dark green = Distance is greatly decreased
                - save_bar_diagram: \n
                    If True: Saves the average results per demographic group in the form of a bar
                    diagram (png).
                - print_progress: \n
                    If True: Prints the progress of the simulation to stdout. As simulations can take
                    a long time this is highly recommended.
                - print_simulation_steps: \n
                    If True: Prints the current simulation step to stdout. This can provide for more
                    insight in the simulation progress.
                - saving_dir: \n
                    The directory to save the results (if any).
            ### Returns:
                - The average results aper demographic group in the form of a dictionary
        """
        if (self.network == None):
            raise Initializing_error("City not yet initialized. Before running" \
            "this simulation, call 'choose_city' first. For details, see manual.")

        return Sim_trans_dist.run_simulation(self.network, self.database, fraction,
                                             gender, age, ethnicity, SES,
                                             save_old_network, save_new_network,
                                             color_new_network, save_bar_diagram,
                                             print_progress, saving_dir="results_sim_transit_dist/")


