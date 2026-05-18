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
settings.neighborhood_distribution = lambda a, b, c, d : Poisson_distribution(a, b, c, d, radius=30)


sim = simulator(csv, geopackage, store_in_file=True)
sim.choose_city("Amsterdam")

class TestMainClass:
    def test_Sim_trans_dist_single(self):
        return
        sim.Sim_trans_dist_single(0.3, svg=False, blank_slate=False, minimal_move=True)

    def test_sim_trans_sist_multiple(self):
        sim.Sim_trans_dist_multiple(0, 0.5, 100, svg=False, blank_slate=True, minimal_move=False)
