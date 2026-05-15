"""
    This file contains all functions related to the simulation of the transit
    distance after removing <fraction> edges.
"""
# Imports
import networkx as nx
import geopandas as gpd
from package_name.core._classes import Database, Network
import package_name.utils.util_plotting as plot
import numpy as np

def run_simulation(network:Network, database:Database, f_start, f_end, step_size, use_population: bool,
                   use_amenity: bool, simple_move: bool, blank_slate: bool,
                   print_progress: bool, saving_dir: str, svg: bool):
    """
        ### Expects:
            - network == Network(city)
            - database == Database(csv, geopackage)
            - database.set_city(city) called
            - network.city == database.city
        ### Parameters:
            - network (Network)
            - database (Database)
            - f (float):\n
                fraction of the car-accessible street length to transform to pedestrian
            - use_population (bool):\n
                If true, factors in the population when pedestrianizing. If False, use_amenity should be True.
            - use_amenity (bool):\n
                If true, factors in the amenity when pedestrianizing. If False, use_population should be True.
            - simple_move (bool):\n
                If true, uses the minimal/iterative method to move transit stops. simple_move xor blank_slate should be true
            - blank_slate (bool):\n
                If true, uses the blank-slate method to move transit stops. simple_move xor blank_slate should be true
            - print_progress: \n
                If True: Prints the progress of the simulation to stdout. As simulations can take
                a long time this is highly recommended.
            - saving_dir: \n
                The directory to save the results (if any).
            - svg: \n
                If True: uses svg format for results, png otherwise.
        ### Returns:
            - The average results per demographic group in the form of a dictionary
        ### Side effects:
            - Removes edges from network
            - Adds tables to database
            - Creates files containing visualizations
    """

    if print_progress: print(f"\n\nRunning multiple fractions pedestrianization simulation for {database.city}\n\n")

    rng = np.arange(f_start, f_end, step_size)

