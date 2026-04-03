import networkx as nx
import osmnx as ox
# print(ox.__version__)

Name = "Almere"

ox.settings.bidirectional_network_types += "drive"
G = ox.graph_from_place(f"{Name}, Netherlands", simplify=True, network_type="drive")

ox.plot_graph(G, save=True, show=True, close=False, filepath=f'Graphs/{Name}.png')




