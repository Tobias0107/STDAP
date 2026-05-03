"_t_travel.py: Compute OD travel time matrix using R5 (transit + walking)"

from datetime import datetime
from datetime import timedelta
import pandas as pd
from r5py import TravelTimeMatrix
from package_name.core._accessibility_model import _get_neighborhood_centroids

def compute_t_travel_matrix(
    network,
    origins,
    destinations,
    departure_time: datetime,
    batch_size: int = 50,
    max_time: timedelta = timedelta(minutes=120),
):
    """
    ### Purpose:
        - Compute OD travel time matrix using R5 (transit + walking)

    ### Expected:
        - R5 network initialized
        - origins and destinations are GeoDataFrames (EPSG:4326)
        - origins contain column 'id'
        - destinations contain column 'id'

    ### Parameters:
        - network:
            Network object with R5 network
        - origins:
            GeoDataFrame of origin points
        - destinations:
            GeoDataFrame of destination points
        - departure_time:
            Datetime for routing
        - batch_size:
            Number of origins per batch
        - max_time:
            Max travel time in minutes

    ### Returns:
        - pandas DataFrame:
            Columns:
                - from_id
                - to_id
                - travel_time

    ### Side-effects:
        - Runs R5 Java routing

    ### Description:
        - Batches origins to avoid memory issues
        - Computes full OD matrix
        - Concatenates results
    """

    r5_network = network.get_r5_network()

    results = []

    # --------------------------------------------------
    # 1. Batch computation
    # --------------------------------------------------
    for i in range(0, len(origins), batch_size):

        batch = origins.iloc[i:i + batch_size]

        print(f"[t_travel] batch {i}–{i + len(batch)}")

        ttm = TravelTimeMatrix(
            transport_network=r5_network,
            origins=batch,
            destinations=destinations,
            departure=departure_time,
            transport_modes=["WALK", "TRANSIT"],
            max_time=max_time
        )

        df_batch = pd.DataFrame(ttm)

        results.append(df_batch)

    # --------------------------------------------------
    # 2. Combine batches
    # --------------------------------------------------
    df_all = pd.concat(results, ignore_index=True)

    # --------------------------------------------------
    # 3. Remove self-travel
    # --------------------------------------------------
    df_all = df_all[df_all["from_id"] != df_all["to_id"]]

    return df_all

def compute_avg_travel_time_per_origin(df):
    """
    Convert OD matrix → average travel time per origin
    """

    return (
        df.groupby("from_id")["travel_time"]
        .mean()
        .reset_index()
        .rename(columns={"travel_time": "avg_travel_time"})
    )



