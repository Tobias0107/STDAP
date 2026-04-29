import geopandas as gpd
from shapely.geometry import Point
from r5py import TravelTimeMatrix
from datetime import datetime
from package_name.core._accessibility_model import _get_neighborhood_points
from package_name.core._accessibility_model import _get_neighborhood_centroids

def compute_travel_times_basic(r5_network):
    """
    ### Expected:
        - A valid r5py TransportNetwork object
        - r5 network must already be initialized using build_r5_network()

    ### Parameters:
        - r5_network:\n
            r5py TransportNetwork object containing OSM and GTFS data

    ### Returns:
        - pandas DataFrame (TravelTimeMatrix):\n
            A dataframe containing travel times between origin and destination points

    ### Side-effects:
        - Runs routing computation using r5 (Java backend)

    ### Description:
        - Creates a minimal example of origins and destinations using GeoPandas
        - Uses r5py's TravelTimeMatrix to compute travel times
        - Serves as a baseline test to verify that r5 is correctly configured
    """

    import geopandas as gpd
    from shapely.geometry import Point
    from r5py import TravelTimeMatrix
    from datetime import datetime
    from package_name.core._accessibility_model import _get_neighborhood_points

    # Define multiple origin points in Amsterdam
    origins = gpd.GeoDataFrame({
        "id": [1, 2, 3],
        "geometry": [
            Point(4.9, 52.37),
            Point(4.88, 52.36),
            Point(4.92, 52.35)
        ]
        }, crs="EPSG:4326")

    # Use same points as destinations
    destinations = origins.copy()

    # Initialize TravelTimeMatrix (this already computes travel times)
    ttm = TravelTimeMatrix(
        transport_network=r5_network,
        origins=origins,
        destinations=destinations,
        departure=datetime(2024, 1, 1, 8, 0)
    )

    # Return result (already a DataFrame)
    return ttm

def compute_travel_times_from_database(database,
                                       network,
                                       departure_time):
    """
    ### Expected:
        - Database has been pre-processed
        - Neighborhood_pts table exists and contains point geometries
        - Network has an initialized r5 transport network
        - All geometries are in EPSG:4326

    ### Parameters:
        - database:\n
            Database object containing Neighborhood_pts table
        - network:\n
            Network object containing initialized r5 network
        - departure_time:\n
            Datetime object specifying departure time for routing

    ### Returns:
        - pandas DataFrame (TravelTimeMatrix):\n
            DataFrame containing travel times between origin and destination points

    ### Side-effects:
        - Executes routing computation via r5 (Java backend)

    ### Raises:
        - ValueError:\n
            If no origin points are found in the database

    ### Description:
        - Extracts neighborhood points from DuckDB
        - Converts them to a GeoDataFrame
        - Uses these points as both origins and destinations
        - Computes a full travel time matrix using r5py
        - Serves as the integration layer between Database and r5
    """

    # Imports (local to avoid heavy dependency loading at module import time)
    from r5py import TravelTimeMatrix

    # 1. Extract origin points from database
    origins = _get_neighborhood_points(database)
    # === TEMP: limit size for testing ===
    origins = origins.head(50)

    # 2. Validate origin data
    if len(origins) == 0:
        raise ValueError("No origin points found: Neighborhood_pts table is empty")
    print("Neighborhoods table size:",
    
    database.conn.sql("SELECT COUNT(*) FROM Neighborhoods").fetchone()[0])
    print(database.conn.sql("DESCRIBE Neighborhoods").df())

    # 3. Use same points as destinations (baseline case)
    destinations = _get_neighborhood_centroids(database)
    print("Total centroids:", len(destinations))

    import matplotlib.pyplot as plt
    from shapely import wkb
    from shapely.geometry import Point
    import geopandas as gpd

    # Ensure geometry is shapely (safe conversion)
    if not isinstance(destinations.geometry.iloc[0], Point):
        destinations["geometry"] = destinations["geometry"].apply(wkb.loads)

    gdf = gpd.GeoDataFrame(destinations, geometry="geometry", crs="EPSG:4326")

    print("Number of centroids:", len(gdf))
    print("Bounds:", gdf.total_bounds)

    gdf.plot(markersize=5)
    plt.title("Neighborhood centroids")
    plt.show()

    ttm_test = TravelTimeMatrix(
        transport_network=network.get_r5_network(),
        origins=origins,
        destinations=destinations,
        departure=departure_time
    )

    df_test = ttm_test

    print("Centroids that survive routing:", df_test["from_id"].nunique())

    # 4. Ensure CRS is defined (required by r5)
    if origins.crs is None:
        origins.set_crs("EPSG:4326", inplace=True)

    if destinations.crs is None:
        destinations.set_crs("EPSG:4326", inplace=True)

    # 5. Retrieve r5 network
    r5_network = network.get_r5_network()

    # 6. Compute travel time matrix (r5 computes on initialization)
    ttm = TravelTimeMatrix(
        transport_network=r5_network,
        origins=origins,
        destinations=destinations,
        departure=departure_time
    )

    return ttm