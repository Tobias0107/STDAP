"""
    This file contains all class definitions except for the main class.
    For details, please see the UML or manual.
"""

# Importing packages
import duckdb as db
import osmnx as ox
import networkx as nx
import pandas as pd
import geopandas as gpd
from shapely import wkb


# Importing helper functions from utils
from package_name.utils.util_OSMnx import get_graph


class Database:
    def __init__(self, csv: str, geopackage: str) -> None:
        """ Initialise database by merging csv and geopackage """

        # Creating a connection to a new database (in memory)
        self.conn = db.connect()

        # Initializing a spatial database
        self.conn.sql("INSTALL spatial;")
        self.conn.sql("LOAD spatial;")
        # self.conn.sql("CALL register_geoarrow_extensions()")

        # Joining the two files into one database (Using only buurtcode and geom from geopackage)
        query = f"""
            CREATE TABLE CBS AS
            SELECT *
            FROM read_csv('{csv}') c
            JOIN (SELECT buurtcode, geom FROM ST_Read('{geopackage}')) g
            ON c.gwb_code = g.buurtcode
            """
        self.conn.sql(query)

    def to_csv(self, limit=10):
        """ Convert every table in database to a csv with given limit. For debugging purposes only. """
        self.conn.sql(f"SELECT * FROM CBS LIMIT {limit}").to_csv("CBS_database_preview.csv")
        # self.conn.sql(f"SELECT * FROM Neighborhood LIMIT {limit}").to_csv("Neighborhood_database_preview.csv")
        self.conn.sql(f"SELECT * FROM Graph LIMIT {limit}").to_csv("Graph_database_preview.csv")
        # self.conn.sql(f"SELECT * FROM Neighborhood_pts LIMIT {limit}").to_csv("Neighborhood_pts_database_preview.csv")

    def get_cities(self):
        """ Get all "gemeente_naam" from database. Returns list of cities. """
        query = """
            SELECT DISTINCT gm_naam
            FROM CBS
            """
        res = self.conn.sql(query).fetchnumpy()
        return res["gm_naam"].tolist()
    
    def load_network(self, OSMnx_graph: nx.MultiDiGraph):
        """
            Load the nodes of a OSMnx graph into the database for later data analysis.
            This operation creates the Graph table (see outer_design).
            The columns in the nodes explained:
            This operation also removes any existing graphs from the database
        """
        self.conn.sql("DROP TABLE IF EXISTS Graph")

        nodes = ox.convert.graph_to_gdfs(OSMnx_graph, edges=False, fill_edge_geometry=False)
        nodes_arrow = nodes.to_arrow()

        self.conn.sql("""
               CREATE TABLE Graph (
                    id BIGINT PRIMARY KEY,
                    street_count INTEGER,
                    point GEOMETRY,
                    neighborhood_id VARCHAR
                );         
            """)

        self.conn.sql( """
                INSERT INTO Graph (id, street_count, point)
                SELECT osmid, street_count, geometry
                FROM nodes_arrow
            """ )

    def pre_process(self, city:str):
        """
            Starts the pre-processing progress.
            Should be called before running the simulations and after choosing the city (performance)
            Turns CBS into Neighborhood table for specific city.
            Finds and creates neighborhood points representing each neighborhood (Neighborhood_pts table)
            See outer design.

            Deletes Neighborhood table if exists
        """
        # Create new Neighborhood table for city
        self.conn.sql(f"""
            DROP TABLE IF EXISTS Neighborhood
        """)
        self.conn.sql(f"""
            CREATE TABLE Neighborhood (
                id BIGINT PRIMARY KEY,
                tot_padestrian_street BIGINT,
                tot_car_street BIGINT,
                pop_density FLOAT,
                amenity_density FLOAT,
                male_density FLOAT,
                female_density FLOAT,
                age_density_15_24 FLOAT,
                age_density_25_44 FLOAT,
                age_density_45_64 FLOAT,
                age_density_65_oo FLOAT,
                background_density_nl FLOAT,
                background_density_eu FLOAT,
                background_density_neu FLOAT,
                birthplace_density_nl FLOAT,
                birthplace_density_eu FLOAT,
                birthplace_density_neu FLOAT,
                low_education_density FLOAT,
                medium_education_density FLOAT,
                high_education_density FLOAT,
                low_income_density FLOAT,
                high_income_density FLOAT,
                risk_poverty_density FLOAT,
            );
        """)
        # Obtain total street length
        

        # Get density values (based on area)
        self.conn.query("""
            INSERT INTO Neighborhood (*)
            VALUES (
                        )
        """)
        


        # Per node, determine the neighborhood
        zones = f"(SELECT gwb_code, geom FROM CBS WHERE recs='Buurt' AND gm_naam='{city}')"
        self.conn.sql(f"""
                UPDATE Graph g
                SET neighborhood_id = z.gwb_code
                FROM {zones} z
                WHERE ST_Within(g.point, z.geom)
            """)

        # Per zone, determine the pop_density, amenity_density, number of transit
        # Use this to create the Neighborhood table


class Network:
    def __init__(self, city: str) -> None:
        """
            Get OSMnx network of city
        """
        self.graph = get_graph(city)
