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
       - DataFrame (neighborhood_id, t_walk_minutes)
   """


   # 1. link transit
   database.link_busses()


   # 2. move if needed
   database.move_transit_minimal()


   # 3. compute node distances
   database.get_neighborhood_dist_to_nearest_transit()


   # 4. aggregate per neighborhood
   df = database.get_dist_per_neighborhood()


   # 5. convert meters → minutes
   WALK_SPEED = 1.33  # m/s


   df["t_walk_min"] = df["avg_dist"] / WALK_SPEED / 60


   return df
