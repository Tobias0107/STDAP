"""
This file contains all functions related to computing accessibility
based on a gravity-based model using travel times.
"""


# Imports
from package_name.core._classes import Database, Network
import numpy as np
from r5py import TravelTimeMatrix
import geopandas as gpd
from datetime import datetime
from package_name.config.data_path import PBF_FILE

def run_accessibility(network: Network,
                     database: Database,
                     departure_time: datetime,
                     beta: float,
                     print_progress=True):
   """
   ### Expected:
       - Network has r5 network initialized
       - Database has been pre-processed and contains Neighborhood_pts
   ### Parameters:
       - network:\n
           Network object containing OSMnx and r5 network
       - database:\n
           Database object containing neighborhood and demographic data
       - departure_time:\n
           Datetime object representing departure time for travel time computation
       - beta:\n
           Distance decay parameter
       - print_progress:\n
           If True: prints progress updates
   ### Returns:
       - Dictionary mapping neighborhood id to accessibility score
   ### Side-effects:
       - None
   ### Notes:
       - Accessibility is computed as:
           A_i = sum_j O_j * exp(-beta * t_ij)
   """


   if print_progress:
       print("Starting accessibility computation...")


   # 1. Origins (neighborhood representative points)
   origins = _get_neighborhood_points(database)


   # 2. Destinations (neighborhood centroids)
   destinations = _get_neighborhood_centroids(database)


   # DEBUG: check of punten binnen testgebied liggen
   print("=== DEBUG BOUNDS ===")
   print("origins bounds:", origins.total_bounds)
   print("destinations bounds:", destinations.total_bounds)
   print("origins count:", len(origins))
   print("destinations count:", len(destinations))
   print("====================")


   # 3. Travel times (t_ij)
   travel_times = _compute_travel_times(network, origins, destinations, departure_time)
   print(travel_times.columns)
   # 4. Opportunities (O_j)
   opportunities = _get_opportunities(database)


   # 5. Accessibility calculation
   accessibility = _compute_accessibility(travel_times, opportunities, beta)


   if print_progress:
       print("Accessibility computation finished.")


   print("origins:", len(origins))
   print("destinations:", len(destinations))
   print(origins.head())
   print(destinations.head())
   return accessibility




def _compute_travel_times(network,
                         origins_gdf,
                         destinations_gdf,
                         departure_time):
   """
   ### Expected:
       - r5 network initialized
       - origins and destinations in EPSG:4326


   ### Parameters:
       - network:\n
           Network object containing r5 network
       - origins_gdf:\n
           GeoDataFrame with origin points
       - destinations_gdf:\n
           GeoDataFrame with destination points
       - departure_time:\n
           Datetime object


   ### Returns:
       - DataFrame with travel times between origin-destination pairs


   ### Side-effects:
       - None


   ### Description:
       - Computes travel time matrix using r5
   """
   # Get r5 network
   r5_network = network.get_r5_network()

   # Initialize travel time matrix
   ttm = TravelTimeMatrix(
       transport_network=r5_network,
       origins=origins_gdf,
       destinations=destinations_gdf,
       departure=departure_time
   )

   # Compute travel times
   travel_time_matrix = ttm.compute_travel_times()


   return travel_time_matrix

from shapely import wkb
import geopandas as gpd

def _get_neighborhood_points(database):
   """
   ### Expected:
       - Table Neighborhood_pts exists
   """


   df = database.conn.sql("""
       SELECT
       neighborhood_id,
       pts_id AS id,
       ST_AsWKB(pt) AS geometry
   FROM Neighborhood_pts
   """).df()


   # === DEBUG 1: RAW SQL OUTPUT ===
   print("=== DEBUG WKB ===")
   print("rows in df:", len(df))


   if len(df) == 0:
       print("⚠️ NO ROWS RETURNED FROM SQL")
   else:
       print("type:", type(df["geometry"].iloc[0]))
       print("value:", df["geometry"].iloc[0])


   print("=================")


   def safe_wkb(x):
       """
       ### Expected:
           - WKB as bytes OR array/list of ints


       ### Returns:
           - Shapely geometry or None
       """


       try:
           # Case 1: already bytes → perfect
           if isinstance(x, (bytes, bytearray)):
               return wkb.loads(bytes(x))


           # Case 2: everything else → TRY to convert to bytes
           return wkb.loads(bytes(x))


       except Exception:
           return None


   df["geometry"] = df["geometry"].apply(safe_wkb)
   df = df.dropna(subset=["geometry"])


   gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:28992")
   gdf = gdf.to_crs("EPSG:4326")
   return gdf

