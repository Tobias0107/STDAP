from datetime import datetime
from package_name.core._classes import Network, Database
# Test dataset paths (used across tests)
csv = "tests/TestDatasets/test.csv"
geopackage = "tests/TestDatasets/test.gpkg"
from package_name.core._travel_time import compute_travel_times_basic
from package_name.core._travel_time import compute_travel_times_from_database
from package_name.core._t_walk import compute_t_walk
import os
import pytest
from package_name.config.data_path import PBF_FILE, GTFS_FILE


@pytest.mark.skipif(
    not os.path.exists(GTFS_FILE),
    reason="GTFS file not available"
)
def test_r5_basic():
   """
   ### Expected:
       - r5 network can be initialized successfully
       - TravelTimeMatrix computation runs without errors
       - At least one travel time result is returned


   ### Parameters:
       - None


   ### Returns:
       - None


   ### Side-effects:
       - Loads OSM and GTFS test datasets
       - Initializes r5 transport network
       - Executes routing computation


   ### Description:
       - Minimal integration test for r5py functionality
       - Ensures that the routing engine works independently of the database pipeline
   """


   # Initialize network for Amsterdam
   network = Network("Amsterdam", store_in_file=True)


   # Build r5 network using test datasets
   network.build_r5_network(
       osm_pbf_path=PBF_FILE,
       gtfs_files=[GTFS_FILE]
   )


   # Compute travel times
   df = compute_travel_times_basic(network.get_r5_network())


   # Validate that results exist
   assert len(df) > 0

@pytest.mark.skipif(
    not os.path.exists(GTFS_FILE),
    reason="GTFS file not available"
)
def test_r5_from_database():
   """
   ### Expected:
       - Database pipeline produces valid neighborhood points
       - r5 network can compute travel times from these points


   ### Description:
       - Integration test: Database → GeoDataFrame → r5
   """


   network = Network("Amsterdam", store_in_file=True)
   database = Database(csv, geopackage)


   database.set_city("Amsterdam")
   database.load_network(network)
   database.pre_process()
   database.create_pts_per_neighborhood()


   # === DEBUG: points BEFORE filtering ===
   total_pts = database.conn.sql("""
       SELECT COUNT(*) FROM Neighborhood_pts
   """).fetchone()[0]


   distinct_neighborhoods = database.conn.sql("""
       SELECT COUNT(DISTINCT neighborhood_id)
       FROM Neighborhood_pts
   """).fetchone()[0]


   print("Total points (raw):", total_pts)
   print("Neighborhoods (raw):", distinct_neighborhoods)


   # === DEBUG: check neighborhoods coverage ===
   total_neighborhoods = database.conn.sql("""
       SELECT COUNT(*)
       FROM Neighborhoods
   """).fetchone()[0]


   neighborhoods_with_points = database.conn.sql("""
       SELECT COUNT(DISTINCT neighborhood_id)
       FROM Neighborhood_pts
   """).fetchone()[0]


   print("Total neighborhoods:", total_neighborhoods)
   print("Neighborhoods with points:", neighborhoods_with_points)
   # ==========================================




   count = database.conn.sql("SELECT COUNT(*) FROM Neighborhood_pts").fetchone()[0]
   assert count > 0




   # === DEBUG VISUALIZATION ===
   import matplotlib.pyplot as plt
   from package_name.core._accessibility_model import _get_neighborhood_points


   origins = _get_neighborhood_points(database)
   print("Sample origin coords:")
   print(origins.head())
   print("CRS:", origins.crs)


   print("Number of points:", len(origins))
   print("Bounds:", origins.total_bounds)


   origins.plot(markersize=1)
   plt.title("Neighborhood points")
   plt.close()
   # ==========================




   network.build_r5_network(
       osm_pbf_path=PBF_FILE,
       gtfs_files=[GTFS_FILE]
   )


   count = database.conn.sql("SELECT COUNT(*) FROM Neighborhood_pts").fetchone()[0]
   assert count > 0


   df = compute_travel_times_from_database(
       database,
       network,
       departure_time=datetime(2024, 1, 1, 8, 0)
   )
   # === DEBUG: surviving origins in travel time matrix ===
   used_origins = df["from_id"].nunique()


   print("Neighborhoods used in routing:", used_origins)
   assert len(df) > 0


def test_t_walk_full():
   """
   ### Expected:
       - t_walk computed for Amsterdam neighborhoods
       - Uses OSMnx only (no r5 / no PBF)
   """


   import os
   from package_name.core._t_walk import compute_t_walk
   from package_name.core._classes import Database, Network


   csv = "tests/TestDatasets/test.csv"
   geopackage = os.path.abspath("tests/TestDatasets/test.gpkg")


   network = Network(
       "Amsterdam",
       store_in_file=True,
       store_dir=os.path.expanduser("~/.percolation_cache/")
   )


   database = Database(csv, geopackage)


   database.set_city("Amsterdam")
   database.load_network(network)
   database.pre_process()
   database.obtain_features()


   # 👇 IMPORTANT: depends on your implementation
   # you likely need:
   # - create_pts_per_neighborhood()
   # - link_busses()
   # - distance computation


   database.create_pts_per_neighborhood()


   df = compute_t_walk(database, network)


   print(df.head())


   assert len(df) > 0
