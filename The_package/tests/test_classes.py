"""
    This file contains the tests for the Database class methods.
    It only checks the runtime and exceptions of every method.
    Tests are run using the 2024 dataset (download manually).

    The tests are written using pytest.
    Run from The_package as root: pytest --durations=0 -s --verbose
"""

from package_name.core._classes import Database, Network
from package_name.config.settings import get_settings

# Dataset
csv = "tests/TestDatasets/kwb2024.csv"
geopackage = "tests/TestDatasets/geopackage.gpkg"

# Edit configuration to match the configuration of the paper
settings = get_settings()
settings.dataset_column_names['high_education'] = "a_opl_bvm"
settings.dataset_column_names['medium_education'] = "a_opl_hvm"
settings.dataset_column_names['low_education'] = "a_opl_hw"
settings.dataset_nullstring = ['       .', '.', '']

network = Network("Amsterdam", store_in_file=True)
database = Database(csv, geopackage)

class TestDatabase:
    def test_init(self):
        database2 = Database(csv, geopackage)

    def test_get_cities(self):
        database.get_cities()

    def test_load_network(self):
        database.set_city("Amsterdam")
        database.load_network(network)

    def test_obtain_features(self):
        database.obtain_features()

    def test_pre_process(self):
        database.pre_process()

    def test_create_pts_per_neighborhood(self):
        database.create_pts_per_neighborhood()

    def test_remove_f_edges(self):
        database.remove_f_edges(0.2, use_population=False, use_amenity=True)

    def test_move_transit_simple(self):
        database.link_busses()
        database.move_transit_minimal()

    def test_move_transit_blank_slate(self):
        database.move_transit_blank_slate()

    def test_get_neighborhood_dist_to_nearest_transit(self):
        database.calculate_distances_to_nearest_transit()

    def test_get_dist_per_neighborhood(self):
        database.get_dist_per_neighborhood()

    def test_get_demographic_average_increase(self):
        database.get_demographic_average_distance()

