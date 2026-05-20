"""
    This file contains the full configuration options for the python package.

    Settings can be obtained and modified with the following method:
        settings = from package_name.config.settings import get_settings
        settings = get_settings()
        settings.example = 5
"""


from dataclasses import dataclass, field, fields
from typing import Callable
import numpy as np
import pandas as pd
import matplotlib.colors as mcolor


import package_name.config.functions as functions

@dataclass
class Settings:
    ###########################################################################
    ##################### Data importation settings ###########################
    ###########################################################################

    dataset_column_names: dict[str, str] = field (
        default_factory = lambda: {
            "id": "gwb_code",
            "regio": "regio",
            "gm_naam": "gm_naam",
            "recs": "recs",
            "pop": "a_inw",
            "male": "a_man",
            "female": "a_vrouw",
            "age_00_14": "a_00_14",
            "age_15_24": "a_15_24",
            "age_25_44": "a_25_44",
            "age_45_64": "a_45_64",
            "age_65_oo": "a_65_oo",
            "background_nl": "a_nl_all",
            "background_eu": "a_eur_al",
            "background_neu": "a_neu_al",
            "birthplace_nl": "a_geb_nl",
            "birthplace_eu": "a_geb_eu",
            "birthplace_neu": "a_geb_ne",
            "low_education": "a_opl_lg",
            "medium_education": "a_opl_md",
            "high_education": "a_opl_hg",
            "low_income": "p_ink_li",
            "high_income": "p_ink_hi",
            "risk_poverty": "p_ink_ar",
            "buurtcode": "buurtcode",
            "geom": "geom"
        },
        metadata={"description": "Datasets of different years might have different "
                  "column names. Therefore this dictionary allows one to change "
                  "the column names of the dataset that are read by the package. "
                  "The keys of the dictionary are the internal names of the data "
                  "used for the simulation. The values are the names of the corresponding "
                  "columns in the datasets (csv / geopackage). Non-existent columns "
                  "will result in an error. Empty columns will not result in an error. "
                  "The geom and buurtcode come from the geopackage. All other columns "
                  "come from the csv."}
    )
    dataset_nullstring: list[str] = field (
        default_factory= lambda: ['       .', '.', ''],
        metadata={"description": "The character used for the NULL values in the csv files. "
                  "Parameter to allow compatibility for datasets of different years."}
    )
    dataset_delim: str = field (
        default=',',
        metadata={"description": "The character used for the delimiter in the csv files. "
                  "Parameter to allow compatibility for datasets of different years."}
    )
    dataset_decimal_separator: str = field (
        default=',',
        metadata={"description": "The separating character when reading floats from csv files."}
    )

    ###########################################################################
    ##################### Simulation settings #################################
    ###########################################################################

    neighborhood_distribution: Callable[[float, float, float, float], np.typing.NDArray[np.float64]] = field(
        default=functions.Poisson_distribution,
        metadata= {"description": "Given the upper and lower bounds of the "\
                    "bounding box of the neighborhood. Generate a list of "\
                    "coordinates of points representing the neighborhood. "\
                    "Default uses scipy PoissonDisk distribution. "\
                    "Import default with 'import package_name.config.functions.Poisson_distribution' "\
                    "This function should return a numpy NDarray consisting of a list of points. "\
                    "Points are lists of 2 elements in the form [x, y]"}
    )
    transit_max_edge_dist: int = field(
        default=30,
        metadata={"description": "This field determined the maximum distance in meters "\
                  "between a transit node, and the nearest edge."}
    )
    transit_max_pts_dist: int = field(
        default=30,
        metadata={"description": "This field determines the maximum distance in meters "\
                  "between a point in a neighborhood, and the nearest node in the pedestrian network."}
    )
    transit_max_move_dist: int = field(
        default=200,
        metadata={"description": "The maximum distance in meters between the previous "\
                  "transit location, and the new moved transit location."}
    )
    max_dist_ped_transit: int = field(
        default=30,
        metadata={"description": "The maximum distance in meters between a transit station "\
                  "and the pedestrian network. This is needed as nodes between the networks do "\
                  "not nessisarily overlap. This constant acts as a buffer allowing the networks "\
                  "to be merged, and obtain the nodes in the driving network accessible by the "\
                  "pedestrian network."}
    )
    min_distance_stops: int = field(
        default=300,
        metadata={"description": "The minimal distance in meter between transit stops."\
                  "Only used for the blank slate transit stop relocation."}
    )
    max_distance_stops: int = field(
        default=800,
        metadata={"description": "The maximum distance in meter between transit stops."\
                  "Only used for the blank slate transit stop relocation."}
    )
    max_stops_in_bus_route: int = field(
        default=20,
        metadata={"description": "The maximum number of stops in a single bus route."
                  "Only used for the blank slate transit stop relocation."}
    )
    min_stops_in_bus_route: int = field(
        default=9,
        metadata={"description": "The maximum number of stops in a single bus route."
                  "Only used for the blank slate transit stop relocation."}
    )
    amenity_to_pop_weight: int = field(
        default=20,
        metadata={"description": "Used for the scoring formula used by the blank-slate method"
                  "Score = pop_size + amenity_to_pop_weight * num_amenities"}
    )

    ###########################################################################
    ##################### Visualization settings ##############################
    ###########################################################################

    png_dpi: int = field(
        default=500,
        metadata={"description": "The dpi used when generating visualizations using the 'png' format."}
    )
    colormap: str = field(
        default='RdBu_r',
        metadata={"description": "viridis_r, The colormap used to color the networks based on distance. "
                  "Should be a valid matplotlib colormap"}
    )
    color_normalization: Callable[..., mcolor.Normalize] = field(
        default=lambda vmin, vmax: mcolor.SymLogNorm(linthresh=1, vmin=vmin, vmax=vmax),
        metadata={"description": "The normalization used to assign colors to values in the colored network. "
                  "It should be a valid matplotlib normalization. The default function is "
                  "matplotlib.mcolor.SymLogNorm() with a linthresh of 1. The function should"
                  "take a vmin and vmax argument."}
    )
    legend_num_labels: int = field(
        default=10,
        metadata={"description": "The number of numbers to show on the colorbar legend when "\
                  "plotting the colored network."}
    )


    ###########################################################################
    ##################### Class methods #######################################
    ###########################################################################

    def describe(self):
        """
            Returns string representation of settings, including per field descriptions.
        """
        lines = ''
        for f in fields(self):
            name = f.name
            value = getattr(self, name)
            description = f.metadata.get("description", "")
            default = f.default

            lines += f"{name} = {value} (default: {default})\nDescription: {description}\n\n"

        return lines

    def to_df(self) -> pd.DataFrame:
        rows = []
        for f in fields(self):
            rows.append({
                "name": f.name,
                "value": getattr(self, f.name),
                "default": f.default,
                "description": f.metadata.get("description", "")
            })
        return pd.DataFrame(rows)


_settings = Settings()


def get_settings() -> Settings:
    return _settings


def reset_settings():
    global _settings
    _settings = Settings()
