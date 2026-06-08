"""
    A basic example showing the usage of the STDAP package.
    First time run downloads graph data, can take a long time.
"""

# Import Simulator class: the main class used for the simulations 
from STDAP.core.main_class import Simulator
# Optionally import the settings class for further configuration
from STDAP.config.settings import get_settings 
# Optionally import PoissonDiskDistribution default function to alter parameters
from STDAP.config.functions import PoissonDiskDistribution

# Path to the manually downloaded CBS packages

csv = "kwb2024.csv" # https://www.cbs.nl/nl-nl/maatwerk/2025/40/kerncijfers-wijken-en-buurten-2024
geopackage = "geopackage.gpkg" # https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/wijk-en-buurtkaart-2025

# Get settings class to configure simulation
settings = get_settings()

# The 2024 CBS dataset uses some different columns compared to the default values
settings.dataset_column_names['high_education'] = "a_opl_bvm"
settings.dataset_column_names['medium_education'] = "a_opl_hvm"
settings.dataset_column_names['low_education'] = "a_opl_hw"
settings.dataset_nullstring = ['       .', '.', '']

# Re-define radius used by PoissonDiskDistribution function
settings.neighborhood_distribution = lambda a, b, c, d : PoissonDiskDistribution(a, b, c, d, radius=100)


# Initiate simulator with datasets, specify graphs should be downloaded to speed up later simulations
sim = Simulator(csv, geopackage, store_in_file=True, storage_dir="The_downloaded_graphs/")

# Get optional cities from dataset (default ordered by name)
city_options = sim.get_cities()

# Choose city
sim.choose_city("Amsterdam")

# Simulate using 25% pedestrianization, completely redesigning the bus-network
sim.Sim_trans_dist_single(0.25,
                          svg=False,
                          bus_network_redesign=True,
                          minimal_move=False,
                          saving_dir="results_example/blank-slate/percentages/25%/")

# Simulate over a range of fractions to pedestrianize, move bus-stops to nearest valid location.
sim.Sim_trans_dist_multiple(0,
                            0.5,
                            100,
                            svg=False,
                            bus_network_redesign=False,
                            minimal_move=True,
                            saving_dir="results_example/minimal/range/")
