"""
    This file contains the tests for the classes within core/_classes.py

    The tests are written using pytest.

    In practice tests are written for every method where possible.
"""

import pytest
from package_name.core._classes import Neighborhood, CBS, Network


csv = "tests/TestDatasets/test.csv"
geopackage = "tests/TestDatasets/test.gpkg"

network = Network("Amsterdam")
cbs = CBS(csv, geopackage)

class TestNeighborhood:
    pass

class TestCBS:
    def test_init(self):
        cbs.to_csv("preview_database.csv")

    def test_get_cities(self):
        cities = cbs.get_cities()
        assert len(cities) == 342

    def test_get_neighborhood_borders(self):
        borders = cbs.get_neighborhood_borders('Amsterdam')
        borders.to_csv("test_borders.csv")


class TestNetwork:
    def test_load_neighborhoods(self):
        network.load_neighborhoods(cbs.get_neighborhood_borders("Amsterdam"))
        assert True

