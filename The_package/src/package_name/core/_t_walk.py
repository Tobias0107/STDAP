"""
This file contains all functions related to computing t_walk:
the average walking time from neighborhood points to the nearest transit stop.


The computation is based on the pedestrian network and uses
shortest path distances (multi-source Dijkstra) from transit stops
to all nodes in the network.


Distances are converted to walking time in minutes.
"""
from package_name.core._classes import Database
import pandas as pd

def compute_t_walk(database, network):
    """
    ### Expected:
        - create_pts_per_neighborhood() run
        - network loaded
    ### Returns:
        - DataFrame (neighborhood_id, avg_dist)
    """

    # 1. link transit stops to graph
    database.link_busses()

    # 2. fix isolated stops
    database.move_transit_minimal()

    # 3. compute shortest path distances
    database.calculate_distances_to_nearest_transit()

    # 4. aggregate per neighborhood
    df = database.get_dist_per_neighborhood()

    return df

def attach_geometry_to_t_walk(database, df):
    """
    ### Expected:
        - df contains neighborhood_id and avg_dist

    ### Returns:
        - GeoDataFrame with geometry and avg_dist
    """
    import geopandas as gpd
    from shapely import wkb

    geom_df = database.conn.sql("""
        SELECT id, ST_AsWKB(geometry) AS geometry
        FROM Neighborhoods
    """).df()

    geom_df["geometry"] = geom_df["geometry"].apply(lambda x: wkb.loads(bytes(x)))

    gdf_geom = gpd.GeoDataFrame(geom_df, geometry="geometry", crs="EPSG:28992")

    merged = df.merge(
        gdf_geom,
        left_on="neighborhood_id",
        right_on="id",
        how="left"
    )

    if "geometry" not in merged.columns:
        if "geometry_y" in merged.columns:
            merged = merged.rename(columns={"geometry_y": "geometry"})
        elif "geometry_x" in merged.columns:
            merged = merged.rename(columns={"geometry_x": "geometry"})
        else:
            raise ValueError("No geometry column found after merge")

    gdf = gpd.GeoDataFrame(merged, geometry="geometry", crs="EPSG:28992")

    return gdf