"""
    This file contains all class definitions except for the main class.
    For details, please see the UML or manual.

    TODO: Informatieverlies printen. By test:
        - 4 door geen punten binnen neighborhood (radius=30)
        - Rest door geen voetpad in buurt van punten.
"""

# Importing packages
import duckdb as db
import osmnx as ox
import networkx as nx
import os
import pandas as pd
import numpy as np
import geopandas as gpd
import pyarrow as pa
import heapq
from shapely import wkb
from collections import defaultdict
import random


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

        if os.path.isfile(f"{self.path}_drive.graphml"):
            self.graph_drive = ox.io.load_graphml(f"{self.path}_drive.graphml")
        else:
            self.graph_drive = get_graph(city)
            if store_in_file:
                ox.io.save_graphml(self.graph_drive, f"{self.path}_drive.graphml")

        if os.path.isfile(f"{self.path}_ped.graphml"):
            self.graph_pedestrian = ox.io.load_graphml(f"{self.path}_ped.graphml")
        else:
            self.graph_pedestrian = get_graph(city, network_type="walk")
            self.graph_pedestrian.add_nodes_from(self.graph_drive.nodes(data=True))
            if store_in_file:
                ox.io.save_graphml(self.graph_pedestrian, f"{self.path}_ped.graphml")

    def get_drive_network_df(self):
        "Returns tuple (nodes, edges) of driving network converted to pandas dataframe"
        return ox.convert.graph_to_gdfs(self.graph_drive)

    def get_pedestrian_nodes_df(self):
        "Returns tuple (nodes, edges) of pedestrian network converted to pandas dataframe"
        return ox.convert.graph_to_gdfs(self.graph_pedestrian, fill_edge_geometry=True)

    def get_distances_to_transit(self, ped_transit_nodes):
        """
            Calculates the distance from the sources, that is the transit stops
            (nodes on pedestrian network), to all other nodes in the network.
            Returns: A dictionary {node_id:dist_to_closest_transit}
        """
        # Get undirected graph (as pedestrian network is undirected)
        G = self.graph_pedestrian.to_undirected(reciprocal=False)
        # Calculate the distances from ped_transit_nodes to all other nodes in ped_network
        return nx.multi_source_dijkstra_path_length(G, ped_transit_nodes, weight="length")

    def get_features(self, amenity=True, public_transport=True):
        """ Import features via api or file, and then return features as GeoDataFrame """
        if os.path.isfile(f"{self.path}.parquet"):
            self.features = gpd.read_parquet(f"{self.path}.parquet")
        else:
            self.features = get_features(self.city, amenity, public_transport)
            if self.store_in_file:
                self.features.to_parquet(f"{self.path}.parquet")
        return self.features

    def transform_edges(self, ebunch):
        """
            Given a list of tuples (u, v, key).
            Removes the edges from the driving network
            and adds them to the pedestrian network
        """
        # For every edge, obtain the data
        edges_to_add = []
        for (u, v, k) in ebunch:
            data = self.graph_drive.get_edge_data(u, v, k)
            edges_to_add.append((u, v, data))

        # Transform edges
        self.graph_drive.remove_edges_from(ebunch)
        self.graph_pedestrian.add_edges_from(edges_to_add)

    def add_edges_to_ped_network(self, ebunch):
        """
            Given a list of tuples (u, v).
            and adds them to the pedestrian network
        """
        self.graph_pedestrian.add_edges_from(ebunch)

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
        # Keeping track of neighborhoods that are dropped during point generation
        self.num_buurten = 0
        self.lost = 0

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
                low_income FLOAT,
                high_income FLOAT,
                risk_poverty FLOAT,
                geom GEOMETRY
            );
            CREATE TABLE Neighborhoods (
                id VARCHAR PRIMARY KEY,
                regio VARCHAR,
                population UBIGINT,
                amenities UBIGINT,
                area UBIGINT,
                num_male UBIGINT,
                num_female UBIGINT,
                num_age_00_14 UBIGINT,
                num_age_15_24 UBIGINT,
                num_age_25_44 UBIGINT,
                num_age_45_64 UBIGINT,
                num_age_65_oo UBIGINT,
                num_background_nl UBIGINT,
                num_background_eu UBIGINT,
                num_background_neu UBIGINT,
                num_birthplace_nl UBIGINT,
                num_birthplace_eu UBIGINT,
                num_birthplace_neu UBIGINT,
                num_low_education UBIGINT,
                num_medium_education UBIGINT,
                num_high_education UBIGINT,
                percent_low_income FLOAT,
                percent_high_income FLOAT,
                percent_risk_poverty FLOAT,
                geometry GEOMETRY
            );
            CREATE TABLE Graph_nodes (
                id UBIGINT PRIMARY KEY,
                street_count INTEGER,
                loc GEOMETRY,
                neighborhood_id VARCHAR
            );
            CREATE TABLE Graph_edges (
                u UBIGINT,
                v UBIGINT,
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
                node_id UBIGINT,
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

        column_names = settings.dataset_column_names

        # Joining the two files into one database (Using only buurtcode and geom from geopackage)
        # Only the (possibly) needed fields are imported from the datasets.
        self.conn.sql(f"""
            INSERT INTO CBS
            SELECT
                c.{column_names["id"]},
                c.{column_names["regio"]},
                c.{column_names["gm_naam"]},
                c.{column_names["recs"]},
                c.{column_names["pop"]},
                c.{column_names["male"]},
                c.{column_names["female"]},
                c.{column_names["age_00_14"]},
                c.{column_names["age_15_24"]},
                c.{column_names["age_25_44"]},
                c.{column_names["age_45_64"]},
                c.{column_names["age_65_oo"]},
                c.{column_names["background_nl"]},
                c.{column_names["background_eu"]},
                c.{column_names["background_neu"]},
                c.{column_names["birthplace_nl"]},
                c.{column_names["birthplace_eu"]},
                c.{column_names["birthplace_neu"]},
                c.{column_names["low_education"]},
                c.{column_names["medium_education"]},
                c.{column_names["high_education"]},
                c.{column_names["low_income"]},
                c.{column_names["high_income"]},
                c.{column_names["risk_poverty"]},
                g.{column_names["geom"]}
            FROM read_csv('{csv}', nullstr={str(settings.dataset_nullstring)}, delim='{settings.dataset_delim}', decimal_separator='{settings.dataset_decimal_separator}') c
            JOIN (SELECT {column_names["buurtcode"]}, geom FROM ST_Read('{geopackage}')) g
            ON c.gwb_code = g.{column_names["buurtcode"]}
            """)

    def to_csv(self, limit=10):
        """ Convert every table currently in database to a csv with given limit. For debugging purposes only. """
        try:
            self.conn.sql(f"SELECT * FROM CBS LIMIT {limit}").to_csv("CBS_database_preview.csv")
        except Exception:
            pass
        try:
            self.conn.sql(f"SELECT * FROM Neighborhoods LIMIT {limit}").to_csv("Neighborhoods_database_preview.csv")
        except Exception:
            pass
        try:
            self.conn.sql(f"SELECT * FROM Graph_nodes LIMIT {limit}").to_csv("Graph_nodes_database_preview.csv")
        except Exception:
            pass
        try:
            self.conn.sql(f"SELECT * FROM Graph_edges LIMIT {limit}").to_csv("Graph_edges_database_preview.csv")
        except Exception:
            pass
        try:
            self.conn.sql(f"SELECT * FROM Neighborhood_pts LIMIT {limit}").to_csv("Neighborhood_pts_database_preview.csv")
        except Exception:
            pass
        try:
            self.conn.sql(f"SELECT * FROM Features LIMIT {limit}").to_csv("Features_database_preview.csv")
        except Exception:
            pass
        try:
            self.conn.sql(f"SELECT * FROM Stations LIMIT {limit}").to_csv("Stations_database_preview.csv")
        except Exception:
            pass
        try:
            self.conn.sql(f"SELECT * FROM Bus_stations_to_move LIMIT {limit}").to_csv("Bus_stations_to_move_database_preview.csv")
        except Exception:
            pass
        try:
            self.conn.sql(f"SELECT * FROM Graph_nodes_accessible LIMIT {limit}").to_csv("Graph_nodes_accessible_database_preview.csv")
        except Exception:
            pass
        try:
            self.conn.sql(f"SELECT * FROM Graph_nodes_ped LIMIT {limit}").to_csv("Graph_nodes_ped_database_preview.csv")
        except Exception:
            pass
        try:
            self.conn.sql(f"SELECT * FROM Distances LIMIT {limit}").to_csv("Distances_database_preview.csv")
        except Exception:
            pass
        try:
            self.conn.sql(f"SELECT * FROM Dist_per_neighborhood LIMIT {limit}").to_csv("Dist_per_neighborhood_database_preview.csv")
        except Exception:
            pass
        try:
            self.conn.sql(f"SELECT * FROM Graph_edges_ped LIMIT {limit}").to_csv("Graph_edges_ped_database_preview.csv")
        except Exception:
            pass
        try:
            self.conn.sql(f"SELECT * FROM Bus_routes LIMIT {limit}").to_csv("Bus_routes_database_preview.csv")
        except Exception:
            pass

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
            - Store network in database
            - (Re)create Graph_nodes Table
            - (Re)create Graph_edges Table
            - (Re)create Graph_nodes_accessible Table
        """
        self.network = network

        # Remove all previous data from tables
        self.conn.sql("DELETE FROM Graph_nodes")
        self.conn.sql("DELETE FROM Graph_edges")

        # Obtain data as GeoDataFrames (GeoPandas)
        nodes_df, edges_df = self.network.get_drive_network_df()

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

        # Get pedestrian nodes
        ped_nodes_df, ped_edges_df = self.network.get_pedestrian_nodes_df()
        ped_nodes = ped_nodes_df.to_arrow()
        ped_edges_df = ped_edges_df.reset_index()
        ped_edges_df["geometry"] = ped_edges_df["geometry"].astype(str) # pyright: ignore[reportArgumentType]
        self.conn.register("ped_edges", ped_edges_df)

        # Create Graph_nodes_ped (storing the nodes of the pedestrian network)
        self.conn.sql(f"""
            CREATE OR REPLACE TABLE Graph_nodes_ped AS
            SELECT n.osmid AS id, n.street_count, n.geometry, c.id AS neighborhood_id
            FROM ped_nodes n
            JOIN CBS c
            ON ST_Within(n.geometry, c.geom)
            WHERE recs='Buurt' AND gm_naam='{self.city}'
        """)

        # Create Graph_edges_ped (storing the nodes of the pedestrian network)
        self.conn.sql(f"""
            CREATE OR REPLACE TABLE Graph_edges_ped AS
            SELECT e.u, e.v, e.key, e.length, false AS removed, ST_GeomFromText(e.geometry) AS geometry, c.id AS neighborhood_id
            FROM ped_edges e
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

        # Create Graph_nodes_accessible (storing drive network nodes accessible by pedestrian network)
        self.conn.sql(f"""
            CREATE OR REPLACE TABLE Graph_nodes_accessible AS
            SELECT n.*, p.id AS pedestrian_node_id
            FROM Graph_nodes n
            JOIN Graph_nodes_ped p
            ON ST_DWithin(p.geometry, n.loc, {settings.max_dist_ped_transit})
        """)

        # Add edges between drive network en pedestrian network
        df = self.conn.sql("""
            SELECT id, pedestrian_node_id
            FROM Graph_nodes_accessible
        """).df()
        ebunch = df.itertuples(index=False, name=None)
        self.network.add_edges_to_ped_network(ebunch)

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
                    c.pop,
                    coalesce(a.count, 0),
                    area,
                    c.male,
                    c.female,
                    c.age_00_14,
                    c.age_15_24,
                    c.age_25_44,
                    c.age_45_64,
                    c.age_65_oo,
                    c.background_nl,
                    c.background_eu,
                    c.background_neu,
                    c.birthplace_nl,
                    c.birthplace_eu,
                    c.birthplace_neu,
                    c.low_education,
                    c.medium_education,
                    c.high_education,
                    c.low_income,
                    c.high_income,
                    c.risk_poverty,
                    c.geom
                FROM (SELECT *, ST_Area(geom) as area
                      FROM CBS
                      WHERE gm_naam='{self.city}' AND recs='Buurt') c
                LEFT JOIN (SELECT c2.id, count(*) as count
                           FROM Features f
                           JOIN CBS c2
                           ON ST_Within(f.loc, c2.geom)
                           WHERE gm_naam='{self.city}' AND recs='Buurt' AND public_transport IS NULL
                           GROUP BY c2.id ) a
                ON c.id = a.id
            """)

    def create_pts_per_neighborhood(self):
        """
        ### Expected:
            - Pre_processing run
        ### Parameters:
            - None
        ### Returns:
            - None
        ### Side-effects:
            - (Re)create Neighborhood_pts table
        ### Notes
            - Uses algorithm from configuration to obtain point locations
            - Links point locations to nearest node in pedestrian network
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
        # Remove pts outside neighborhood
        # Points linked to ped_network by closest node within transit_max_pts_dist
        self.conn.sql(f"""
            INSERT INTO Neighborhood_pts (neighborhood_id, pt, node_id)
            SELECT pt.ids, ST_Point(pt.xs, pt.ys), ped.id
            FROM Neighborhood_pts_df pt
            JOIN Neighborhoods n
            ON pt.ids = n.id AND ST_Within(ST_Point(pt.xs, pt.ys), n.geometry)
            JOIN Graph_nodes_ped ped
            ON ST_DWithin(ST_Point(pt.xs, pt.ys), ped.geometry, {settings.transit_max_pts_dist})
            QUALIFY row_number()
            OVER (PARTITION BY ped.id
                  ORDER BY ST_Distance(ST_Point(pt.xs, pt.ys), ped.geometry) ASC) = 1
            """)

        # Keeping track of neighborhoods lost during point generation
        # Total neighborhoods.
        self.num_buurten = self.conn.sql("SELECT count(id) FROM Neighborhoods").fetchone()[0] # type: ignore
        # Total lost
        self.lost = self.num_buurten - self.conn.sql("SELECT count(neighborhood_id) FROM (SELECT DISTINCT neighborhood_id FROM Neighborhood_pts)").fetchone()[0] # type: ignore

    def obtain_generated_pts(self):
        """
        ### Expects:
            - create_pts_per_neighborhood run
        ### Parameters:
            - None
        ### Returns:
            - (xs, ys)\n
                Here xs and ys are numpy arrays containing the x and y coordinates of the points respectively
        ### Side-effects:
            - None
        """
        arrow = self.conn.sql(""" SELECT ST_X(pt) AS x, ST_Y(pt) AS y FROM Neighborhood_pts """).to_arrow_table()
        return (arrow.column("x").to_numpy(), arrow.column("y").to_numpy())

    def remove_f_edges(self, fraction: float, use_population=True, use_amenity=False):
        """
        ### Description:
            Will sort the edges based scoring formula (see report).
            Will then transform desired fraction of total car-accessible streets\
        ### Expected:
            - Pre_process run
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
            - Updates street_count in Graph_nodes table
        """
        # Get city total road length
        tot_street_len = self.conn.sql("""
            SELECT SUM(length)
            FROM Graph_edges
            WHERE NOT removed
        """).fetchone()[0] # type: ignore
        if tot_street_len is None or tot_street_len == 0:
            raise Exception("Failed calculating total street length")
            return
        tot_street_len = float(tot_street_len)

        # Determine pedestrianization method
        if use_population and use_amenity:
            density = """
                n.population * n.amenities / n.area
            """
        elif use_population:
            density = """
                n.population / n.area
            """
        elif use_amenity:
            density = """
                n.amenities / n.area
            """
        else:
            raise ValueError(
                "use_population and use_amenity can't both be false"
            )

        # Obtain starting score per neighborhood
        initial_df = self.conn.sql(f"""
            WITH ped AS (
                SELECT neighborhood_id, SUM(length) AS ped_len
                FROM Graph_edges_ped
                GROUP BY neighborhood_id
                ),
                car AS (
                    SELECT neighborhood_id, SUM(length) AS car_len
                    FROM Graph_edges
                    WHERE NOT removed
                    GROUP BY neighborhood_id
                )
            SELECT n.id AS neighborhood_id,
                   {density} AS density,
                   COALESCE(p.ped_len, 0.0) AS ped_len,
                   COALESCE(p.ped_len, 0.0) + COALESCE(c.car_len, 0.0) AS tot_len,
                   COALESCE(p.ped_len, 0.0) / (COALESCE(p.ped_len, 0.0) + COALESCE(c.car_len, 0.0)) AS ped_frac
            FROM Neighborhoods n
            LEFT JOIN ped p
            ON p.neighborhood_id = n.id
            JOIN car c
            ON c.neighborhood_id = n.id
        """).df()

        # Initialize normalization variables
        density_min = float(initial_df["density"].min())
        density_max = float(initial_df["density"].max())
        density_diff = density_max - density_min
        if density_diff <= 0: density_diff = 1.0
        fraction_min = float(initial_df["ped_frac"].min())
        fraction_max = float(initial_df["ped_frac"].max())
        fraction_diff = fraction_max - fraction_min
        if fraction_diff <= 0: fraction_diff = 1.0

        # Neighborhood score dictionary
        neighborhoods = {}
        for row in initial_df.itertuples(index=False):
            density_norm = (float(row.density) - density_min) / density_diff # type: ignore
            neighborhoods[row.neighborhood_id] = {
                "density": float(density_norm), # type: ignore
                "ped_len": float(row.ped_len), # type: ignore
                "tot_len": float(row.tot_len), # type: ignore
            }

        # Get removable edges
        edges_df = self.conn.sql("""
            SELECT u, v, key, length, neighborhood_id
            FROM Graph_edges
            WHERE NOT removed
        """).df()

        # Group edges by neighborhood
        neighborhood_edges = defaultdict(list)
        for row in edges_df.itertuples(index=False):
            neighborhood_edges[row.neighborhood_id].append((row.u, row.v, row.key, float(row.length))) # type: ignore

        # Create heap queue sorting the neighborhoods based on score
        heap = []
        for neighborhood_id, score in neighborhoods.items():
            tot_len = score["tot_len"]
            if tot_len <= 0:
                continue
            score = score["density"] * (score["ped_len"] / score["tot_len"] - fraction_min) / fraction_diff
            heapq.heappush(heap, (-score, neighborhood_id))

        # Iteratively select edges to remove based on neighborhood scores
        pedestrianized = 0.0
        # Lists used to build edges_to_remove table
        to_pedestrianize_u = []
        to_pedestrianize_v = []
        to_pedestrianize_key = []
        # While the fraction of road to be removed isn't met, transform next edge
        while (pedestrianized / tot_street_len < fraction and heap):
            # Best scoring neighborhood (with edges to pedestrianize)
            _, neighborhood_id = heapq.heappop(heap)
            if not neighborhood_edges[neighborhood_id]:
                continue

            # Neighborhood score (related) data
            score = neighborhoods[neighborhood_id]

            # Get random edge
            idx = random.randrange(len(neighborhood_edges[neighborhood_id]))
            u, v, key, length = neighborhood_edges[neighborhood_id].pop(idx)

            # Update total and score values for transformed edge
            # Then insert neighborhood back into heap (if edges remain)
            pedestrianized += length
            score["ped_len"] += length
            if score["tot_len"] > 0:
                new_score = score["density"] * (score["ped_len"] / score["tot_len"]  - fraction_min) / fraction_diff
                if neighborhood_edges[neighborhood_id]:
                    heapq.heappush(heap, (-new_score, neighborhood_id))

            # Save transformed edge to update database later
            to_pedestrianize_u.append(u)
            to_pedestrianize_v.append(v)
            to_pedestrianize_key.append(key)

        # Create dataframe of the to remove edges and import it into duckdb
        to_remove_df = pd.DataFrame({
            "u": to_pedestrianize_u,
            "v": to_pedestrianize_v,
            "key": to_pedestrianize_key,
        })
        self.conn.register("to_remove_df", to_remove_df)
        self.conn.sql("""
            CREATE OR REPLACE TEMP TABLE edges_to_remove AS
            SELECT *
            FROM to_remove_df
        """)

        # Remove the edges from the network
        ebunch = list(to_remove_df.itertuples(index=False, name=None))
        self.network.transform_edges(ebunch)

        # Update database with removed edges
        # Removed tag for edges
        self.conn.sql("""
            UPDATE Graph_edges g
            SET removed = true
            FROM edges_to_remove r
            WHERE g.u = r.u AND g.v = r.v AND g.key = r.key
        """)
        # Recalculate street count
        self.conn.sql("""
            UPDATE Graph_nodes
            SET street_count = 0
        """)
        self.conn.sql("""
            UPDATE Graph_nodes
            SET street_count = sub.degree
            FROM (SELECT node_id, COUNT(*) AS degree
                  FROM (SELECT u AS node_id
                        FROM Graph_edges
                        WHERE NOT removed
                        UNION ALL
                        SELECT v AS node_id
                        FROM Graph_edges
                        WHERE NOT removed AND oneway
                  )
                GROUP BY node_id
            ) sub
            WHERE id = sub.node_id
        """)

    def link_busses(self):
        """
        ### Expected:
            - Pre-process done (pre_process called)
        ### Parameters:
            - None
        ### Returns:
            - None
        ### Side_effects;
            - Creates table Stations linking busstations to nodes. (If it doesn't exist already)
        """
        # Link bus-stations to nodes (create table Bus_stations)
        self.conn.sql(f"""
            CREATE TABLE IF NOT EXISTS Stations AS
            SELECT f.id AS feature_id, n.id AS node_id, f.loc, f.bus, f.train, f.railway
            FROM (SELECT * FROM Features WHERE bus='yes' OR train='yes' OR railway='stop') f
            JOIN Graph_nodes n
            ON ST_DWithin(f.loc, n.loc, {settings.transit_max_edge_dist})
            QUALIFY row_number() OVER (PARTITION BY f.element, f.id ORDER BY ST_Distance(f.loc, n.loc) ASC) = 1
        """)

    def move_transit_minimal(self):
        """
        ### Description
            Moves Bus stations that are isolated from the driving network.
            A node will be considered isolated if the degree < 2. The transit will
            then be moved to the nearest node with a degree >= 2 that is connected
            to the pedestrian network.
            As transit stops are not nessisarily connected to the street network, transit
            is mapped to the nearest edge in the network. Here the maximum distance between
            a transit and an edge before the transit is ignored can be set in settings.py
            (transit_max_edge_dist). Default = 30. (In meters)
        ### Expected:
            - busses linked (link_busses called)
        ### Parameters:
            - None
        ### Returns:
            - None
        ### Side_effects;
            - (Re)creates table for Bus_stations_to_move.
            - Updates Stations table with new, moved transit
        """
        # Get minimal pairs with smallest distance between the two.
        self.conn.sql(f"""
            CREATE OR REPLACE TABLE Bus_stations_to_move AS
            SELECT isolated_busses.feature_id AS feature_id,
                   isolated_busses.node_id AS old_node, node_candidates.id AS new_node,
                   isolated_busses.loc AS old_loc, node_candidates.loc AS new_loc
            FROM (SELECT b.node_id, b.feature_id, b.loc
                  FROM Stations b
                  JOIN Graph_nodes n
                  ON b.node_id = n.id
                  WHERE n.street_count < 2 AND b.bus='yes'
                 ) isolated_busses
            JOIN (SELECT DISTINCT id, loc
                  FROM Graph_nodes_accessible
                  WHERE street_count >= 2
                 ) node_candidates
            ON ST_DWithin(isolated_busses.loc, node_candidates.loc, {settings.transit_max_move_dist})
            QUALIFY row_number() OVER (PARTITION BY isolated_busses.feature_id
                                       ORDER BY ST_Distance(isolated_busses.loc, node_candidates.loc) ASC) = 1
        """)

        # Update Stations with new, moved transit.
        self.conn.sql("""
            UPDATE Stations
            SET node_id = b.new_node
            FROM Bus_stations_to_move b
            WHERE Stations.feature_id = b.feature_id
            """)

    def move_transit_blank_slate(self):
        """
        ### Description
        Makes use of method described in report.
        ### Expected:
            - busses linked (link_busses called)
        ### Parameters:
            - None
        ### Returns:
            - None
        ### Side_effects;
            - (Re)creates table for Bus_stations_to_move.
            - Updates Stations table with new, moved transit
        """
        # Candidate start-end points == train/metro stations.
        # Subquery to select train stations (bus stops )
        train_metro = """
            SELECT f.id, s.node_id, f.loc
            FROM Stations s
            JOIN Features f
            ON s.feature_id = f.id
            WHERE f.railway='stop' OR f.train='yes'
        """
        # Create origin-destination pairs, start routes with origin as stop 0
        origin_dest = f"""
            SELECT s1.id, s1.loc, s2.id, s2.loc, s1.id, s1.loc, [s1.id], 0
            FROM ({train_metro}) s1
            JOIN ({train_metro}) s2
            ON s1.id < s2.id
        """
        # Recursively determine possible bus routes, creates table
        self.conn.sql(f"""
            CREATE OR REPLACE TABLE Bus_routes AS
            WITH RECURSIVE routes(origin, origin_loc, dest, dest_loc, stop, stop_loc, path_list, stop_number)
                USING KEY (origin, dest)
            AS (
                -- Base table
                ({origin_dest})
                    UNION
                -- Recursive step: adding next stop to the table
                SELECT r.origin, r.origin_loc, r.dest, r.dest_loc, n.id, n.loc, list_append(r.path_list, n.id), r.stop_number + 1
                FROM routes r
                -- Select from candidate bus stops:
                JOIN Graph_nodes_accessible n
                -- Condition: Maximum distance between stops
                ON ST_DWithin(r.stop_loc, n.loc, {settings.max_distance_stops})
                WHERE
                    -- Condition: Maximum bus_route length
                    r.stop_number < {settings.max_stops_in_bus_route}
                    -- Condition: Minimum distance between stops
                    AND ST_Distance(r.stop_loc, n.loc) > {settings.min_distance_stops}
                    -- Condition: Closer to destination
                    AND ST_Distance(n.loc, r.dest_loc) < ST_Distance(r.stop_loc, r.dest_loc)
                    -- Condition: Further from origin
                    AND ST_Distance(n.loc, r.origin_loc) > ST_Distance(r.stop_loc, r.origin_loc)
                -- Select closest stop qualifying
                QUALIFY row_number()
                    OVER(PARTITION BY r.origin, r.dest
                         ORDER BY ST_Distance(r.stop_loc, n.loc) ASC) = 1
            )
            FROM routes
            -- Bus stops having too little stops are removed.
            WHERE stop_number > {settings.min_stops_in_bus_route}
        """)

        # Score the routes
        self.conn.sql(f"""
            CREATE OR REPLACE TEMP TABLE Selected_routes AS
            -- Pre-calculate score/node
            WITH Node_scores AS (
                SELECT g.id as node_id, (n.population + 100 * n.amenities) AS score
                FROM Graph_nodes_accessible g
                JOIN Neighborhoods n
                ON g.neighborhood_id = n.id
            )
            SELECT DISTINCT ON (route_score) r.*, sum(s.score) AS route_score
            FROM Bus_routes r,
            unnest(r.path_list) AS t(node_id)
            JOIN Node_scores s
            ON t.node_id = s.node_id
            GROUP BY ALL
        """)
        # Select top routes and insert stops into Stations table
        # Stop count may have a deviation (see below)
        deviation = int((settings.max_stops_in_bus_route - settings.min_stops_in_bus_route) / 2)
        self.conn.sql(f"""
            -- Determine original number of transit stops
            SELECT stop_number, route_score, path_list
            FROM Selected_routes
            QUALIFY sum(stop_number)
            OVER (ORDER BY route_score DESC) <=
                        (SELECT count(*) + {deviation} FROM Stations WHERE bus IS NOT NULL)
        """)

        self.conn.sql("SELECT * FROM Selected_routes").to_csv("Selected_routes.csv")


    def calculate_distances_to_nearest_transit(self):
        """
        ### Description
            For every point representing a neighborhood, it will calculate the
            distance to the nearest transit using the pedestrian network.
        ### Expects
            - link_busses()
            - create_pts_per_neighborhood()
        ### Returns
            - None
        ### Side-effects:
            - (Re)creates table Distances (node_id, dist)
        """
        # Get Sources = Transit stops (as they are less points)
        ped_transit_np = self.conn.sql("""
            SELECT n.pedestrian_node_id
            FROM Graph_nodes_accessible n
            JOIN Stations s
            ON n.id = s.node_id
        """).fetchnumpy()
        ped_transit = ped_transit_np['pedestrian_node_id'].tolist()

        # Calculate distances from sources to all other nodes
        dists = self.network.get_distances_to_transit(ped_transit)

        # Import into duckdb
        dists_table = pa.table({
            "node_id": list(dists.keys()),
            "dist": list(dists.values())
        })
        self.conn.register("dists_table", dists_table)
        self.conn.sql("""
            CREATE OR REPLACE TABLE Distances AS
            SELECT *
            FROM dists_table
        """)

    def get_dist_per_neighborhood(self):
        """
        ### Expects:
            - get_neighborhood_dist_to_nearest_transit
        ### Parameters:
            - None
        ### Returns:
            - geopandas GeoDataFrame:\n
                (neighborhood, WKB, neighborhood_id, avg_dist)
        ### Side-effects:
            - (Re)creates table Dist_per_neighborhood
        """
        # Group by neighborhood, join point with dist, avg dist
        self.conn.sql("""
            CREATE OR REPLACE TABLE Dist_per_neighborhood AS
            SELECT pt.neighborhood_id, avg(d.dist) AS avg_dist
            FROM Neighborhood_pts pt
            LEFT JOIN Distances d
            ON pt.node_id = d.node_id
            GROUP BY pt.neighborhood_id
        """)
        df = self.conn.sql("""
            SELECT n.regio AS neighborhood, ST_AsWKB(n.geometry) AS wkb, d.*
            FROM Dist_per_neighborhood d
            JOIN Neighborhoods n
            ON n.id = d.neighborhood_id
            ORDER BY d.avg_dist DESC
            """).df()
        df['geometry'] = df['wkb'].apply(lambda x: wkb.loads(bytes(x))) # type: ignore
        return gpd.GeoDataFrame(df, geometry='geometry', crs='epsg:28992')

    def get_demographic_average_distance(self):
        """
        ### Expects:
            - get_neighborhood_dist_to_nearest_transit
            - get_dist_per_neighborhood
        ### Parameters:
            - None
        ### Returns:
            - Pandas DataFrame (dem_grp, avg_dist):\n
              Demographic groups are the following:
                - male
                - female
                - 0-14
                - 15-34
                - 25-44
                - 45-64
                - 65+
                - background_nl
                - background_eu
                - background_neu
                - born_nl
                - born_eu
                - born_neu
                - low_education
                - mid_education
                - high_education
                - low_income
                - high_income
                - risk_poverty
        ### Side-effects:
            - None
        """
        return self.conn.sql("""
            WITH
                Flattened AS (
                    SELECT id, 'avg' AS key, population AS value FROM Neighborhoods
                    UNION ALL
                    SELECT id, 'male', num_male FROM Neighborhoods
                    UNION ALL
                    SELECT id, 'female', num_female FROM Neighborhoods
                    UNION ALL
                    SELECT id, '0-14', num_age_00_14 FROM Neighborhoods
                    UNION ALL
                    SELECT id, '15-24', num_age_15_24 FROM Neighborhoods
                    UNION ALL
                    SELECT id, '25-44', num_age_25_44 FROM Neighborhoods
                    UNION ALL
                    SELECT id, '45-64', num_age_45_64 FROM Neighborhoods
                    UNION ALL
                    SELECT id, '65+', num_age_65_oo FROM Neighborhoods
                    UNION ALL
                    SELECT id, 'background_nl', num_background_nl FROM Neighborhoods
                    UNION ALL
                    SELECT id, 'background_eu', num_background_eu FROM Neighborhoods
                    UNION ALL
                    SELECT id, 'background_neu', num_background_neu FROM Neighborhoods
                    UNION ALL
                    SELECT id, 'born_nl', num_birthplace_nl FROM Neighborhoods
                    UNION ALL
                    SELECT id, 'born_eu', num_birthplace_eu FROM Neighborhoods
                    UNION ALL
                    SELECT id, 'born_neu', num_birthplace_neu FROM Neighborhoods
                    UNION ALL
                    SELECT id, 'low_education', num_low_education FROM Neighborhoods
                    UNION ALL
                    SELECT id, 'mid_education', num_medium_education FROM Neighborhoods
                    UNION ALL
                    SELECT id, 'high_education', num_high_education FROM Neighborhoods
                    UNION ALL
                    SELECT id, 'low_income', percent_low_income * population FROM Neighborhoods
                    UNION ALL
                    SELECT id, 'high_income', percent_high_income * population FROM Neighborhoods
                    UNION ALL
                    SELECT id, 'risk_poverty', percent_risk_poverty * population FROM Neighborhoods
                ),
                Totals AS (
                    SELECT key, sum(value) AS total
                    FROM Flattened
                    GROUP BY key
                )
            SELECT f.key AS dem_grp, sum (f.value * d.avg_dist) / t.total AS avg_dist
            FROM Flattened f
            JOIN Totals t
            ON f.key = t.key
            LEFT JOIN Dist_per_neighborhood d
            ON f.id = d.neighborhood_id
            GROUP BY f.key, t.total
            ORDER BY f.key
        """).df()

    def get_population_distribution(self):
        """
        ### Expects:
            - Pre-process run
        ### Parameters:
            - None
        ### Returns:
            Dataframe (neighborhood, density)
        ### Side-effects:
            - None
        """
        df = self.conn.sql("""
            SELECT regio AS neighborhood, 100 * population / area AS density, ST_AsWKB(geometry) AS wkb
            FROM Neighborhoods
        """).df()
        df['geometry'] = df['wkb'].apply(lambda x: wkb.loads(bytes(x))) # type: ignore
        return gpd.GeoDataFrame(df, geometry='geometry', crs='epsg:28992')

    def get_amenity_pts(self):
        """
        ### Expects:
            - Get features run
        ### Parameters:
            - None
        ### Returns:
            - (xs, ys)\n
                Here xs and ys are numpy arrays containing the x and y coordinates of the points respectively
        ### Side-effects:
            - None
        """
        arrow = self.conn.sql(""" SELECT ST_X(ST_Centroid(loc)) AS x, ST_Y(ST_Centroid(loc)) AS y FROM Features WHERE bus IS NULL""").to_arrow_table()
        return (arrow.column("x").to_numpy(), arrow.column("y").to_numpy())
