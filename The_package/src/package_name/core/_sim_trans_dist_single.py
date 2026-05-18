"""
    This file contains all functions related to the simulation of the transit
    distance after removing <fraction> edges.
"""
# Imports
import networkx as nx
import geopandas as gpd
from package_name.core._classes import Database, Network
import package_name.utils.util_plotting as plot

def run_simulation(network:Network, database:Database, f: float, use_population: bool,
                   use_amenity: bool, simple_move: bool, blank_slate: bool,
                   print_progress: bool, saving_dir: str, svg: bool):
    """
        ### Expects:
            - network == Network(city)
            - database == Database(csv, geopackage)
            - database.set_city(city) called
            - network.city == database.city
        ### Parameters:
            - network (Network)
            - database (Database)
            - f (float):\n
                fraction of the car-accessible street length to transform to pedestrian
            - use_population (bool):\n
                If true, factors in the population when pedestrianizing. If False, use_amenity should be True.
            - use_amenity (bool):\n
                If true, factors in the amenity when pedestrianizing. If False, use_population should be True.
            - simple_move (bool):\n
                If true, uses the minimal/iterative method to move transit stops. simple_move xor blank_slate should be true
            - blank_slate (bool):\n
                If true, uses the blank-slate method to move transit stops. simple_move xor blank_slate should be true
            - print_progress: \n
                If True: Prints the progress of the simulation to stdout. As simulations can take
                a long time this is highly recommended.
            - saving_dir: \n
                The directory to save the results (if any).
            - svg: \n
                If True: uses svg format for results, png otherwise.
        ### Returns:
            - The average results per demographic group in the form of a dictionary
        ### Side effects:
            - Removes edges from network
            - Adds tables to database
            - Creates files containing visualizations
    """

    if print_progress: print(f"\n\nRunning single fraction pedestrianization simulation for {database.city}\n\n")

    # Storing original network (for difference network)
    if print_progress: print("Storing original network (for difference network)")
    G_original = network.graph_drive.copy()
    edges_t0 = set(network.graph_drive.edges(keys=True))

    # Obtaining information, building database tables
    if print_progress: print("Loading city network into database")
    database.load_network(network)
    if print_progress: print("Obtaining city amenities and public transit")
    database.obtain_features()
    if print_progress: print("Pre-processing network")
    database.pre_process()
    if print_progress: print("Creating points for every neighborhood")
    database.create_pts_per_neighborhood()
    if print_progress: print("Linking bus_stations to the network")
    database.link_busses()
    if print_progress: print("Storing pre-simulation bus-stop locations")
    bus_xs_t0, bus_ys_t0 = database.get_transit_pts()

    # Run simulation
    if print_progress: print("Calculating walking distances to public transit")
    database.calculate_distances_to_nearest_transit()

    # Get beforehand information
    if print_progress: print("Averaging distance to transit per neighborhood beforehand")
    dists_neighborhoods_t0 = database.get_dist_per_neighborhood()
    if print_progress: print("Averaging distance per demographic group beforehand")
    dem_grp_avg_t0 = database.get_demographic_average_distance()

    # Continue simulation
    if print_progress: print(f"Removing {f * 100}% of the driving network length")
    database.remove_f_edges(f, use_population, use_amenity)
    if print_progress: print("Moving transit")
    if simple_move: database.move_transit_minimal()
    elif blank_slate: database.move_transit_blank_slate()
    if print_progress: print("Re-calculating distances to public transit")
    database.calculate_distances_to_nearest_transit()

    # Get resulting information (basic)
    if print_progress: print("Averaging distance to transit per neighborhood afterwards")
    dists_neighborhoods_t1 = database.get_dist_per_neighborhood()
    if print_progress: print("Averaging distance per demographic group afterwards")
    dem_grp_avg_t1 = database.get_demographic_average_distance()

    # Get specific information
    if print_progress: print("Retrieving generated points (for visualization)")
    xs, ys = database.obtain_generated_pts()
    if print_progress: print("Creating difference network")
    edges_t1 = set(network.graph_drive.edges(keys=True))
    G_difference = G_original.edge_subgraph(edges_t0 - edges_t1).copy()
    if print_progress: print("Retrieving population and amenity distribution")
    pop_dist = database.get_population_distribution()
    amenity_xs, amenity_ys = database.get_amenity_pts()
    if print_progress: print("Retrieving after-simulation bus-stop locations")
    bus_xs_t1, bus_ys_t1 = database.get_transit_pts()

    ###########################################################################
    # Visualization ###########################################################
    ###########################################################################

    city = database.city

    # Bar diagraph before pedestrianization
    if print_progress: print("Plotting demographic average distance before pedestrianization")
    plot.bar_demographic_average_distance(df=dem_grp_avg_t0,
                                      title=f"Average distance per demographic group before pedestrianization: {city}",
                                      storage_folder=saving_dir,
                                      name=f"Average distance per demographic group  before pedestrianization",
                                      svg=svg)

    # Bar diagraph after pedestrianization
    if print_progress: print("Plotting demographic average distance after pedestrianization")
    plot.bar_demographic_average_distance(df=dem_grp_avg_t1,
                                      title=f"Average distance per demographic group after pedestrianization: {city}",
                                      subtitle=f"Neighborhoods lost: {database.lost} ({round((database.lost / database.num_buurten) * 100, 2)})%",
                                      storage_folder=saving_dir,
                                      name=f"Average distance per demographic group after pedestrianization",
                                      svg=svg)

    # Generated points
    if print_progress: print("Plotting all generated points")
    plot.plot_points(xs, ys,
                     title=f'Generated points: {city}',
                     subtitle=f'Number of points: {xs.size}\nNeighborhoods lost: {database.lost} ({round((database.lost / database.num_buurten) * 100, 2)})%',
                     storage_folder=saving_dir,
                     name=f'Generated points',
                     svg=svg)

    # Amenities
    if print_progress: print("Plotting all generated points")
    plot.plot_points(amenity_xs, amenity_ys,
                     title=f'Amenities: {city}',
                     subtitle=f'Number of amenities: {amenity_xs.size}',
                     storage_folder=saving_dir,
                     name=f'Amenities',
                     svg=svg)

    # Bus stops before and after
    if print_progress: print("Plotting pre-pedestrianization bus-stops")
    plot.plot_points(bus_xs_t0, bus_ys_t0,
                     title=f'bus-stops before pedestrianization: {city}',
                     subtitle=f'Number of stops: {bus_xs_t0.size}',
                     storage_folder=saving_dir,
                     name=f'bus-stops before pedestrianization',
                     svg=svg)
    if print_progress: print("Plotting after-pedestrianization bus-stops")
    plot.plot_points(bus_xs_t1, bus_ys_t1,
                     title=f'bus-stops after pedestrianization: {city}',
                     subtitle=f'Number of stops: {bus_xs_t1.size}',
                     storage_folder=saving_dir,
                     name=f'bus-stops after pedestrianization',
                     svg=svg)


    # # Population distribution
    if print_progress: print("Plotting population-density distribution network")
    plot.colored_network(pop_dist, '',
                         data_col_name='density',
                         title=f"Population-density distribution: {city}",
                         subtitle='%',
                         storage_folder=saving_dir,
                         name=f"Population-density distribution",
                         svg=svg,
                         show_graph=False,
                         force_linear=True)


    # Bar diagraphs of distances per neighborhood beforehand
    if print_progress: print("Plotting distances per neighborhood beforehand (bar diagraph)")
    plot.bar_dist_per_neighborhood(dists_neighborhoods_t0,
                                    title=f"Neighborhood distances (m) before pedestrianization: {city}",
                                    subtitle='',
                                    storage_folder=saving_dir,
                                    name=f"Neighborhood distances before pedestrianization",
                                    svg=svg)

    # Bar diagraphs of distances per neighborhood afterwards
    if print_progress: print("Plotting distances per neighborhood afterwards (bar diagraph)")
    plot.bar_dist_per_neighborhood(dists_neighborhoods_t1,
                                    title=f"Neighborhood distances (m) after pedestrianization: {city}",
                                    subtitle='',
                                    storage_folder=saving_dir,
                                    name=f"Neighborhood distances after pedestrianization",
                                    svg=svg)

    # both networks beforehand
    if print_progress: print("Creating colored graphs before pedestrianization: car-accessible")
    plot.colored_network(dists_neighborhoods_t0, network.graph_drive,
                         data_col_name='avg_dist',
                         title=f"Car-accessible network before pedestrianization: {city}",
                         subtitle='+ distance',
                         storage_folder=saving_dir,
                         name=f"Car-accessible network before pedestrianization",
                         svg=svg)

    if print_progress: print("Creating colored graphs before pedestrianization: pedestrian")
    plot.colored_network(dists_neighborhoods_t0, network.graph_pedestrian,
                         data_col_name='avg_dist',
                         title=f"Pedestrian network before pedestrianization: {city}",
                         subtitle='+ distance',
                         storage_folder=saving_dir,
                         name=f"Pedestrian network before pedestrianization",
                         svg=svg)

    # both networks after pedestrianization
    if print_progress: print("Creating colored graphs after pedestrianization: car-accessible")
    plot.colored_network(dists_neighborhoods_t1, network.graph_drive,
                         data_col_name='avg_dist',
                         title=f"Car-accessible network after pedestrianization: {city}",
                         subtitle='+ distance',
                         storage_folder=saving_dir,
                         name=f"Car-accessible network after pedestrianization",
                         svg=svg)

    if print_progress: print("Creating colored graphs after pedestrianization: pedestrian")
    plot.colored_network(dists_neighborhoods_t1, network.graph_pedestrian,
                         data_col_name='avg_dist',
                         title=f"Pedestrian network after pedestrianization: {city}",
                         subtitle='+ distance',
                         storage_folder=saving_dir,
                         name=f"Pedestrian network after pedestrianization",
                         svg=svg)

    # The difference between the two (Only if f != 0.0)
    if f > 0.001:
        if print_progress: print("Creating colored graphs about the difference before and after")
        dists_neighborhoods_t1['avg_dist'] = dists_neighborhoods_t1['avg_dist'] - dists_neighborhoods_t0['avg_dist']
        plot.colored_network(dists_neighborhoods_t1, G_difference,
                            data_col_name='avg_dist',
                            title=f"Pedestrianized network: {city}",
                            subtitle='+ increased distance',
                            storage_folder=saving_dir,
                            name=f"Pedestrianized network",
                            svg=svg)

    return dem_grp_avg_t1
