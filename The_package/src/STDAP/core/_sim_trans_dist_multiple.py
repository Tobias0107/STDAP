"""
    This file contains the run_simulation function containing the function logic used by the main class
    to simulate pedestrianization on a range of fractions.
"""

# Imports
import networkx as nx
import geopandas as gpd
import pandas as pd
from STDAP.core._classes import Database, Network
import STDAP.utils.util_plotting as plot
import numpy as np


def run_simulation(network:Network, database:Database, f_start, f_end, fn, use_population: bool,
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
            - f_start (Numeric):\n
                First fraction to pedestrianize
            - f_end (Numeric):\n
                Last fraction to pedestrianize
            - fn (Numeric):\n
                Number of fractions to pedestrianize in total
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

    ###########################################################################
    ############## Pre-processing, done once per city #########################
    ###########################################################################

    if print_progress: print("Loading city network into database")
    database.load_network(network)

    if print_progress: print("Obtaining city amenities and public transit")
    database.obtain_features()

    if print_progress: print("Pre-processing network")
    database.pre_process()

    if print_progress: print("Creating points for every neighborhood")
    database.create_pts_per_neighborhood()

    if print_progress: print(f"Linking bus_stations to the network")
    database.link_busses()

    ###########################################################################
    #################### run simulation for all fractions #####################
    ###########################################################################

    # Not really used, but I have it anyway.
    neighborhood_dists = []
    # Store all DataFrames, combine into one later.
    dem_grp_avg_lst: list[pd.DataFrame] = []

    rng: np.typing.NDArray[np.float64] = np.linspace(f_start, f_end, fn)
    for f in rng.astype(float):

        if print_progress: print(f"(f: {round(f, 2)}) Removing {round(f * 100, 2)}% of the driving network length")
        database.remove_f_edges(f, use_population, use_amenity)

        if print_progress and simple_move: print(f"(f: {round(f, 2)}) Moving invalid transit stops to nearest valid place")
        if simple_move: database.move_transit_minimal()
        if print_progress and blank_slate: print(f"(f: {round(f, 2)}) Using blank slate method to re-generate transit stops")
        if blank_slate: database.move_transit_blank_slate()

        if print_progress: print(f"(f: {round(f, 2)}) Re-calculating distances to public transit")
        database.calculate_distances_to_nearest_transit()

        if print_progress: print(f"(f: {round(f, 2)}) Retrieving average distance per neighborhood")
        neighborhood_dists.append(database.get_dist_per_neighborhood())

        if print_progress: print(f"(f: {round(f, 2)}) Retrieving average distance per demographic group")
        df = database.get_demographic_average_distance()
        df["f"] = f
        dem_grp_avg_lst.append(df)

    # Combine DataFrame list into one list
    dem_grp_avgs = pd.concat(dem_grp_avg_lst, ignore_index=True)

    ###########################################################################
    ############################ Visualization ################################
    ###########################################################################

    # Plot the DataFrame
    if print_progress: print("Visualizing simulation results")
    plot.DataFrame(dem_grp_avgs,
                   x_col='f',
                   y_col='avg_dist',
                   label_col='dem_grp',
                   xlabel='Fraction pedestrianized',
                   ylabel='Average distance',
                   title=f'Average distance per fraction: {database.city}',
                   subtitle='',
                   storage_folder=saving_dir,
                   name=f'Average distance per fraction. {database.city}',
                   svg=svg,
                   multiple_figures=True)

    return dem_grp_avgs
