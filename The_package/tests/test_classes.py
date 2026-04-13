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
database.to_csv()

class TestDatabase:
    def test_init(self):
        pass

    def test_get_cities(self):
        pass

    def test_get_neighborhood_borders(self):
        pass

    def test_load_network(self):
        database.load_network(network.graph)


class TestNetwork:
    def test_load_neighborhoods(self):
        pass

