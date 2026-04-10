"""
    This file contains the tests for the classes within core/_classes.py

    The tests are written using pytest.

    In practice tests are written for every method where possible.
"""

import pytest
from package_name.core._classes import Neighborhood, CBS, Network


class TestNeighborhood:
    pass

class TestCBS:
    csv = "tests/TestDatasets/test.csv"
    geopackage = "tests/TestDatasets/test.gpkg"
    
    def test_get_cities(self):
        cbs = CBS(self.csv, self.geopackage)
        cities = cbs.get_cities()
        assert len(cities) == 342


class TestNetwork:
    pass

