from shapely.geometry import Point
import networkx as nx
from haversine import haversine
from MultiDiGraphConvertor import convert_MultiDi_to_Simple
from BufferedGraph import *

'''
    @input:     The MultiDiGraph, coordinate, buffer size
    @output:    Returns list of nodes in that subgraph

    The function create a buffer around the coordinate with given buffer_size and return the list of nodes lies in the
    subgraph network created around the coordinate
'''


def assign_tuple(g, coord, buffer_size):
    geometry = Point(coord[1], coord[0])
    new_g = combine_network_buffer(g, geometry, buffer_size)
    print new_g.nodes
    return list(new_g.nodes)


'''
    @input:     The MultiDiGraph, start and end coordinates, buffer size of graph and point
    @output:    Returns all the different path from start to end coordinates and new graph of given buffer size

    The function get list of the start and end coordinate which lies in the subgraph created around that coordinate
    with given buffer. Iterate over the list of coordinates and check if there is path exist from start to end, if it
    does then calculate the shortest path from those coordinates and save it into dictionary along with the distance.
'''


def find_shortest_paths(g, start_tuple, end_tuple, graph_buffer, point_buffer):
    geometry = Point(start_tuple[1], start_tuple[0])
    start_tuples = assign_tuple(g, start_tuple, point_buffer)
    end_tuples = assign_tuple(g, end_tuple, point_buffer)

    buffered_graph = combine_network_buffer(g, geometry, graph_buffer)
    nodes = list(buffered_graph.nodes)

    path_dict = {}
    for start_tuple in start_tuples:

        if start_tuple in nodes:
            for end_tuple in end_tuples:
                if end_tuple in nodes:
                    if nx.has_path(buffered_graph, start_tuple, end_tuple) and start_tuple != end_tuple:
                        shortest_distance = nx.dijkstra_path_length(buffered_graph, start_tuple, end_tuple,
                                                                    weight='weight')
                        shortest_path = nx.shortest_path(buffered_graph, start_tuple, end_tuple, weight='weight')
                        path_dict[shortest_distance] = shortest_path

    return path_dict, buffered_graph

''''
    @input:     The MultiDiGraph, alpha, buffer size of the graph and the point, start & end coordinates and
                breakpoint upper counter to stop loop
    @output:    Returns the number of different paths

    The function return the list of total different paths which is alpha times the shortest path. It get the list of
    all the path from start to end coordinate and check if the distance of that particular path is alpha times the
    shortest path. If it is less than or equal to it then increment the counter
'''


def alpha_times_shortestpath(g, alpha, graph_buffer, point_buffer, start_tuple, end_tuple, break_point):
    shortest_paths, buffered_graph = find_shortest_paths(g, start_tuple, end_tuple, graph_buffer, point_buffer)
    total_paths = 0

    if len(shortest_paths) >= 1:
        shortest_dis = min(shortest_paths.keys())
        shortest_path = shortest_paths[shortest_dis]
        new_start_coord = shortest_path[0]
        new_end_coord = shortest_path[len(shortest_path)-1]

        all_paths = nx.shortest_simple_paths(convert_MultiDi_to_Simple(buffered_graph), source=new_start_coord,
                                             target=new_end_coord, weight='weight')

        flag = True
        path_list = []
        nodes_in_path = []

        for path in all_paths:
            if total_paths >= break_point:
                break

            total_distance = 0
            for index in range(1, len(path)):
                if nx.has_path(buffered_graph, path[index - 1], path[index]):
                    total_distance += haversine(path[index - 1], path[index])
                    if total_distance > (alpha * shortest_dis):
                        flag = False
                        break

            if flag or (total_distance <= (alpha * shortest_dis)):
                total_paths += 1
                path_list.append(total_distance)
                nodes_in_path.append(len(path))

            if not flag:
                break

    return total_paths
