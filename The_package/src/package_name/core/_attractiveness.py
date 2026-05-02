import pandas as pd

def compute_attractiveness(database, weights=None, normalize_cols=False):
    """
    ### Expected:
        - pre_process() run

    ### Parameters:
        - database:
            Database object
        - weights:
            dict of weights, e.g. {"population": 1.0}
        - normalize_cols:
            If True: normalize each component before weighting

    ### Returns:
        - DataFrame (neighborhood_id, attractiveness)
    """

    if weights is None:
        weights = {"population": 1.0}

    df = database.conn.sql("""
        SELECT
            id AS neighborhood_id,
            population,
            amenities,
            area
        FROM Neighborhoods
    """).df()

    # Normalize if requested
    if normalize_cols:
        for col in weights.keys():
            if col not in df.columns:
                raise ValueError(f"Unknown attractiveness component: {col}")
            df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

    # Compute weighted sum
    df["attractiveness"] = 0.0

    for key, w in weights.items():
        if key not in df.columns:
            raise ValueError(f"Unknown attractiveness component: {key}")
        df["attractiveness"] += w * df[key]

    return df[["neighborhood_id", "attractiveness"]]

def attach_geometry_to_attractiveness(database, df):
    """
    ### Returns:
        - GeoDataFrame with geometry and attractiveness
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

    return gpd.GeoDataFrame(merged, geometry="geometry", crs="EPSG:28992")

def plot_attractiveness_map(gdf, storage_folder="debug", name="attractiveness", show=False):
    """
    ### Description:
        Plot attractiveness per neighborhood
    """

    import os
    import matplotlib.pyplot as plt

    os.makedirs(storage_folder, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 10))

    gdf.plot(
        column="attractiveness",
        cmap="plasma",
        legend=True,
        ax=ax
    )

    plt.title("Neighborhood attractiveness")
    plt.axis("off")

    filepath = f"{storage_folder}/{name}.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()

