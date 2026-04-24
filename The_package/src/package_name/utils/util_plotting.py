"""
    All the plotting related util functions
"""


import pandas as pd
import matplotlib.pyplot as plt
import os


def plot_demographic_average_distance(df: pd.DataFrame, title='Average Distance per Group', storage_folder='.', name='bar_diagraph'):
    """
    ### Description
        This function creates a bar diagraph of the demographic average distance dataframe
        as is returned by the database.get_demographic_average_distance()
        Creates a red horizontal line for the average.
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
    # Splitting average from dataframes
    avg = df.loc[df["dem_grp"] == "avg", "avg_dist"].iloc[0]
    df = df[df["dem_grp"] != "avg"]

    # Creating bar diagraph
    fig, ax = plt.subplots()
    ax.bar(df["dem_grp"], df["avg_dist"])
    ax.axhline(y=avg)

    # Setting labels
    ax.set_xlabel("Demographic Groups")
    ax.set_ylabel("Average Distance")
    ax.set_title(title)
    ax.tick_params(axis='x', which='major', pad=5)
    plt.xticks(rotation=90)
    plt.tight_layout()

    # Save bar-diagraph
    if not os.path.isdir(storage_folder):
        os.makedirs(storage_folder)

    fig.savefig(os.path.join(storage_folder, name + '.svg'))
