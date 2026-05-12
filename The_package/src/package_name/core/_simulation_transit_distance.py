"""
    This file contains all functions related to the simulation of the transit
    distance after removing <fraction> edges.
"""
# Imports
import networkx as nx
from package_name.core._classes import Database, Network
import package_name.utils.util_plotting as plot

def run_simulation(network:Network, database:Database, f: float, use_population=True,
                   use_amenity=True, simple_move=True, blank_slate=False,
                   print_progress=True, saving_dir="results_sim_transit_dist/"):
    """
        ### Expects:
            - network == Network(city)
            - database == Database(csv, geopackage)
            - database.set_city(city) called
            - network.city == database.city
        ### Parameters:
            - network (Network)
            - database (Database)
            - f (float)\n
                fraction of the car-accessible streets to transform to pedestrian
            - gender: \n
                If True: displays simulation results for gender
            - age: \n
                If True: displays simulation results for age
            - ethnicity: \n
                If True: displays simulation results for ethnicity
            - SES: \n
                If True: displays simulation results for Social Economic Status (SES)
            - Save_old_network: \n
                If True: saves the network pre-transformation in png format
            - Save_new_network: \n
                If True: saves the network after transformation in png format
            - color_new_network: \n
                If True: gives colors to neighborhoods in the network based on the
                average calculated new distance one has to travel to transit.
                Red = Big increase (relative to other neighborhoods)
                Orange = Small increase (relative to other neighborhoods)
                Yellow = Practically remains the same
                Light green = Distance is slightly decreased
                Dark green = Distance is greatly decreased
            - save_bar_diagram: \n
                If True: Saves the average results per demographic group in the form of a bar
                diagram (png).
            - print_progress: \n
                If True: Prints the progress of the simulation to stdout. As simulations can take
                a long time this is highly recommended.
            - print_simulation_steps: \n
                If True: Prints the current simulation step to stdout. This can provide for more
                insight in the simulation progress.
            - saving_dir: \n
                The directory to save the results (if any).

        ### Returns:
            - The average results aper demographic group in the form of a dictionary
        ### Side effects:
            - Removes edges from network
            - Adds tables to database
            - Creates files containing visualizations
    """

    if print_progress: print(f"\nRunning simulation for {database.city}\n\n")

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
    database.move_transit_minimal()
    if print_progress: print("Re-calculating distances to public transit")
    database.calculate_distances_to_nearest_transit()

    # Get resulting information
    if print_progress: print("Averaging distance to transit per neighborhood afterwards")
    dists_neighborhoods_t1 = database.get_dist_per_neighborhood()
    if print_progress: print("Averaging distance per demographic group afterwards")
    dem_grp_avg_t1 = database.get_demographic_average_distance()
    if print_progress: print("Obtaining generated points (for visualization)")
    xs, ys = database.obtain_generated_pts()
    if print_progress: print("Creating difference network")
    edges_t1 = set(network.graph_drive.edges(keys=True))
    G_difference = G_original.edge_subgraph(edges_t0 - edges_t1).copy()
    if print_progress: print("Difference network:")
    if print_progress: print(G_difference)

    ###########################################################################
    # Visualization ###########################################################
    ###########################################################################

    city = database.city

    # Bar diagraph before transformation
    if print_progress: print("Plotting demographic average distance before transformation")
    plot.bar_demographic_average_distance(df=dem_grp_avg_t0,
                                      title=f"{city} before transformation",
                                      storage_folder=saving_dir,
                                      name=f"{city} before transformation")

    # Bar diagraph after transformation
    if print_progress: print("Plotting demographic average distance after transformation")
    plot.bar_demographic_average_distance(df=dem_grp_avg_t1,
                                      title=f"{city} after transformation",
                                      subtitle=f"Neighborhoods lost: {database.lost} ({round((database.lost / database.num_buurten) * 100, 2)})%",
                                      storage_folder=saving_dir,
                                      name=f"{city} after transformation")

    # Generated points
    if print_progress: print("Plotting all generated points")
    plot.plot_points(xs, ys,
                     title='Generated points',
                     subtitle=f'Number of points: {xs.size}',
                     storage_folder=saving_dir,
                     name=f'generated points: {city}')


    # Bar diagraphs of distances per neighborhood beforehand
    if print_progress: print("Plotting distances per neighborhood beforehand (bar diagraph)")
    plot.bar_dist_per_neighborhood(dists_neighborhoods_t0,
                                    title=f"Distances per neighborhood in {city} beforehand",
                                    subtitle='',
                                    storage_folder=saving_dir,
                                    name=f"Distances per neighborhood in {city} beforehand")

    # Bar diagraphs of distances per neighborhood afterwards
    if print_progress: print("Plotting distances per neighborhood afterwards (bar diagraph)")
    plot.bar_dist_per_neighborhood(dists_neighborhoods_t1,
                                    title=f"Distances per neighborhood in {city} afterwards",
                                    subtitle='',
                                    storage_folder=saving_dir,
                                    name=f"Distances per neighborhood in {city} afterwards")

    # both networks beforehand
    if print_progress: print("Creating colored graphs beforehand: car-accessible")
    plot.colored_network(dists_neighborhoods_t0, network.graph_drive,
                         title=f"Car-accessible network {city} beforehand",
                         subtitle='',
                         storage_folder=saving_dir,
                         name=f"Car-accessible network {city} beforehand")

    if print_progress: print("Creating colored graphs beforehand: pedestrian")
    plot.colored_network(dists_neighborhoods_t0, network.graph_pedestrian,
                         title=f"Pedestrian network {city} beforehand",
                         subtitle='',
                         storage_folder=saving_dir,
                         name=f"Pedestrian network {city} beforehand")

    # both networks afterwards
    if print_progress: print("Creating colored graphs afterwards: car-accessible")
    plot.colored_network(dists_neighborhoods_t1, network.graph_drive,
                         title=f"Car-accessible network {city} afterwards",
                         subtitle='',
                         storage_folder=saving_dir,
                         name=f"Car-accessible network {city} afterwards")

    if print_progress: print("Creating colored graphs afterwards: pedestrian")
    plot.colored_network(dists_neighborhoods_t1, network.graph_pedestrian,
                         title=f"Pedestrian network {city} afterwards",
                         subtitle='',
                         storage_folder=saving_dir,
                         name=f"Pedestrian network {city} afterwards")

    # The difference between the two
    if print_progress: print("Creating colored graphs about the difference before and after: car-accessible")
    dists_neighborhoods_t1['avg_dist'] = dists_neighborhoods_t1['avg_dist'] - dists_neighborhoods_t0['avg_dist']
    plot.colored_network(dists_neighborhoods_t1, G_difference,
                         title=f"Car-accessible network {city} difference",
                         subtitle='beforehand - afterwards',
                         storage_folder=saving_dir,
                         name=f"Car-accessible network {city} difference",
                         force_linear=True)

    if print_progress: print("Creating colored graphs about the difference before and after: pedestrian")
    plot.colored_network(dists_neighborhoods_t1, G_difference,
                         title=f"Pedestrian network {city} difference",
                         subtitle='beforehand - afterwards',
                         storage_folder=saving_dir,
                         name=f"Pedestrian network {city} difference",
                         force_linear=True)

    # Show population distribution


    # 


