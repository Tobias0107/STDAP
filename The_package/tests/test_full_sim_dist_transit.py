"""
    This file contains the full simulation performed for the paper:
    Modeling Pedestrianization in Dutch Urban Street Networks: Impacts on Transit
    Accessibility for different Demographic Groups
"""

from package_name.core.main_class import simulator
from package_name.config.settings import get_settings
from package_name.config.functions import PoissonDiskDistribution
import package_name.utils.util_plotting as plot
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import gc
from itertools import product


csv = "tests/TestDatasets/kwb2024.csv"
geopackage = "tests/TestDatasets/geopackage.gpkg"

settings = get_settings()

settings.dataset_column_names['high_education'] = "a_opl_bvm"
settings.dataset_column_names['medium_education'] = "a_opl_hvm"
settings.dataset_column_names['low_education'] = "a_opl_hw"
settings.dataset_nullstring = ['       .', '.', '']
settings.neighborhood_distribution = lambda a, b, c, d : PoissonDiskDistribution(a, b, c, d, radius=30)


class TestMultipleFractions:
    def test_main(self):
        # Basic parameters
        folder = "Results"
        show_progress = True
        svg_format = False
        cache_networks = True
        f_start = 0
        f_stop = 0.5
        fn = 10

        large_cities = [
            # "Amsterdam",
            # "Rotterdam",
            "'s-Gravenhage",
            "Utrecht",
            "Eindhoven",
            # "Groningen",
            # "Tilburg",
            # "Almere",
            # "Breda",
            # "Nijmegen",
            # "Apeldoorn",
            "Haarlem",
            # "Arnhem",
            # "Haarlemmermeer",
            # "Amersfoort",
            # "Enschede",
            # "Zaanstad",
            # "'s-Hertogenbosch",
            # "Zwolle",
            # "Leeuwarden"
        ]

        # Fractions of interest (max two per city)
        min_1 = 0.1
        min_2 = 0.25
        blank_1 = 0.0

        # Initialize simulator
        sim = simulator(csv, geopackage, store_in_file=cache_networks)

        # Initializing different simulation options
        ped_opt = [(True, True, "Hybrid"),
                   (True, False, "Population_based"),
                   (False, True, "Amenity_based")]
        bus_mv_opt = [(True, False, "Nearest"),
                      (False, True, "Blank-Slate")]

        #######################################################################
        ######### Perform simulations #########################################
        #######################################################################


        # 6 different simulation options
        for i, ((pop, amenity, ped_method),
               (minimal, blank, mv_method)) in enumerate(product(ped_opt, bus_mv_opt), start=1):
            if show_progress: print(f"\n\nSimulating using the {ped_method} method and the {mv_method} method.\n\n")

            # For every city
            # for i, city in enumerate(sim.get_cities(order_by="pop", limit=10)):
            for j, city in enumerate(large_cities, start=1):
                if show_progress: print(f"\n({i * j} / {6 * len(large_cities)}) Simulating city: {city} using {ped_method} pedestrianization and {mv_method} transit movement.\n")

                try:
                    # Choose city
                    if show_progress: print(f"Obtaining network from API or Cached files")
                    sim.choose_city(str(city))

                    # Simulate for all fractions
                    df = sim.Sim_trans_dist_multiple(f_start, f_stop, fn,
                                                     use_population=pop,
                                                     use_amenity=amenity,
                                                     minimal_move=minimal,
                                                     blank_slate=blank,
                                                     print_progress=show_progress,
                                                     saving_dir=os.path.join(folder, ped_method, mv_method, "fraction_range", str(city)),
                                                     svg=svg_format)
                    # Store in file to save RAM
                    storage_folder = os.path.join("network_cache", ped_method, mv_method)
                    if not os.path.isdir(storage_folder):
                        os.makedirs(storage_folder)
                    df.to_parquet(os.path.join(storage_folder, str(city) + ".parquet"))
                    del df

                    # Generate results for interesting fractions
                    sim.Sim_trans_dist_single(min_1,
                                            use_population=pop,
                                            use_amenity=amenity,
                                            minimal_move=minimal,
                                            blank_slate=blank,
                                            print_progress=show_progress,
                                            saving_dir=os.path.join(folder, ped_method, mv_method, "individual_fractions", f"{min_1}%", str(city)),
                                            svg=svg_format)
                    sim.Sim_trans_dist_single(min_2,
                                            use_population=pop,
                                            use_amenity=amenity,
                                            minimal_move=minimal,
                                            blank_slate=blank,
                                            print_progress=show_progress,
                                            saving_dir=os.path.join(folder, ped_method, mv_method, "individual_fractions", f"{min_2}%", str(city)),
                                            svg=svg_format)
                    sim.Sim_trans_dist_single(blank_1,
                                            use_population=pop,
                                            use_amenity=amenity,
                                            minimal_move=minimal,
                                            blank_slate=blank,
                                            print_progress=show_progress,
                                            saving_dir=os.path.join(folder, ped_method, mv_method, "individual_fractions", f"{blank_1}%", str(city)),
                                            svg=svg_format)
                    # Against memory problems
                    del sim
                    sim = simulator(csv, geopackage, store_in_file=cache_networks)
                    plt.close("all")
                    gc.collect()
                except Exception as e:
                    print(f"! Encountered error ({e}).\n If not during plotting: {city} likely misses key amenities / networks and is most likely not a city.\nSkipping to next city...\n")
                    plt.close("all")
                    gc.collect()

            # Store results to calculate avg for entire Netherlands
            multiple_lst: list[pd.DataFrame] = []
            for city in sim.get_cities():
                try:
                    df = pd.read_parquet(os.path.join("network_cache", ped_method, mv_method, str(city) + ".parquet"))
                    multiple_lst.append(df)
                except Exception:
                    pass

            # Plot Netherlands average
            plot.DataFrames(multiple_lst,
                    x_col='f',
                    y_col='avg_dist',
                    label_col='dem_grp',
                    xlabel='Fraction pedestrianized',
                    ylabel='Average distance',
                    title=f'Distance nearest transit: Netherlands',
                    subtitle='',
                    storage_folder=os.path.join(folder, ped_method, mv_method),
                    name=f'Distance nearest transit: Netherlands',
                    svg=svg_format,
                    multiple_figures=True)
