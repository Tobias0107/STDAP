"""
    This file contains all class definitions except for the main class.
    For details, please see the UML or manual.
"""

# Importing packages
import duckdb as db
import networkx as nx
import osmnx as ox
import pandas as pd
import numpy as np


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
            FROM read_csv('{csv}') c JOIN ST_Read('{geopackage}') g ON c.gwb_code = g.buurtcode
            """
        # Store the result in the database variable
        self.database = db.sql(query)

    def get_cities(self):
        """ Get all "gemeente_naam" from database """
        query = """
            SELECT DISTINCT gm_naam
            FROM database
            GROUP BY gm_naam
            """
        res = db.sql(query).fetchnumpy()
        return res["gm_naam"].tolist()
    
    


class Network:
    def __init__(self, city) -> None:
        pass
