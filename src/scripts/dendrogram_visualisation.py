import logging
import networkx as nx
import os
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.algorithms.traversal.depth_first_search import dfs_tree
from dendrogram_tools import dend_json_2_nodes_n_edges
from template_generation_utils import read_dendrogram_tree, index_dendrogram, generate_dendrogram_tree
from marker_tools import read_marker_file
from nomenclature_tools import nomenclature_2_nodes_n_edges

TAXON = "CS202002013"
# TAXON = "CS201912132"

NODE_LABEL_DISPLACEMENT = 1200

NODE_Y_DISPLACEMENT = 300

GAP_BETWEEN_LEAFS = 500

INTERMEDIATE_NODE_SIZE = 300

LEAF_NODE_SIZE = 50

PATH_DEND_JSON = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/" + TAXON + ".json")

PATH_NMN_TABLE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/nomenclature_table_CCN202002013.csv")

PATH_MARKERS = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../markers/" + TAXON + "_markers.tsv")

CLUSTER_ORDER = ["Lamp5", "Sncg", "Vip", "Sst", "Pvalb", "L2", "L4", "L5", "L6", "Meis", "OPC", "Astro", "Oligo",
                 "Endo", "VLMC", "SMC", "Peri", "Micro", "PVM"]


def visualise_tree(root=None, exact_order=True):
    # tree = read_dendrogram_tree(PATH_DEND_JSON)
    dend = nomenclature_2_nodes_n_edges(PATH_NMN_TABLE)
    tree = generate_dendrogram_tree(dend)

    if root is not None:
        tree = dfs_tree(tree, root)
    marker_expressions = read_marker_file(PATH_MARKERS)

    add_label_metadata(tree)
    node_colors, node_labels, node_sizes, pos = decorate_nodes(marker_expressions, tree)

    all_leafs = [x for x in tree.nodes(data=True) if tree.out_degree(x[0]) == 0]

    position_leaf_nodes(all_leafs, exact_order, pos)
    position_intermediate_nodes(all_leafs, pos, tree)

    # nx.draw_networkx(tree, pos, node_color=color_map, with_labels=False, arrows=False)
    nx.draw_networkx_nodes(tree, pos, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_edges(tree, pos, arrows=True, connectionstyle="arc3,rad=0.1")
    text = nx.draw_networkx_labels(tree, pos, node_labels, font_size=7)
    rotate_leaf_labels(text)

    plt.show()


def position_leaf_nodes(all_leaves, exact_order, pos):
    if exact_order:
        # sort by accession_id increasing
        leaves = list(all_leaves)
        list.sort(leaves, key=lambda node: int(str(node[0]).replace(TAXON + "_", "")))
        leaf_order = list()
        for node in leaves:
            leaf_order.append(node[1]["label"])

        print(leaf_order)
    else:
        leaf_order = CLUSTER_ORDER

    min_depth = get_min_depth(all_leaves, pos)
    last_x = 0
    for cluster in leaf_order:
        last_x = position_cluster_leafs(cluster, pos, all_leaves, min_depth, last_x)


def position_cluster_leafs(cluster, pos, all_leafs, min_depth, last_x=2):
    cluster_leafs = [x for x in all_leafs if x[1]["label"].startswith(cluster)]
    if len(cluster_leafs) == 0:
        logging.error("Node '" + cluster + "' that exists in reference order, not exists in the dendrogram.")
        return last_x
    cluster_leafs = sorted(cluster_leafs, key=lambda cluster_leaf: pos[cluster_leaf[0]][0])

    for leaf in cluster_leafs:
        # print(leaf[0]+"   "+str(last_x))
        pos[leaf[0]] = (last_x, min_depth)
        last_x += GAP_BETWEEN_LEAFS

    return last_x


def add_label_metadata(tree):
    # out = dend_json_2_nodes_n_edges(PATH_DEND_JSON)
    out = nomenclature_2_nodes_n_edges(PATH_NMN_TABLE)
    dend_dict = index_dendrogram(out)
    for node in tree.nodes(data=True):
        dend_node = dend_dict[node[0]]
        if "cell_set_preferred_alias" in dend_node:
            node[1]["label"] = dend_node["cell_set_preferred_alias"]


def decorate_nodes(marker_expressions, tree):
    labels = {}
    color_map = []
    node_sizes = []
    for node in tree.nodes(data=True):
        if tree.out_degree(node[0]) == 0:
            node_id = str(node[0]).replace(TAXON + "_", "")
            labels[node[0]] = node[1]["label"] + " (" + node_id + ")"
            node_sizes.append(LEAF_NODE_SIZE)
        else:
            labels[node[0]] = str(node[0]).replace(TAXON, "")
            node_sizes.append(INTERMEDIATE_NODE_SIZE)

        # nodes that also exist in the marker file will be displayed as red, others as blue
        if str(node[0]) in marker_expressions.keys():
            # light red
            color_map.append('#F08080')
        else:
            # sky blue
            color_map.append('#00BFFF')
    plt.title(TAXON)
    pos = graphviz_layout(tree, prog='dot')
    return color_map, labels, node_sizes, pos


def position_intermediate_nodes(all_leafs, pos, tree):
    intermediate_nodes = [x for x in tree.nodes(data=True) if x not in all_leafs]
    intermediate_nodes = sorted(intermediate_nodes, key=lambda node: pos[node[0]][1])
    for node in intermediate_nodes:
        min_x = 99999
        max_x = 0
        max_y = 0
        descendants = tree.successors(node[0])
        for descendant in descendants:
            if pos[descendant][0] > max_x:
                max_x = pos[descendant][0]
            if pos[descendant][0] < min_x:
                min_x = pos[descendant][0]
            if pos[descendant][1] > max_y:
                max_y = pos[descendant][1]

        pos[node[0]] = ((min_x + max_x) / 2, max_y + NODE_Y_DISPLACEMENT)

    fix_intemediate_overlaps(intermediate_nodes, pos)


def fix_intemediate_overlaps(intermediate_nodes, pos, changed=False):
    intermediate_nodes = sorted(intermediate_nodes, key=lambda node: pos[node[0]][0])

    previous_x = -1000
    previous_y = -1000
    for node in intermediate_nodes:
        if previous_y - pos[node[0]][1] < 50:
            if pos[node[0]][0] - previous_x < INTERMEDIATE_NODE_SIZE:
                displacement = INTERMEDIATE_NODE_SIZE + 200 - (pos[node[0]][0] - previous_x)
                pos[node[0]] = (pos[node[0]][0] + displacement, pos[node[0]][1])
                changed = True
        previous_x = pos[node[0]][0]
        previous_y = pos[node[0]][1]

    if changed:
        fix_intemediate_overlaps(intermediate_nodes, pos)


def rotate_leaf_labels(text):
    for node, t in text.items():
        if not str(t._text).startswith("_"):
            t.set_rotation('vertical')
            t._y = t._y - NODE_LABEL_DISPLACEMENT
            t._verticalalignment = 'right'


def get_min_depth(all_leafs, pos):
    min_depth = 99999
    for node in all_leafs:
        # print(str(pos[node[0]][0]))
        if pos[node[0]][1] < min_depth:
            min_depth = pos[node[0]][1]
    return min_depth


visualise_tree()
#visualise_tree("CS202002013_123")
#visualise_tree("CS202002013_179")