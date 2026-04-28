"""
    All the plotting related util functions
"""

import osmnx as ox
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np


def bar_demographic_average_distance(df: pd.DataFrame, title='Average Distance per Group', subtitle='', storage_folder='.', name='dist_per_dem_grp'):
    """
    ### Description
        This function creates a bar diagraph of the demographic average distance dataframe
        as is returned by the database.get_demographic_average_distance()
        Creates a red horizontal line for the average.
    ### Parameters:
        - df: \n
            The dataframe, as is returned by the database.get_demographic_average_distance()
        - title: \n
            The title of the figure
        - subtitle: \n
            The subtitle of the figure
        - storage_folder: \n
            The folder to store the bar diagraph.\
        - name: \n
            The name of the bar diagraph (file)
    ### Returns
        - None
    ### Side-effects
        - Stores a svg of the plot on given location.
    """
    # Splitting average from dataframes
    avg = df.loc[df["dem_grp"] == "avg", "avg_dist"].iloc[0]
    df = df[df["dem_grp"] != "avg"]

    # Creating bar diagraph
    fig, ax = plt.subplots()
    ax.bar(df["dem_grp"], df["avg_dist"], color='lightgrey', rasterized=True)
    ax.axhline(y=avg, color='red')

    # Setting labels
    ax.set_xlabel("Demographic Groups")
    ax.set_ylabel("Average Distance")
    plt.suptitle(title)
    plt.title(subtitle, fontsize=8)
    ax.tick_params(axis='x', which='major', pad=5)
    plt.xticks(rotation=90)
    plt.tight_layout()

    ax.annotate(
        f"Average = {int(avg)}",
        xy=(1, avg),
        xytext=(-5, 5),
        xycoords=("axes fraction", "data"),
        textcoords="offset points",
        ha="right",
        va="bottom",
        color="red"
    )

    # Save bar-diagraph
    if not os.path.isdir(storage_folder):
        os.makedirs(storage_folder)

    fig.savefig(os.path.join(storage_folder, name + '.svg'))


def plot_points(xs: np.ndarray, ys: np.ndarray, title='Average Distance per Group', subtitle='', storage_folder='.', name='generated_points'):
    """
    ### Description
        This function plots the given points. The figure is stored in svg format by default.
        If the amount of points exceed 5000 the figure is stored in png format instead.
        (Due to performance considerations.)
    ### Parameters
        - df: \n
            The dataframe, as is returned by the database.get_demographic_average_distance()
        - storage_folder: \n
            The folder to store the bar diagraph.\
        - name: \n
            The name of the bar diagraph
    ### Returns
        - None
    ### Side-effects
        - Stores a svg of the plot on given location.
    """
    # Create figure
    fig = plt.figure()
    plt.scatter(xs, ys, s=0.5, edgecolors='none')

    # Labels
    plt.suptitle(title)
    plt.title(subtitle, fontsize=8)

    # Make sure directory exists
    if not os.path.isdir(storage_folder):
        os.makedirs(storage_folder)

    # Save figure .svg if small, .png if large
    if xs.size < 5000:
        fig.savefig(os.path.join(storage_folder, name + '.svg'), format='svg')
    else:
        fig.savefig(os.path.join(storage_folder, name + '.png'), format='png')


def bar_dist_per_neighborhood(df: pd.DataFrame, title='Average Distance per Neighborhood', subtitle='', storage_folder='.', name='dist_per_neighborhood'):
    """
    ### Description
        This function creates a bar diagraph of the distance per neighborhood
        as is returned by the database.get_demographic_average_distance()
        Creates a red horizontal line for the average.
    ### Parameters:
        - df: \n
            The dataframe, as is returned by the database.get_demographic_average_distance()
        - title: \n
            The title of the figure
        - subtitle: \n
            The subtitle of the figure
        - storage_folder: \n
            The folder to store the bar diagraph.\
        - name: \n
            The name of the bar diagraph (file)
    ### Returns
        - None
    ### Side-effects
        - Stores a svg of the plot on given location.
    """

    # Creating bar diagraph
    fig, ax = plt.subplots()
    ax.bar(df["regio"], df["avg_dist"], color='lightgrey', rasterized=True)

    # Setting labels
    ax.set_xlabel("Neighborhoods")
    ax.set_ylabel("Average Distances")
    plt.suptitle(title)
    plt.title(subtitle, fontsize=8)
    ax.set_xticklabels([])
    plt.tight_layout()


    # Save bar-diagraph
    if not os.path.isdir(storage_folder):
        os.makedirs(storage_folder)

    fig.savefig(os.path.join(storage_folder, name + '.svg'))
