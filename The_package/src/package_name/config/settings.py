"""
    This file contains the full configuration options for the python package.

    Settings can be obtained and modified with the following method:
        settings = from package_name.config.settings import get_settings
        settings = get_settings()
        settings.example = 5
"""


from dataclasses import dataclass, field
from typing import Callable
import numpy as np


import package_name.config.functions as functions

@dataclass
class Settings:
    example: int = field(
        default=0,
        metadata={"description": "Here the description"}
    )
    neighborhood_distribution: Callable[[float, float, float, float], np.typing.NDArray[np.float64]] = field(
        default=functions.Poisson_distribution,
        metadata= {"description": "Given the upper and lower bounds of the "\
                    "bounding box of the neighborhood. Generate a list of "\
                    "coordinates of points representing the neighborhood."\
                    "Default uses scipy PoissonDisk distribution."\
                    "Import default with 'import package_name.config.functions.Poisson_distribution'"\
                    "This function should return a numpy NDarray consisting of a list of points."\
                    "Points are lists of 2 elements in the form [x, y]"}
    )
    one_way_worth: float = field(
        default=0.7,
        metadata={"description": "The worth of a one way street, as compared to"\
                  "two way streets. The parameter is used for simulations that remove"\
                  "streets from driving networks. Setting this to zero would fully prioritize"\
                  "removing 2-way streets before 1-way streets"}
    )
    transit_min_edges: int = field(
        default=2,
        metadata={"description": "This field determines when the simulation treats"\
                  "an bus/tram station as isolated. When the node of the transit station"\
                  "contains strictly less then transit_min_edges, it is treated as isolated."}
    )
    transit_max_edge_dist: int = field(
        default=30,
        metadata={"description": "This field determined the maximum distance in meters"\
                  "between a transit node, and the nearest edge."}
    )


_settings = Settings()


def get_settings() -> Settings:
    return _settings


def reset_settings():
    global _settings
    _settings = Settings()


 

