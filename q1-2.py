import networkx as nx
from mpl_toolkits.axes_grid1 import host_subplot
import matplotlib.pyplot as plt

prob = []

for e in range(4, 0, -1):
    for a in range(1, 10):
        prob.append(a / 10**e)
prob.append(1)

print(prob)

c = []
h = []

for p in prob:
    G = nx.watts_strogatz_graph(1000, 4, p, seed=0)
    c.append(nx.average_clustering(G))
    h.append(nx.average_shortest_path_length(G))

f_c = host_subplot(111)

f_h = f_c.twinx()

f_c.set_xlabel("Probability of Rewiring p")
f_c.set_ylabel("Clustering coefficient")
f_h.set_ylabel("Path length")

p1, = f_c.plot(prob, c, label="Average clustering coefficient c")
p2, = f_h.plot(prob, h, label="Average shortest path length h")

leg = plt.legend()

f_c.yaxis.get_label().set_color(p1.get_color())
leg.texts[0].set_color(p1.get_color())

f_h.yaxis.get_label().set_color(p2.get_color())
leg.texts[1].set_color(p2.get_color())

plt.xscale("log")

plt.show()