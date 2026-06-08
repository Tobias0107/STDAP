"""
    All the plotting related util functions
"""

import osmnx as ox
import networkx as nx
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
import os
import numpy as np

from STDAP.config.settings import get_settings
settings = get_settings()


def bar_demographic_average_distance(df, title='Average Distance per Group', subtitle='', storage_folder='.', name='dist_per_dem_grp', svg=True):
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
        - svg:\n
            If True: saves bar diagraph in svg format, png otherwise.
    ### Returns
        - None
    ### Side-effects
        - Stores a svg/png of the plot on given location.
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

    if svg:
        fig.savefig(os.path.join(storage_folder, name + '.svg'), format='svg')
    else:
        fig.savefig(os.path.join(storage_folder, name + '.png'), format='png', dpi=settings.png_dpi)
    plt.close(fig)


def plot_points(xs: np.ndarray, ys: np.ndarray, title='', subtitle='', storage_folder='.', name='plotted_points', svg=False):
    """
    ### Parameters
        - xs, ys: \n
            Respectively the x and y coordinates of the points in the form of a numpy array.
        - title: \n
            The title of the picture
        - subtitle: \n
            The subtitle of the picture
        - storage_folder: \n
            The folder to store the bar diagraph.\
        - name: \n
            The name of the bar diagraph
        - svg:\n
            If True: saves bar diagraph in svg format, png otherwise.
    ### Returns
        - None
    ### Side-effects
        - Stores a svg/png of the plot on given location.
    """
    # Create figure
    fig = plt.figure()
    plt.scatter(xs, ys, s=0.5, edgecolors='none')
    # plt.axis('off')

    # Labels
    plt.suptitle(title)
    plt.title(subtitle, fontsize=8)

    # Make sure directory exists
    if not os.path.isdir(storage_folder):
        os.makedirs(storage_folder)

    # Save figure .svg if small, .png if large
    if svg:
        fig.savefig(os.path.join(storage_folder, name + '.svg'), format='svg')
    else:
        fig.savefig(os.path.join(storage_folder, name + '.png'), format='png', dpi=settings.png_dpi)
    plt.close(fig)


def bar_dist_per_neighborhood(df, title='', subtitle='', storage_folder='.', name='dist_per_neighborhood', svg=True):
    """
    ### Description
        This function creates a bar diagraph of the distance per neighborhood
        as is returned by the database.get_dist_per_neighborhood()
        Creates a red horizontal line for the average.
    ### Parameters:
        - df: \n
            The dataframe, as is returned by the database.get_dist_per_neighborhood()
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
        - Stores a svg/png of the plot on given location.
    """

    # Creating bar diagraph
    fig, ax = plt.subplots()
    ax.bar(df["neighborhood"], df["avg_dist"], color='lightgrey', rasterized=True)

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

    if svg:
        fig.savefig(os.path.join(storage_folder, name + '.svg'))
    else:
        fig.savefig(os.path.join(storage_folder, name + '.png'), format='png', dpi=settings.png_dpi)
    plt.close(fig)


def colored_network(DataFrame: gpd.GeoDataFrame, graph, data_col_name, title='', subtitle='', colorbar_label='', storage_folder='.', name='colored_network', svg=True, force_linear=False, show_graph=True):
    """
    ### Parameters:
        - DataFrame: \n
            The dataframe (neighborhoods, data_col_name) used to color the network.
            May be a GeoDataFrame or DataFrame
        - graph: \n
            The network to use as the base of the network image
        - title: \n
            The title of the figure
        - subtitle: \n
            The subtitle of the figure
        - storage_folder: \n
            The folder to store the bar diagraph.\
        - name: \n
            The name of the bar diagraph (file)
        - svg: \n
            If True: Uses svg format. Otherwise png format.
        - show_graph: \n
            If False: Doesn't show graph in image.
    ### Returns
        - None
    ### Side-effects
        - Stores a svg/png of the plot on given location.
    """
    # Create Colormap
    vals = DataFrame[data_col_name]
    v_min, v_max = vals.min(), vals.max()
    if force_linear:
        norm = plt.Normalize(v_min, v_max) # type: ignore
    else:
        norm = settings.color_normalization(v_min, v_max) # type: ignore
    cmap = mpl.colormaps[settings.colormap]

    # Add use Colormap to determine the color for every neighborhood
    DataFrame['color'] = DataFrame[data_col_name].apply(lambda x: cmap(norm(x)))

    # Plot the neighborhood colors
    fig, ax = ox.plot_footprints(DataFrame, color=DataFrame['color'], edge_color='black', alpha=0.4, show=False, close=False) # type: ignore

    # Plot the network
    if show_graph:
        (b1, b2, b3, b4) = DataFrame.total_bounds
        fig, ax = ox.plot_graph(graph, ax=ax, node_size=0, edge_color='white', edge_linewidth=0.5, show=False, close=False, bbox=(b1, b2, b3, b4))

    # Create the color-bar used for the legenda
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation='vertical', pad=0.02, shrink=0.8)

    # Create the labels for the legenda
    u = np.linspace(0, 1, num=settings.legend_num_labels)
    tick_values = norm.inverse(u).tolist()
    cbar.set_ticks(tick_values)
    cbar.set_ticklabels([str(int(x)) for x in tick_values])
    cbar.set_label(colorbar_label, fontsize=10)
    plt.suptitle(title)
    plt.title(subtitle, fontsize=8)

    # Save bar-diagraph
    if not os.path.isdir(storage_folder):
        os.makedirs(storage_folder)

    if svg:
        fig.savefig(os.path.join(storage_folder, name + '.svg'))
    else:
        fig.savefig(os.path.join(storage_folder, name + '.png'), dpi=settings.png_dpi)
    plt.close(fig)


