"""
    This file contains the tests for the classes within core/_classes.py

    The tests are written using pytest.

    In practice tests are written for every method where possible.

    Run from The_package as root: pytest --durations=0 -s --verbose
"""

from package_name.core._classes import Database, Network


csv = "tests/TestDatasets/test.csv"
geopackage = "tests/TestDatasets/test.gpkg"

network = Network("Amsterdam", store_in_file=True)
database = Database(csv, geopackage)

class TestDatabase:
    def test_init(self):
        database2 = Database(csv, geopackage)

    def test_get_cities(self):
        assert len(database.get_cities()) == 342

    def test_load_network(self):
        database.load_network(network)

    def test_pre_process(self):
        database.set_city("Amsterdam")
        database.load_network(network)
        database.pre_process()

    def test_obtain_features(self):
        database.set_city("Amsterdam")
        database.load_network(network)
        database.obtain_features()

    def test_create_pts_per_neighborhood(self):
        database.create_pts_per_neighborhood()

    def test_show_database(self):
        database.to_csv(limit=1000000000)


class TestNetwork:
    def test_load_neighborhoods(self):
        pass

    def test_r5_network_initially_none(self):
        net = Network("Amsterdam")
        assert net.r5_network is None

    def test_build_r5_network(self):
        net = Network("Amsterdam")

        net.build_r5_network(osm_pbf_path="tests/TestDatasets/test.osm.pbf",  gtfs_files=["tests/TestDatasets/test_gtfs.zip"])

        assert net.r5_network is not None
        

