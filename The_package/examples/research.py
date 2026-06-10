"""
    This file contains the code used to research the effects of pedestrianization
    on transit stop distance (Thesis by Tobias van den Bosch).
    The code is cleaned up to be more readable.
"""

from STDAP.core.main_class import Simulator
from STDAP.config.settings import get_settings
import STDAP.utils.util_plotting as plot
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import gc
from itertools import product

# Path to manually downloaded datasets
csv = "Datasets/kwb2024.csv" # https://www.cbs.nl/nl-nl/maatwerk/2025/40/kerncijfers-wijken-en-buurten-2024
geopackage = "Datasets/geopackage.gpkg" # https://www.cbs.nl/nl-nl/maatwerk/2025/40/kerncijfers-wijken-en-buurten-2024

# Set configuration to match 2024 dataset columns
settings = get_settings()
settings.dataset_column_names['high_education'] = "a_opl_bvm"
settings.dataset_column_names['medium_education'] = "a_opl_hvm"
settings.dataset_column_names['low_education'] = "a_opl_hw"
settings.dataset_nullstring = ['       .', '.', '']

# Define the large cities to run simulations for
large_cities = [
    "Amsterdam",
    "Rotterdam",
    "'s-Gravenhage",
    "Utrecht",
    "Eindhoven",
    "Groningen",
    "Tilburg",
    "Almere",
    "Breda",
    "Nijmegen",
    "Apeldoorn",
    "Haarlem",
    "Arnhem",
    "Haarlemmermeer",
    "Amersfoort",
    "Enschede",
    "Zaanstad",
    "'s-Hertogenbosch",
    "Zwolle",
    "Leeuwarden"
]

# The basic parameters used to quickly configure simulation parameters
folder = "Results"
show_progress = True
svg_format = False
cache_networks = True
cache_folder = "network_cache"
f_start = 0
f_stop = 0.5
fn = 10
frac_1 = 0.1
frac_2 = 0.25

# Initialize simulator
sim = Simulator(csv, geopackage, store_in_file=cache_networks, storage_dir=cache_folder)

# Initializing different simulation options
ped_opt = [(True, True, "Hybrid"),
           (True, False, "Population_based"),
           (False, True, "Amenity_based")]
bus_mv_opt = [(True, False, "Nearest"),
              (False, True, "Transit_redesign")]

###############################################################################
############################ Perform simulations ##############################
###############################################################################

# Loop over all possible combinations of simulation options
for i, ((pop, amenity, ped_method),
       (minimal, redesign, mv_method)) in enumerate(product(ped_opt, bus_mv_opt), start=1):
    if show_progress: print(f"\n\nSimulating using the {ped_method} method and the {mv_method} method.\n\n")

    # Loop over every city
    for j, city in enumerate(large_cities, start=1):
        if show_progress: print(f"\n({i * j} / {6 * len(large_cities)}) Simulating city: {city} using {ped_method} pedestrianization and {mv_method} transit movement.\n")

        # Write intermediate results to files in case this simulation crashes
        storage_folder = os.path.join(cache_folder, city, ped_method, mv_method)
        if not os.path.isdir(storage_folder):
            os.makedirs(storage_folder)

        #######################################################################
        ################# Simulate for the single city ########################
        #######################################################################
        # Select the city so simulate
        sim.choose_city(str(city))

        # Simulate the for all fractions pedestrianized
        df = sim.Sim_trans_dist_multiple(f_start, f_stop, fn,
                                         use_population=pop,
                                         use_amenity=amenity,
                                         minimal_move=minimal,
                                         bus_network_redesign=redesign,
                                         print_progress=show_progress,
                                        # Store results in a nice to use file structure
                                         saving_dir=os.path.join(folder, city, ped_method, mv_method, "fraction_range"),
                                         svg=svg_format)
        # Write results to file (RAM saver)
        df.to_parquet(os.path.join(storage_folder, "range.parquet"))
        del df
        gc.collect()

        # Simulate for the individual fractions
        sim.Sim_trans_dist_single(frac_1,
                                  use_population=pop,
                                  use_amenity=amenity,
                                  minimal_move=minimal,
                                  bus_network_redesign=redesign,
                                  print_progress=show_progress,
                                 # Store results in a nice to use file structure
                                  saving_dir=os.path.join(folder, city, ped_method, mv_method, "individual_fractions", f"{frac_1 * 100}%"),
                                  svg=svg_format)        
        sim.Sim_trans_dist_single(frac_2,
                                  use_population=pop,
                                  use_amenity=amenity,
                                  minimal_move=minimal,
                                  bus_network_redesign=redesign,
                                  print_progress=show_progress,
                                 # Store results in a nice to use file structure
                                  saving_dir=os.path.join(folder, city, ped_method, mv_method, "individual_fractions", f"{frac_1 * 100}%"),
                                  svg=svg_format)
        # Just in case
        plt.close("all")

    ###########################################################################
    ######################## Visualize average results ########################
    ###########################################################################

    # Re-obtain the stored results
    multiple_lst: list[pd.DataFrame] = []
    for city in sim.get_cities():
        df = pd.read_parquet(os.path.join(cache_folder, str(city), ped_method, mv_method, "range.parquet"))
        multiple_lst.append(df)

    # Visualize average results
    plot.DataFrames(multiple_lst,
                    x_col='f',
                    y_col='avg_dist',
                    label_col='dem_grp',
                    xlabel='Fraction pedestrianized',
                    ylabel='Average distance',
                    title=f'Distance nearest transit: Average',
                    subtitle='',
                   # Store results in a nice to use file structure
                    storage_folder=os.path.join(folder, "Average", ped_method, mv_method),
                    name=f'Distance nearest transit: Average',
                    svg=svg_format,
                    multiple_figures=True)
