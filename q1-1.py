import networkx as nx
import numpy as np
import queue
import matplotlib.pyplot as plt

# printing in nicer format
def print_nodes(graph):
    for n, d in graph.nodes(data=True):
        print(n, d)

def print_edges(graph):
    for u, v, d in graph.edges(data=True):
        print('({}, {})'.format(u, v), d)

# load adj matrix
G = nx.from_numpy_matrix(np.loadtxt("input.txt", skiprows=1))
G_org = G.copy()
nx.draw_networkx(G, with_labels=True)
decompositions = []

print("Network decomposition:")
while G.edges():
    nx.set_edge_attributes(G, 0, "betweeness")
    # for each node in the graph
    for n in G.nodes():

        # create a copy of graph G
        T = G.copy()

        # initate for BFS
        nx.set_node_attributes(T, "undiscovered", "status")
        nx.set_node_attributes(T, {n: "discovered"}, "status")
        nx.set_node_attributes(T, {n: 0}, "d")
        nx.set_node_attributes(T, {n: []}, "pred")
        nx.set_node_attributes(T, 0, "n_paths")
        nx.set_node_attributes(T, {n: 1}, "n_paths")

        # queue the root node
        q = queue.Queue()
        q.put(n)

        # BFS of current nodes
        while not q.empty():
            u = q.get()
            # print(u)
            d_u = T.nodes[u]["d"]
            # visit neighbours of u
            for v in T.neighbors(u):
                if T.nodes[v]["status"] == "undiscovered":
                    nx.set_node_attributes(T, {v: "discovered"}, "status")
                    nx.set_node_attributes(T, {v: d_u+1}, "d")
                    # set u as predecesor of v
                    nx.set_node_attributes(T, {v: [u]}, "pred")
                    nx.set_node_attributes(T, {v: T.nodes()[u]["n_paths"]}, "n_paths")
                    q.put(v)

                # set u as predecesor of v if distance is not greater than current shortest path
                elif T.nodes[v]["status"] == "discovered":
                    if T.nodes[v]["d"] >= d_u+1:
                        pred_v = T.nodes[v]["pred"]
                        pred_v.append(u)
                        nx.set_node_attributes(T, {v: pred_v}, "pred")
                        nx.set_node_attributes(T, {v: T.nodes()[v]["n_paths"]+T.nodes()[u]["n_paths"]}, "n_paths")

            # set status of u as finished   
            nx.set_node_attributes(T, {u: "finished"}, "status")
            
        # remove nodes that are not reachable from current node
        T.remove_nodes_from([n for n in T.nodes if T.nodes()[n]["n_paths"] == 0])
        # print_nodes(T)
        # print("-----------")

        # Compute betweeness
        nx.set_node_attributes(T, 1, "flow")
        # from nodes furthest from source
        for node, data in sorted(T.nodes(data=True), key=lambda u: u[1]["d"], reverse=True):
            # print(node)
            if len(data["pred"]) == 0:
                break
            # total flow of predecesors 
            flow_preds = 0.0
            for u in data["pred"]:
                flow_preds += T.nodes()[u]["n_paths"]
            # print(flow_preds)
            if flow_preds == 0:
                flow_preds = 1
            for u in data["pred"]:
                # split flows according to the number of shortest paths to the predecesors
                split = T.nodes()[node]["flow"] * T.nodes()[u]["n_paths"] / flow_preds
                nx.set_node_attributes(T, {u: T.nodes()[u]["flow"]+split}, "flow")
                nx.set_edge_attributes(G, {(node, u): G.edges()[(node, u)]["betweeness"]+split}, "betweeness")
            # for n, d in T.nodes(data=True):
            #     print(n, d)
            # print("----------------")

    # remove edges according to betweeness
    # print_edges(G)
    betweeness = nx.get_edge_attributes(G, 'betweeness')
    betweeness_max = max(betweeness.values())
    edges_to_rm = []
    for u, v, d in G.edges(data=True):
        if d["betweeness"] == betweeness_max:
            edges_to_rm.append((u, v))
    G.remove_edges_from(edges_to_rm)
    
    print([c for c in nx.connected_components(G)])
    decompositions.append(G.copy())

decomp_modularity = {}

# Modularity results
for decomp in decompositions:
    # print(decomp.edges())
    modularity = 0.0
    m = G_org.number_of_edges()
    for c in nx.connected_components(decomp):
        # print (c)
        for u in c:
            for v in c:
                a = 1 if decomp.has_edge(u, v) else 0
                # print(u, v, a)
                modularity += a - G_org.degree(u) * G_org.degree(v) / (2*m)
    modularity /= 2*m
    decomp_modularity[decomp] = modularity

    print('{} clusters: modularity {}'.format(nx.number_connected_components(decomp), modularity))

# Print optimal decomposition
opt_decocmp = max(decomp_modularity, key=decomp_modularity.get)
print('Optimal structire: ', [c for c in nx.connected_components(opt_decocmp)])

