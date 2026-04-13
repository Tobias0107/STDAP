"""
    This file contains all class definitions except for the main class.
    For details, please see the UML or manual.
"""

# Importing packages
import duckdb as db
import osmnx as ox
import pandas as pd
import geopandas as gpd
from shapely import wkb


# Importing helper functions from utils
from package_name.utils.util_OSMnx import get_graph


class Neighborhood:
    # All information that should be stored
    def __init__(self) -> None:
        pass


class CBS:
    def __init__(self, csv: str, geopackage: str) -> None:
        """ Initialise database by merging csv and geopackage """

        # Initializing a spatial database
        db.sql("INSTALL spatial;")
        db.sql("LOAD spatial;")
        # Joining the two files into one database
        query = f"""
            CREATE TABLE database AS
            SELECT *
            FROM read_csv('{csv}') c
            JOIN (SELECT buurtcode, geom FROM ST_Read('{geopackage}')) g
            ON c.gwb_code = g.buurtcode
            """
        db.sql(query)

    def to_csv(self, path: str, limit=10):
        db.sql(f"SELECT * FROM database LIMIT {limit}").to_csv(path)

    def get_cities(self):
        """ Get all "gemeente_naam" from database """
        query = """
            SELECT DISTINCT gm_naam
            FROM database
            GROUP BY gm_naam
            """
        res = db.sql(query).fetchnumpy()
        return res["gm_naam"].tolist()
    
    def get_neighborhood_borders(self, city):
        """
            Get normal pandas dataframe containing the geometry in the form of
            a bytearray (WKB).
        """
        query = f"""
            SELECT regio, ST_AsWKB(geom) as geometry
            FROM database
            WHERE gm_naam = '{city}' AND recs = 'Buurt'
            """
        df = db.sql(query).df()
        return df

class Network:
    def __init__(self, city: str) -> None:
        """
            Get OSMnx network of city
        """
        self.graph = get_graph(city)
        self.gdf_nodes, self.gdf_edges = ox.graph_to_gdfs(self.graph)
        self.known_neighborhoods: dict[int, Neighborhood] = dict()

    def load_neighborhoods(self, geodata: gpd.GeoDataFrame):
        print(self.gdf_nodes)
        print()
        print(geodata)

