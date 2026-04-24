"""
    The tests for the main class, and its simulation methods
"""

from package_name.core.main_class import simulator

csv = "tests/TestDatasets/kwb2025.csv"
geopackage = "tests/TestDatasets/geopackage.gpkg"

sim = simulator(csv, geopackage, store_in_file=True)
sim.choose_city("Amsterdam")

class TestMainClass:
    def test_Simulate_transit_dist_on_trans(self):
        sim.Simulate_transit_dist_on_trans(0.3)

