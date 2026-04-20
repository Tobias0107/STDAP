"""
    This file contains all class definitions except for the main class.
    For details, please see the UML or manual.
"""

# Importing packages
import duckdb as db
import osmnx as ox
import os
import pandas as pd
import numpy as np
import geopandas as gpd


# Importing helper functions from utils
from package_name.utils.util_OSMnx import get_graph, get_features

# Importing configuration settings
from package_name.config.settings import get_settings
settings = get_settings()

# Importing exceptions
from package_name.exceptions import Initializing_error


class Network:
    def __init__(self, city: str, store_in_file=False, store_dir='network_cache/') -> None:
        """
            Get OSMnx network of city.
            If store_in_file=True, writes a copy of the original imported network to a store_path.
            If such a copy exists, initialization will use this copy instead of the OSMnx api.
        """
        self.store_in_file = store_in_file
        self.path = f"{store_dir}{city}"
        self.city = city
        self.r5_network = None
        self.osm_pbf_path = None
        self.gtfs_files = None

        if os.path.isfile(f"{self.path}.graphml"):
            self.graph = ox.io.load_graphml(f"{self.path}.graphml")
        else:
            self.graph = get_graph(city)
            if store_in_file:
                ox.io.save_graphml(self.graph, f"{self.path}.graphml")

    def get_nodes_and_edges(self):
        return ox.convert.graph_to_gdfs(self.graph)

    def get_features(self, amenity=True, public_transport=True):
        if os.path.isfile(f"{self.path}.parquet"):
            self.features = gpd.read_parquet(f"{self.path}.parquet")
        else:
            self.features = get_features(self.city, amenity, public_transport)
            if self.store_in_file:
                self.features.to_parquet(f"{self.path}.parquet")
        return self.features

    def remove_edges(self, ebunch):
        "Given a list of tuples (u, v) or (u, v, key). Removes the edges from the network"
        self.graph.remove_edges_from(ebunch)

    def build_r5_network(self, osm_pbf_path: str, gtfs_files: list):
        """
        Builds an r5py TransportNetwork using OSM + GTFS.
        """
        if self.r5_network is not None:
            return  self.r5_network  # al gebouwd

        from r5py import TransportNetwork

        self.osm_pbf_path = osm_pbf_path
        self.gtfs_files = gtfs_files

        self.r5_network = TransportNetwork(osm_pbf_path, gtfs_files)

        return self.r5_network

    def get_r5_network(self):
        if self.r5_network is None:
            raise ValueError("r5 network not initialized. Call build_r5_network() first.")
        return self.r5_network

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
            CREATE TABLE Neighborhoods (
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
                geometry GEOMETRY
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
                oneway BOOLEAN NOT NULL,
                removed BOOLEAN NOT NULL,
                geometry GEOMETRY NOT NULL,
                neighborhood_id VARCHAR,
                PRIMARY KEY (u, v, key)
            );
            CREATE TABLE Neighborhood_pts (
                neighborhood_id VARCHAR,
                pts_id INTEGER DEFAULT NEXTVAL('seq_pts_id'),
                pt GEOMETRY,
                PRIMARY KEY (neighborhood_id, pts_id)
            );
            CREATE TABLE Features (
                element VARCHAR,
                id UBIGINT,
                loc GEOMETRY,
                bus VARCHAR,
                name VARCHAR,
                public_transport VARCHAR,
                amenity VARCHAR,
                railway VARCHAR,
                train VARCHAR,
                brand VARCHAR,
                wheelchair VARCHAR,
                highway VARCHAR,
                PRIMARY KEY (element, id)
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
        self.conn.sql(f"SELECT * FROM Neighborhoods LIMIT {limit}").to_csv("Neighborhoods_database_preview.csv")
        self.conn.sql(f"SELECT * FROM Graph_nodes LIMIT {limit}").to_csv("Graph_nodes_database_preview.csv")
        self.conn.sql(f"SELECT * FROM Graph_edges LIMIT {limit}").to_csv("Graph_edges_database_preview.csv")
        self.conn.sql(f"SELECT * FROM Neighborhood_pts LIMIT {limit}").to_csv("Neighborhood_pts_database_preview.csv")
        self.conn.sql(f"SELECT * FROM Features LIMIT {limit}").to_csv("Features_database_preview.csv")

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

    def load_network(self, network: Network):
        """
        ### Expected:
            - City set (set_city method)
        ### Parameters:
            - Network:\n
                An instance of the Network class containing the network of a single city
        ### Returns:
            - None
        ### Side-effects:
            - (Re)create Graph_nodes Table
            - (Re)create Graph_edges Table
        """
        self.network = network

        # Remove all previous data from tables
        self.conn.sql("DELETE FROM Graph_nodes")
        self.conn.sql("DELETE FROM Graph_edges")

        # Obtain data as GeoDataFrames (GeoPandas)
        nodes_df, edges_df = self.network.get_nodes_and_edges()

        # Make GeoDataFrames importable by duckdb
        nodes = nodes_df.to_arrow()
        edges_df = edges_df.reset_index()
        edges_df["geometry"] = edges_df["geometry"].astype(str) # pyright: ignore[reportArgumentType]
        self.conn.register("edges", edges_df)

        # Import nodes into duckdb (pre-calculate the zone for each node)
        self.conn.sql(f"""
                INSERT INTO Graph_nodes (id, street_count, loc, neighborhood_id)
                SELECT n.osmid, n.street_count, n.geometry, c.id
                FROM nodes n
                JOIN CBS c
                ON ST_Within(n.geometry, c.geom)
                WHERE recs='Buurt' AND gm_naam='{self.city}'
            """)
        # Import edges into duckdb (pre-calculate the zone for each edge)
        self.conn.sql(f"""
                INSERT INTO Graph_edges (u, v, key, length, oneway, removed, geometry, neighborhood_id)
                SELECT u, v, key, length, oneway, false, ST_GeomFromText(geometry), c.id
                FROM edges e
                JOIN Graph_nodes n1
                ON e.u = n1.id
                JOIN Graph_nodes n2
                ON e.v = n2.id
                JOIN CBS c
                ON ST_Within(ST_Point((ST_X(n1.loc) + ST_X(n2.loc)) / 2,
                                      (ST_Y(n1.loc) + ST_Y(n2.loc)) / 2
                             ), c.geom)
                WHERE recs='Buurt' AND gm_naam='{self.city}'
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
        ### Notes:
            - Only tested with amenity and public_transport both True
        """
        # Delete any existing features
        self.conn.sql("DELETE FROM Features")
        if not (amenity and public_transport):
            return

        # Get features GeoDataFrame from OSMnx
        features_gdf = self.network.get_features(amenity, public_transport)

        # Make features importable in duckdb
        features_arrow = features_gdf.to_arrow()
        self.conn.register("features_arrow", features_arrow)

        # Fill Features table using GeoDataFrame
        self.conn.sql("""
                INSERT INTO Features
                SELECT
                    element,
                    id,
                    geometry,
                    bus,
                    name,
                    public_transport,
                    amenity,
                    railway,
                    train,
                    brand,
                    wheelchair,
                    highway
                FROM features_arrow
            """)

    def pre_process(self):
        """
        ### Expected:
            - City set (set_city())
            - Network loaded (load_network())
            - Features loaded (obtain_features) (optional):\n
                features not loaded, will result in NULL values in Neighborhoods::Amenity_density
        ### Parameters:
            - city:\n
                The city to do the pre_processing for.
        ### Returns:
            - None
        ### Side-effects:
            - Replace entries Neighborhoods with entries new city pre-processed from CBS and Amenities
            - Determine neighborhoods for every node in Graph_nodes
        """
        # Remove all entries from neighborhood
        self.conn.sql("DELETE FROM Neighborhoods")

        self.conn.sql(f"""
                INSERT INTO Neighborhoods
                SELECT
                    c.id,
                    c.regio,
                    c.pop / area,
                    coalesce(a.count, 0) / area,
                    c.male / area,
                    c.female / area,
                    c.age_00_14 / area,
                    c.age_15_24 / area,
                    c.age_25_44 / area,
                    c.age_45_64 / area,
                    c.age_65_oo / area,
                    c.background_nl / area,
                    c.background_eu / area,
                    c.background_neu / area,
                    c.birthplace_nl / area,
                    c.birthplace_eu / area,
                    c.birthplace_neu / area,
                    c.low_education / area,
                    c.medium_education / area,
                    c.high_education / area,
                    c.low_income / area,
                    c.high_income / area,
                    c.risk_poverty / area,
                    c.geom
                FROM (SELECT *, ST_Area(geom) as area
                      FROM CBS
                      WHERE gm_naam='{self.city}' AND recs='Buurt') c
                LEFT JOIN (SELECT c2.id, count(*) as count
                           FROM features f
                           JOIN CBS c2
                           ON ST_Within(f.loc, c2.geom)
                           WHERE gm_naam='{self.city}' AND recs='Buurt' AND public_transport IS NULL
                           GROUP BY c2.id ) a
                ON c.id = a.id
            """)

    def create_pts_per_neighborhood(self):
        """
        ### Expected:
            - Pre-processing run
        ### Parameters:
            - None
        ### Returns:
            - None
        ### Side-effects:
            - (Re)create Neighborhood_pts table
        ### Notes'
            - Uses algorithm from configuration to obtain point locations
            - Done in parallel for extra speed
        """
        # Obtain bounding box as dataframe:
        df = self.conn.sql("""
            SELECT id, ST_XMin(geometry) as lower_x, ST_XMax(geometry) as upper_x,
                      ST_YMin(geometry) as lower_y, ST_YMax(geometry) as upper_y
            FROM Neighborhoods
            """).df()

        # For every bounding box, calculate the points
        ids = []
        xs = []
        ys = []
        for row in df.itertuples():
            pts = settings.neighborhood_distribution(row.lower_x, # type: ignore
                                                     row.upper_x, # type: ignore
                                                     row.lower_y, # type: ignore
                                                     row.upper_y) # type: ignore
            if pts.size == 0:
                continue
            ids.extend([row.id] * (int)(pts.size/2))
            xs.extend(pts[:, 0])
            ys.extend(pts[:, 1])

        Neighborhood_pts_df = pd.DataFrame({
            "ids":ids,
            "xs":xs,
            "ys":ys
        })

        # Import dataframe to duckdb
        self.conn.sql("""
            INSERT INTO Neighborhood_pts (neighborhood_id, pt)
            SELECT pt.ids, ST_Point(pt.xs, pt.ys)
            FROM Neighborhood_pts_df pt
            JOIN Neighborhoods n
            ON pt.ids = n.id AND ST_Within(ST_Point(pt.xs, pt.ys), n.geometry)
            """)


    def remove_f_edges(self, fraction: float, use_population=True, use_amenity=False):
        """
        ### Description:
            Will sort the edges based on population or amenity density per meter street.
            Will then remove edges until desired fraction of street-length is reached.
            Meaning successive removals will built upon the previous removals.
        ### Expected:
            - Created points per neighborhood (create_pts_per_neighborhood() run)
        ### Parameters:
            - fraction\n
                The fraction of the total street length to remove from the network.
            - use_population\n
                If True: Removes edges based on population nearby ((pop (* one_way_worth if one way)) / (length * area))
            - use_amenity \n
                If True: Removes edges based on amenity nearby ((amen (* one_way_worth if one way)) / (length * area))
        ### Returns:
            - None
        ### Side_effects;
            - Updates Graph_edges table removed tag (BOOLEAN)
            - Removes edges from graph network
        """
        one_way_worth = settings.one_way_worth
        if not (use_population ^ use_amenity):
            raise ValueError("use_population and use_amenity can't be both true or both false")
        elif use_population:
            density = "n.pop_density"
        else:
            density = "n.amenity_density"

        # Get id of edges to be removed.
        tot_len = "(SELECT sum(length) from Graph_edges)"
        self.conn.sql(f"""
            CREATE OR REPLACE TEMP TABLE edges_to_remove AS
            SELECT *
            FROM (
                SELECT e.*
                FROM Graph_edges e
                JOIN Neighborhoods n
                ON e.neighborhood_id = n.id
                QUALIFY sum(e.length)
                    OVER (ORDER BY (CASE WHEN e.oneway
                                        THEN ({density} / e.length * {one_way_worth})
                                        ELSE ({density} / e.length) END ) DESC )
                    <=  ({fraction} * {tot_len}) ) sub
            WHERE sub.removed = 'false'
        """)
        # Remove edges from network
        to_remove_df = self.conn.sql("SELECT u, v, key FROM edges_to_remove").df()
        ebunch = list(to_remove_df.itertuples(index=False, name=None))
        self.network.remove_edges(ebunch)

        # Update the Graph_edges table with removed edges
        self.conn.sql("""
            UPDATE Graph_edges
            SET removed = 'true'
            FROM edges_to_remove
            WHERE Graph_edges.u = edges_to_remove.u
                      AND Graph_edges.u = edges_to_remove.u
                      AND Graph_edges.key = edges_to_remove.key
        """)

    def move_transit(self):
        pass

    def get_neighborhood_dist_to_nearest_transit(self):
        pass

    def get_colored_network(self):
        pass

