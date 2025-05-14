import os
import osmnx as ox
import pandas as pd


def bhBarsGraph():
    custom_filter = '["highway"~"primary|secondary|tertiary"]'
    G = ox.graph.graph_from_place(
        "belo horizonte - MG", custom_filter=custom_filter, network_type="walk"
    )

    gdf = ox.geocoder.geocode_to_gdf("belo horizonte - MG")
    geometry = gdf.geometry.iloc[0]
    features = ox.features.features_from_polygon(geometry, {"amenity": "bar"})

    feature_points = features.representative_point()
    nn = ox.distance.nearest_nodes(G, feature_points.x, feature_points.y)

    useful_tags = ["geometry", "name"]
    for node, feature in zip(nn, features[useful_tags].to_dict(orient="records")):
        feature = {k: v for k, v in feature.items() if pd.notna(v)}
        G.nodes[node].update({"bar": feature})

    return G


def getNodeFromBarName(G, bar_name):
    for node, data in G.nodes(data=True):
        if "bar" in data and data["bar"].get("name") == bar_name:
            return node
    return None


def getShortestPath(G, start_bar, end_bar):
    start_node = getNodeFromBarName(G, start_bar)
    end_node = getNodeFromBarName(G, end_bar)
    if start_node is None or end_node is None:
        raise ValueError("One or both bar names not found in the graph.")

    path = ox.shortest_path(G, orig=start_node, dest=end_node, weight="length")
    path_length = sum(
        min(G.get_edge_data(u, v).values(), key=lambda d: d["length"])["length"]
        for u, v in zip(path[:-1], path[1:])
    )

    return path, path_length


graph = bhBarsGraph()
shortest_path = getShortestPath(graph, "Druida Mix", "Morrito do Mato")
fig, ax = ox.plot_graph_route(
    graph, shortest_path, route_linewidth=3, node_size=0, bgcolor="white"
)
