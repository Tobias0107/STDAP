"""
    Tests the main class for exceptions and runtime.
"""

from STDAP.core.main_class import simulator
from STDAP.config.settings import get_settings

csv = "tests/TestDatasets/kwb2024.csv"
geopackage = "tests/TestDatasets/geopackage.gpkg"

settings = get_settings()

settings.dataset_column_names['high_education'] = "a_opl_bvm"
settings.dataset_column_names['medium_education'] = "a_opl_hvm"
settings.dataset_column_names['low_education'] = "a_opl_hw"
settings.dataset_nullstring = ['       .', '.', '']


class TestMainClass:
    def test_Sim_trans_dist_single(self):
        sim = simulator(csv, geopackage, store_in_file=True)
        sim.choose_city("Amsterdam")
        sim.Sim_trans_dist_single(0.25, svg=False, blank_slate=True, minimal_move=False, saving_dir="results_test/blank-slate/percentages/25%/")

    def test_sim_trans_sist_multiple(self):
        sim = simulator(csv, geopackage, store_in_file=True)
        sim.choose_city("Amsterdam")
        sim.Sim_trans_dist_multiple(0, 0.5, 100, svg=False, blank_slate=False, minimal_move=True, saving_dir="results_test/minimal/range/")
