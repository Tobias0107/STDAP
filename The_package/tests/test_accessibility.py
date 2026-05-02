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
    database.obtain_features()
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

    from package_name.core._t_walk import compute_t_walk, attach_geometry_to_t_walk
    from package_name.utils.util_plotting import plot_t_walk_map

    df = compute_t_walk(database, network)

    gdf = attach_geometry_to_t_walk(database, df)

    plot_t_walk_map(
        gdf,
        storage_folder="debug",
        name="t_walk_amsterdam"
    )

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
        - Plot is successfully generated and saved

    ### Description:
        - Integration test: database → t_walk → geometry → visualization
    """

    import os
    from package_name.core._t_walk import (
        compute_t_walk,
        attach_geometry_to_t_walk
    )
    from package_name.core._classes import Database, Network
    from package_name.utils.util_plotting import plot_t_walk_map

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
    database.create_pts_per_neighborhood()

    # === Step 1: compute t_walk ===
    df = compute_t_walk(database, network)

    # === Step 2: attach geometry ===
    gdf = attach_geometry_to_t_walk(database, df)

    # === Step 3: generate plot ===
    output_folder = "debug"
    output_name = "t_walk_pytest"

    plot_t_walk_map(
        gdf,
        storage_folder="debug",
        name="t_walk_pytest",
        show=True  
   )

    output_path = f"{output_folder}/{output_name}.png"

    # === Step 4: assertions ===
    assert len(df) > 0
    assert len(gdf) > 0
    assert os.path.exists(output_path)

def test_attractiveness_full():
    """
    ### Expected:
        - Attractiveness computed for Amsterdam neighborhoods
        - Plot is successfully generated and saved

    ### Description:
        - Integration test: database → attractiveness → geometry → visualization
    """

    import os
    from package_name.core._attractiveness import (
        compute_attractiveness,
        attach_geometry_to_attractiveness
    )
    from package_name.core._classes import Database, Network
    from package_name.utils.util_plotting import plot_attractiveness_map

    csv = "tests/TestDatasets/test.csv"
    geopackage = os.path.abspath("tests/TestDatasets/test.gpkg")

    # === Setup ===
    network = Network("Amsterdam", store_in_file=True)

    database = Database(csv, geopackage)

    database.set_city("Amsterdam")
    database.load_network(network)
    database.pre_process()

    # === Step 1: compute attractiveness ===
    df_attr = compute_attractiveness(database)

    # === Step 2: attach geometry ===
    gdf_attr = attach_geometry_to_attractiveness(database, df_attr)

    # === Step 3: plot ===
    output_folder = "debug"
    output_name = "attractiveness_test"

    plot_attractiveness_map(
        gdf_attr,
        storage_folder=output_folder,
        name=output_name,
        show=True
    )

    output_path = f"{output_folder}/{output_name}.png"

    # === Assertions ===
    assert len(df_attr) > 0
    assert len(gdf_attr) > 0
    assert os.path.exists(output_path)