def DataFrames(DataFrames: list[pd.DataFrame], x_col:str, y_col:str, label_col:str,
                   xlabel:str, ylabel:str, title='', subtitle='', storage_folder='.',
                   name='DataFrame', svg=True, multiple_figures=False):
    """
        ### Parameters:
        - DataFrames: \n
            The list of DataFrames to plot. The average over the list is taken.
        - x_col: \n
            The column name for the x-axis data
        - y_col: \n
            The column name for the y-axis data
        - label_col: \n
            The column name with the labels, data is grouped using this label column.
        - x_label: \n
            The label to give to the x-axis
        - y_label: \n
            The label to give to the y-axis
        - title: \n
            The title of the figure
        - subtitle: \n
            The subtitle of the figure
        - storage_folder: \n
            The folder to store the file.\
        - name: \n
            The name of the file to store
        - svg: \n
            If True: Uses svg format. Otherwise png format.
        - multiple_figures: \n
            Generate figures for every individual label also.
    ### Returns
        - None
    ### Side-effects
        - Stores a svg/png of the plot on given location.
    """
    combined = pd.concat(DataFrames, ignore_index=True)
    avg_df = (
        combined
        .groupby([label_col, x_col], as_index=False)[y_col]
        .mean()
    )
    DataFrame(avg_df, x_col, y_col, label_col, xlabel, ylabel, title, subtitle, storage_folder,
              name, svg, multiple_figures)


def DataFrame(DataFrame, x_col:str, y_col:str, label_col:str,
                   xlabel:str, ylabel:str, title='', subtitle='', storage_folder='.',
                   name='DataFrame', svg=True, multiple_figures=False):
    """
    ### Parameters:
        - DataFrame: \n
            The DataFrame to plot
        - x_col: \n
            The column name for the x-axis data
        - y_col: \n
            The column name for the y-axis data
        - label_col: \n
            The column name with the labels, data is grouped using this label column.
        - x_label: \n
            The label to give to the x-axis
        - y_label: \n
            The label to give to the y-axis
        - title: \n
            The title of the figure
        - subtitle: \n
            The subtitle of the figure
        - storage_folder: \n
            The folder to store the file.\
        - name: \n
            The name of the file to store
        - svg: \n
            If True: Uses svg format. Otherwise png format.
        - multiple_figures: \n
            Generate figures for every individual label also.
    ### Returns
        - None
    ### Side-effects
        - Stores a svg/png of the plot on given location.
    """
    
    # Shared code
    if not os.path.isdir(storage_folder):
            os.makedirs(storage_folder)


    # Creating the plot basis (one plot)
    fig, ax = plt.subplots()
    for label, grp in DataFrame.groupby(label_col):
        grp = grp.sort_values(x_col)
        ax.plot(
            grp[x_col],
            grp[y_col],
            label=label
        )

    # Set title and labels
    plt.suptitle(title)
    plt.title(subtitle, fontsize=8)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    fig.tight_layout()

    # Save plot
    if svg:
        fig.savefig(os.path.join(storage_folder, name + '.svg'))
    else:
        fig.savefig(os.path.join(storage_folder, name + '.png'), dpi=settings.png_dpi)
    plt.close(fig)

    if multiple_figures:
        for label, grp in DataFrame.groupby(label_col):

            # Create plot basis (single line, single figure)
            fig, ax = plt.subplots()
            ax.plot(
                grp[x_col],
                grp[y_col],
                label=label
            )

            # Set title and labels
            plt.suptitle(title)
            plt.title(subtitle, fontsize=8)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.legend()

            # Save plot
            if svg:
                fig.savefig(os.path.join(storage_folder, str(label) + name + '.svg'))
            else:
                fig.savefig(os.path.join(storage_folder, str(label) + name + '.png'), dpi=settings.png_dpi)
            plt.close(fig)
