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
        metadata={"description": "The worth of a one way street, as compared to"
                  "two way streets. The parameter is used for simulations that remove"
                  "streets from driving networks."}
    )


_settings = Settings()


def get_settings() -> Settings:
    return _settings


def reset_settings():
    global _settings
    _settings = Settings()


 

