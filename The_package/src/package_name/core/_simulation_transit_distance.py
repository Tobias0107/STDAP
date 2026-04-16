"""
    This file contains all functions related to the simulation of the transit
    distance after removing <fraction> edges.
"""
# Imports 
from _classes import Database, Network


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
    """
    
    


