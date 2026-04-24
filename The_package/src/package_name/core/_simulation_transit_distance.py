"""
    This file contains all functions related to the simulation of the transit
    distance after removing <fraction> edges.
"""
# Imports
from package_name.core._classes import Database, Network
import package_name.utils.util_plotting as plot

def run_simulation(network:Network, database:Database, f: float,
                   gender=True, age=True, ethnicity=True, SES=True,
                   save_old_network=True, save_new_network=True,
                   color_new_network=True, save_bar_diagram=True,
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
    # Obtaining information, building database tables
    database.load_network(network)
    database.obtain_features()
    database.pre_process()
    database.create_pts_per_neighborhood()
    database.link_busses()

    # Run simulation
    database.calculate_distances_to_nearest_transit()

    # Get beforehand information
    dists_neighborhoods_t0 = database.get_dist_per_neighborhood()
    dem_grp_avg_t0 = database.get_demographic_average_distance()

    # Continue simulation
    database.remove_f_edges(f)
    database.move_transit_minimal()
    database.calculate_distances_to_nearest_transit()

    # Get resulting information
    dists_neighborhoods_t1 = database.get_dist_per_neighborhood()
    dem_grp_avg_t1 = database.get_demographic_average_distance()
    xs, ys = database.obtain_generated_pts()

    # Add points + lost data

    ###########################################################################
    # Visualization ###########################################################
    ###########################################################################

    city = database.city

    # Bar diagraph before transformation
    plot.plot_demographic_average_distance(df=dem_grp_avg_t0,
                                      title=f"{city} before transformation",
                                      storage_folder="results",
                                      name=f"{city} before transformation")

    # Bar diagraph after transformation
    plot.plot_demographic_average_distance(df=dem_grp_avg_t1,
                                      title=f"{city} after transformation",
                                      subtitle=f"Neighborhoods lost: {database.lost} ({round((database.lost / database.num_buurten) * 100, 2)})%",
                                      storage_folder="results",
                                      name=f"{city} after transformation")

    # Generated points
    plot.plot_points(xs, ys,
                     title='Generated points',
                     subtitle=f'Number of points: {xs.size}',
                     storage_folder='results',
                     name=f'generated points: {city}')



    # print("dists_neighborhoods_t0")
    # print(dists_neighborhoods_t0)
    # print()    # print("dists_neighborhoods_t1")
    # print(dists_neighborhoods_t1)
    # print()


