"""
    Here the test for the utils.
    Some tests are commented out to save time when testing. 
"""

import pytest
from package_name.utils.util_OSMnx import get_graph, get_features

class TestUtilsOSMnx:
    def test_get_graph(self):
        # G = get_graph("Groningen")
        pass

    def test_get_features(self):
        gdf = get_features("Groningen")
        gdf.to_csv("tmp.csv")


