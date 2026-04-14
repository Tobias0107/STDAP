"""
    This file contains the tests for the classes within core/_classes.py

    The tests are written using pytest.

    In practice tests are written for every method where possible.
"""

import pytest
from package_name.core._classes import Database, Network


csv = "tests/TestDatasets/test.csv"
geopackage = "tests/TestDatasets/test.gpkg"

network = Network("Amsterdam")
database = Database(csv, geopackage)

class TestDatabase:
    def test_init(self):
        database2 = Database(csv, geopackage)

    def test_get_cities(self):
        assert len(database.get_cities()) == 342

    def test_load_network(self):
        database.load_network(network.graph)

    def test_pre_process(self):
        # database.load_network(network.graph)
        database.pre_process("Amsterdam")
        database.to_csv()


class TestNetwork:
    def test_load_neighborhoods(self):
        pass

