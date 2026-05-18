"""
    This file contains the full simulation performed for the paper:
    Modeling Pedestrianization in Dutch Urban Street Networks: Impacts on Transit
    Accessibility for different Demographic Groups
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


class TestMultipleFractions:
    def test_main(self):
        sim = simulator(csv, geopackage, store_in_file=True)
        for city in sim.get_cities():
            sim.choose_city(str(city))


