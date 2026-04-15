"""
    This file contains all class definitions except for the main class.
    For details, please see the UML or manual.
"""

# Importing packages
import duckdb as db
import osmnx as ox
import networkx as nx
import os

# Importing helper functions from utils
from package_name.utils.util_OSMnx import get_graph, get_features


class Database:
    def __init__(self, csv: str, geopackage: str) -> None:
        """
        ### Expected:
            - None
        ### Parameters:
            - csv:\n
                The path to the csv Kerncijfers Wijken en Buurten (KWB) CBS
            - geopackage:\n
                The path to the geopackage containing the neighborhood borders CBS
        ### Returns:
            - Database object
        ### Side-effects:
            - Creates in-memory duckdb
            - Stores connection to database to self.conn
            - Loads spatial extension to duckdb
            - Creates all tables for database (see design)
            - Uses csv and geopackage to fill CBS table
        """

        # Creating a connection to a new database (in memory)
        self.conn = db.connect()

        # Initializing a spatial database
        self.conn.sql("INSTALL spatial;")
        self.conn.sql("LOAD spatial;")

        # Auto increment initialization
        self.conn.sql("CREATE SEQUENCE seq_pts_id START 1;")

        # Creating all other tables (initialized empty)
        self.conn.sql(f"""
            CREATE TABLE CBS (
                id VARCHAR PRIMARY KEY,
                regio VARCHAR NOT NULL,
                gm_naam VARCHAR NOT NULL,
                recs VARCHAR NOT NULL,
                pop UBIGINT NOT NULL,
                male UBIGINT,
                female UBIGINT,
                age_00_14 UBIGINT,
                age_15_24 UBIGINT,
                age_25_44 UBIGINT,
                age_45_64 UBIGINT,
                age_65_oo UBIGINT,
                background_nl UBIGINT,
                background_eu UBIGINT,
                background_neu UBIGINT,
                birthplace_nl UBIGINT,
                birthplace_eu UBIGINT,
                birthplace_neu UBIGINT,
                low_education UBIGINT,
                medium_education UBIGINT,
                high_education UBIGINT,
                low_income UBIGINT,
                high_income UBIGINT,
                risk_poverty UBIGINT,
                geom GEOMETRY
            );
            CREATE TABLE Neighborhood (
                id VARCHAR PRIMARY KEY,
                regio VARCHAR,
                pop_density FLOAT,
                amenity_density FLOAT,
                male_density FLOAT,
                female_density FLOAT,
                age_density_00_14 FLOAT,
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
            CREATE TABLE Graph_nodes (
                id BIGINT PRIMARY KEY,
                street_count INTEGER,
                loc GEOMETRY,
                neighborhood_id VARCHAR
            );
            CREATE TABLE Graph_edges (
                u BIGINT,
                v BIGINT,
                key INTEGER,
                length FLOAT NOT NULL,
                geometry GEOMETRY NOT NULL,
                oneway BOOLEAN,
                PRIMARY KEY (u, v, key)
            );
            CREATE TABLE Neighborhood_pts (
                neighborhood_id VARCHAR,
                pts_id INTEGER DEFAULT NEXTVAL('seq_pts_id'),
                pt GEOMETRY,
                PRIMARY KEY (neighborhood_id, pts_id)
            );
        """)

        # Joining the two files into one database (Using only buurtcode and geom from geopackage)
        # Only the (possibly) needed fields are imported from the datasets.
        self.conn.sql(f"""
            INSERT INTO CBS
            SELECT
                c.gwb_code,
                c.regio,
                c.gm_naam,
                c.recs,
                c.a_inw,
                c.a_man,
                c.a_vrouw,
                c.a_00_14,
                c.a_15_24,
                c.a_25_44,
                c.a_45_64,
                c.a_65_oo,
                c.a_nl_all,
                c.a_eur_al,
                c.a_neu_al,
                c.a_geb_nl,
                c.a_geb_eu,
                c.a_geb_ne,
                c.a_opl_lg,
                c.a_opl_md,
                c.a_opl_hg,
                c.p_ink_li,
                c.p_ink_hi,
                c.p_ink_ar,
                g.geom
            FROM read_csv('{csv}', nullstr='.') c
            JOIN (SELECT buurtcode, geom FROM ST_Read('{geopackage}')) g
            ON c.gwb_code = g.buurtcode
            """)

    def to_csv(self, limit=10):
        """ Convert every table in database to a csv with given limit. For debugging purposes only. """
        self.conn.sql(f"SELECT * FROM CBS LIMIT {limit}").to_csv("CBS_database_preview.csv")
        self.conn.sql(f"SELECT * FROM Neighborhood LIMIT {limit}").to_csv("Neighborhood_database_preview.csv")
        self.conn.sql(f"SELECT * FROM Graph_nodes LIMIT {limit}").to_csv("Graph_nodes_database_preview.csv")
        self.conn.sql(f"SELECT * FROM Graph_edges LIMIT {limit}").to_csv("Graph_edges_database_preview.csv")
        self.conn.sql(f"SELECT * FROM Neighborhood_pts LIMIT {limit}").to_csv("Neighborhood_pts_database_preview.csv")

    def get_cities(self):
        """
        ### Expected:
            - None
        ### Parameters:
            - None
        ### Returns:
            - List of cities (local autoritjes) in the CBS datasets 
        ### Side-effects:
            - None
        """
        query = """
            SELECT DISTINCT gm_naam
            FROM CBS
            """
        res = self.conn.sql(query).fetchnumpy()
        return res["gm_naam"].tolist()
    
    def set_city(self, city: str):
        """
        ### Expected:
            - None
        ### Parameters:
            - city:\n
                The city to perform the simulation on
        ### Returns:
            - None 
        ### Side-effects:
            - Remembers city (needed for later methods)
        """
        self.city = city
    
    def load_network(self, OSMnx_graph: nx.MultiDiGraph):
        """
        ### Expected:
            - None
        ### Parameters:
            - OSMnx_graph:\n
                An OSMnx Multigraph containing the network of a single city
        ### Returns:
            - None
        ### Side-effects:
            - (Re)create Graph_nodes Table
            - (Re)create Graph_edges Table
        """
        # Remove all previous data from tables
        self.conn.sql("DELETE FROM Graph_nodes")
        self.conn.sql("DELETE FROM Graph_edges")

        # Obtain data as GeoDataFrames (GeoPandas)
        nodes_df, edges_df = ox.convert.graph_to_gdfs(OSMnx_graph)
        
        # Make GeoDataFrames importable by duckdb
        nodes = nodes_df.to_arrow()
        edges_df = edges_df.reset_index()
        edges_df["geometry"] = edges_df["geometry"].astype(str) # pyright: ignore[reportArgumentType]
        self.conn.register("edges", edges_df)

        # Import GeoDataFrames into duckdb
        self.conn.sql("""
                INSERT INTO Graph_nodes (id, street_count, loc)
                SELECT osmid, street_count, geometry
                FROM nodes
            """)
        self.conn.sql("""
                INSERT INTO Graph_edges (u, v, key, length, geometry, oneway)
                SELECT u, v, key, length, ST_GeomFromText(geometry), oneway
                FROM edges
            """)
        
    def obtain_features(self, amenity=True, public_transport=True):
        """
        ### Expected:
            - City set (set_city())
            - Network loaded (load_network())
        ### Parameters:
            - aminity:\n
                If True: obtains all amenities
            - public_transport:\n
                If True: obtains all public transport
        ### Returns:
            - None
        ### Side-effects:
            - (Re)create features Table with obtained features
        """
        features_gdf = get_features(self.city, amenity, public_transport)
        features = features_gdf.to_arrow()
        


    
    def pre_process(self):
        """
        ### Expected:
            - City set (set_city())
            - Network loaded (load_network())
        ### Parameters:
            - city:\n
                The city to do the pre_processing for.
        ### Returns:
            - None
        ### Side-effects:
            - Replace entries Neighborhood with entries new city pre-processed from CBS and Amenities
            - Determine neighborhood for every node in Graph_nodes
        """
        # Remove all entries from neighborhood
        self.conn.sql("DELETE FROM Neighborhood")
        
        # Obtain total street length 
        tot_street_length = "SELECT sum(length) as tot_street FROM Graph_edges"

        # Obtain amenity density

        # Get density values (based on area)
        # CBS (ST_Area(geom))

        self.conn.sql(f"""
                INSERT INTO Neighborhood
                SELECT 
                    id,
                    regio,
                    pop / area,
                    NULL,
                    male / area,
                    female / area,
                    age_00_14 / area,
                    age_15_24 / area,
                    age_25_44 / area,
                    age_45_64 / area,
                    age_65_oo / area,
                    background_nl / area,
                    background_eu / area,
                    background_neu / area,
                    birthplace_nl / area,
                    birthplace_eu / area,
                    birthplace_neu / area,
                    low_education / area,
                    medium_education / area,
                    high_education / area,
                    low_income / area,
                    high_income / area,
                    risk_poverty / area,
                FROM (SELECT *, ST_Area(geom) as area
                      FROM CBS
                      WHERE gm_naam='{self.city}' AND recs='Buurt')
            """)

        # Per node, determine the neighborhood
        zones = f"(SELECT id, geom FROM CBS WHERE recs='Buurt' AND gm_naam='{self.city}')"
        self.conn.sql(f"""
                UPDATE Graph_nodes g
                SET neighborhood_id = z.id
                FROM {zones} z
                WHERE ST_Within(g.loc, z.geom)
            """)


class Network:
    def __init__(self, city: str, store_in_file=False, store_path='network_cache/') -> None:
        """
            Get OSMnx network of city.
            If store_in_file=True, writes a copy of the original imported network to a store_path.
            If such a copy exists, initialization will use this copy instead of the OSMnx api.
        """
        if os.path.isfile(f"{store_path}{city}.graphml"):
            self.graph = ox.io.load_graphml(f"{store_path}{city}.graphml")
        else:
            self.graph = get_graph(city)
            if store_in_file:
                ox.io.save_graphml(self.graph, f"{store_path}{city}.graphml")

