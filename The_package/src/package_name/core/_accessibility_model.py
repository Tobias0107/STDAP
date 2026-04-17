"""
This file contains all functions related to computing accessibility
based on a gravity-based model using travel times.
"""
# Imports 
from _classes import Database, Network
import numpy as np

def run_accessibility(network: Network,
                      database: Database,
                      departure_time,
                      beta: float,
                      print_progress=True):
    """
    Computes accessibility per neighborhood using:
    A_i = sum_j O_j * exp(-beta * t_ij)
    """

    if print_progress:
        print("Starting accessibility computation...")

    # 1. Origins (cluster centers of neighborhoods)
    origins = _get_neighborhood_points(database)

    # 2. Destinations (neighborhood centroids or same set)
    destinations = _get_neighborhood_centroids(database)

    # 3. Travel times (t_ij)
    travel_times = _compute_travel_times(origins, destinations, departure_time)

    # 4. Opportunities (Oj)
    opportunities = _get_opportunities(database)

    # 5. Accessibility
    accessibility = _compute_accessibility(travel_times, opportunities, beta)

    return accessibility