def _get_neighborhood_centroids(database):
   """
   ### Expected:
       - Table Neighborhoods exists
       - Geometry column stored as WKB (DuckDB output)
   ### Parameters:
       - database:\n
           Database object
   ### Returns:
       - GeoDataFrame with neighborhood centroids as shapely geometries
   ### Side-effects:
       - None
   ### Description:
       - Retrieves neighborhood centroids from the database
       - Converts WKB geometries to shapely objects
       - Ensures compatibility with GeoPandas
   """
   # Step 1: Retrieve centroids as WKB
   df = database.conn.sql("""
       SELECT
           id,
           ST_AsWKB(ST_Centroid(geometry)) AS geometry
       FROM Neighborhoods
   """).df()
   print("Centroid WKB raw rows:", len(df))
   print("Null geometries:", df["geometry"].isna().sum())
   def safe_wkb(x):
       try:
           return wkb.loads(bytes(x))   # <-- FORCE bytes conversion
       except Exception:
           return None

   # Step 2: Convert WKB → shapely geometry
   df["geometry"] = df["geometry"].apply(safe_wkb)

   # Step 3: Remove invalid geometries
   df = df.dropna(subset=["geometry"])

   # Step 4: Convert to GeoDataFrame
   gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:28992")
   gdf = gdf.to_crs("EPSG:4326")
   return gdf

def _get_neighborhood_polygons(database):
   """
   ### Expected:
       - Table Neighborhoods exists
       - Geometry column stored as WKB (DuckDB output)

   ### Parameters:
       - database:\n
           Database object

   ### Returns:
       - GeoDataFrame with neighborhood polygons

   ### Side-effects:
       - None

   ### Description:
       - Retrieves neighborhood geometries from the database
       - Converts WKB geometries to shapely objects
       - Ensures compatibility with GeoPandas
   """
   from shapely import wkb
   import geopandas as gpd

   df = database.conn.sql("""
       SELECT
           id AS neighborhood_id,
           ST_AsWKB(geometry) AS geometry
       FROM Neighborhoods
   """).df()

   def safe_wkb(x):
       try:
           return wkb.loads(bytes(x))
       except Exception:
           return None

   df["geometry"] = df["geometry"].apply(safe_wkb)
   df = df.dropna(subset=["geometry"])

   gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:28992")
   gdf = gdf.to_crs("EPSG:4326")

   return gdf

def _get_opportunities(database):
   """
   ### Expected:
       - CBS table exists with population data


   ### Parameters:
       - database:\n
           Database object


   ### Returns:
       - DataFrame with neighborhood id and population


   ### Side-effects:
       - None


   ### Description:
       - Retrieves opportunity values (population per neighborhood)
   """


   return database.conn.sql("""
       SELECT id, pop
       FROM CBS
       WHERE recs='Buurt'
   """).df()




def _compute_accessibility(travel_times, opportunities, beta):
   """
   ### Expected:
       - travel_times contains from_id, to_id, travel_time
       - opportunities contains id and pop


   ### Parameters:
       - travel_times:\n
           DataFrame with travel times
       - opportunities:\n
           DataFrame with opportunity values
       - beta:\n
           Distance decay parameter


   ### Returns:
       - Dictionary mapping origin id to accessibility score


   ### Side-effects:
       - None


   ### Description:
       - Computes accessibility using gravity model:
         A_i = sum_j O_j * exp(-beta * t_ij)
   """


   # Convert opportunities to dictionary for fast lookup
   opp_dict = dict(zip(opportunities["id"], opportunities["pop"]))


   results = {}


   # Loop over origins
   for i in travel_times["from_id"].unique():
       subset = travel_times[travel_times["from_id"] == i]


       Ai = 0


       for _, row in subset.iterrows():
           j = row["to_id"]


           # NOTE: adjust if column name differs (e.g. travel_time_p50)
           tij = row["travel_time"]


           Oj = opp_dict.get(j)


           if Oj is None:
               continue


           Ai += Oj * np.exp(-beta * tij)


       results[i] = Ai


   return results