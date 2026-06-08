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

from package_name.config.settings import get_settings
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


def bar_demographic_average_distances(dfs:list[pd.DataFrame], title='Average Distance per Group',
                                      subtitle='', storage_folder='.', name='dist_per_dem_grp', svg=True):
    combined = pd.concat(dfs, ignore_index=True)
    avg_df = (
        combined
        .groupby(["dem_grp"], as_index=False)["avg_dist"]
        .mean()
    )
    bar_demographic_average_distance(avg_df, title, subtitle, storage_folder, name, svg)


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

def bar_dist_per_neigborhoods(DataFrames: list[pd.DataFrame], title='', subtitle='',
                              storage_folder='.', name='DataFrame', svg=True):
    combined = pd.concat(DataFrames, ignore_index=True)
    avg_df = (
        combined
        .groupby(["neighborhood"], as_index=False)["avg_dist"]
        .mean()
    )
    bar_dist_per_neighborhood(avg_df, title, subtitle, storage_folder, name, svg)



def colored_network(DataFrame: gpd.GeoDataFrame, graph, data_col_name, title='', subtitle='', colorbar_label='', storage_folder='.', name='colored_network', svg=True, force_linear=False, show_graph=True):
    """
    ### Parameters:
        - df: \n
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

def plot_t_walk_map(gdf, storage_folder="debug", name="t_walk", show=False):
    """
    ### Expected:
        - gdf contains geometry and avg_dist

    ### Parameters:
        - gdf:
            GeoDataFrame with neighborhood geometry
        - storage_folder:
            Folder to store plot
        - name:
            Output filename (without extension)
        - show:
            If True: display plot interactively

    ### Returns:
        - None

    ### Side-effects:
        - Saves plot to disk
        - Optionally displays plot
    """

    import os
    import matplotlib.pyplot as plt

    os.makedirs(storage_folder, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 10))

    gdf.plot(
        column="avg_dist",
        cmap="viridis",
        legend=True,
        ax=ax
    )

    plt.title("Average walking distance to transit (t_walk)")
    plt.axis("off")

    filepath = f"{storage_folder}/{name}.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")

    if show:
        plt.show()

    plt.close()

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

def attach_geometry_to_t_travel(database, df_avg):
    """
    Attach neighborhood geometry to avg travel time per origin

    ### Expected:
        - df_avg contains:
            - from_id
            - avg_travel_time

    ### Returns:
        - GeoDataFrame with geometry + avg_travel_time
    """

    import geopandas as gpd
    from shapely import wkb

    geom_df = database.conn.sql("""
        SELECT id, ST_AsWKB(geometry) AS geometry
        FROM Neighborhoods
    """).df()

    geom_df["geometry"] = geom_df["geometry"].apply(lambda x: wkb.loads(bytes(x)))

    gdf_geom = gpd.GeoDataFrame(
        geom_df,
        geometry="geometry",
        crs="EPSG:28992"
    )

    merged = df_avg.merge(
        gdf_geom,
        left_on="from_id",
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


def plot_t_travel_avg_map(gdf, storage_folder="debug", name="t_travel", show=False):
    """
    ### Purpose:
        - Visualize average travel time per neighborhood

    ### Expected:
        - GeoDataFrame with:
            - geometry
            - avg_travel_time

    ### Description:
        - Plots choropleth map of average travel time
    """

    import os
    import matplotlib.pyplot as plt

    os.makedirs(storage_folder, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 10))

    gdf.plot(
        column="avg_travel_time",
        cmap="viridis",
        legend=True,
        ax=ax
    )

    ax.set_title("Average Travel Time per Neighborhood")
    ax.axis("off")

    path = f"{storage_folder}/{name}.png"
    plt.savefig(path)

    if show:
        plt.show()

    plt.close()