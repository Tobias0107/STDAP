"""
    The tests for the main class, and its simulation methods
"""

from package_name.core.main_class import simulator
from package_name.config.settings import get_settings
from package_name.config.functions import Poisson_distribution

csv = "tests/TestDatasets/kwb2024.csv"
geopackage = "tests/TestDatasets/geopackage.gpkg"

settings = get_settings()

settings.dataset_column_names['high_education'] = "a_opl_bvm"
settings.dataset_column_names['medium_education'] = "a_opl_hvm"
settings.dataset_column_names['low_education'] = "a_opl_hw"
settings.dataset_nullstring = ['       .', '.', '']
settings.neighborhood_distribution = lambda a, b, c, d : Poisson_distribution(a, b, c, d, radius=100)


sim = simulator(csv, geopackage, store_in_file=True)
sim.choose_city("Amsterdam")

class TestMainClass:
    def test_Simulate_transit_dist_on_trans(self):
        sim.Simulate_transit_dist_on_trans(0.03, use_amenity=False, svg=False)

