import networkx as nx
from template_generation_utils import read_csv_to_dict, generate_dendrogram_tree


def nomenclature_2_nodes_n_edges(taxonomy_file_path):
    out = dict()
    out['nodes'] = []
    out['edges'] = set()

    child_cell_sets = list()
    headers, nomenclature_records = read_csv_to_dict(taxonomy_file_path, id_column_name='cell_set_accession')
    for node_cell_set_accession in nomenclature_records:
        record_dict = nomenclature_records[node_cell_set_accession]
        node = {prop: record_dict[prop] for prop in headers}
        out['nodes'].append(node)

        children_str = record_dict['child_cell_set_accessions']
        if children_str:
            children = set(children_str.strip().split('|'))
        else:
            children = {node_cell_set_accession}
        node = {"node_cell_set_accession": node_cell_set_accession, "children": children}
        child_cell_sets.append(node)

    sorted_child_cell_sets = sorted(child_cell_sets, key=lambda x: len(x["children"]))
    for child_cell_sets in sorted_child_cell_sets:
        parent_node = find_next_inclusive_node(sorted_child_cell_sets, child_cell_sets)
        if parent_node:
            out['edges'].add((child_cell_sets["node_cell_set_accession"], parent_node["node_cell_set_accession"]))

    fix_multi_inheritance_relations(out, sorted_child_cell_sets)
    return out


def find_next_inclusive_node(sorted_child_cell_sets, current_node):
    """
    Find the first node whose children are the minimal container of the children of the current node.
    Args:
        sorted_child_cell_sets: list of the nodes and their children
        current_node: node to search its parent node.

    Returns: parent node info
    """
    is_consecutive = False
    for child_cell_sets in sorted_child_cell_sets:
        if is_consecutive and current_node["children"].issubset(child_cell_sets["children"]):
            return child_cell_sets
        if child_cell_sets == current_node:
            is_consecutive = True

    return None


def fix_multi_inheritance_relations(out, sorted_child_cell_sets):
    """
    Different from json dendrograms, (mouse) nomenclature tsv supports multi-inheritance. This function identifies
    multi-inheritance cases and accordingly generates new edges.

    There is multi-inheritance if a node is leaf but also has a children definition in the nomenclature.

    Args:
        out: single inheritance taxonomy
        sorted_child_cell_sets: list of the nodes and their children
    Returns: updated taxonomy
    """
    leaf_nodes = find_leaf_nodes(out['edges'])
    multi_inheritance_nodes = get_multi_inheritance_nodes(out, leaf_nodes, sorted_child_cell_sets)

    for mi_node in multi_inheritance_nodes:
        is_consecutive = False
        children = mi_node["children"].copy()
        for child_cell_sets in reversed(sorted_child_cell_sets):
            if is_consecutive and child_cell_sets["children"].issubset(children):
                out['edges'].add((child_cell_sets["node_cell_set_accession"], mi_node["node_cell_set_accession"]))
                children = children - child_cell_sets["children"]
            if child_cell_sets == mi_node:
                is_consecutive = True


# def get_multi_inheritance_nodes(leaf_nodes, sorted_child_cell_sets):
#     multi_inheritance_nodes = list()
#     for node in sorted_child_cell_sets:
#         if node["node_cell_set_accession"] in leaf_nodes and len(node["children"]) > 1:
#             multi_inheritance_nodes.append(node)
#     return multi_inheritance_nodes

def get_multi_inheritance_nodes(out, leaf_nodes, sorted_child_cell_sets):
    multi_inheritance_nodes = list()
    dend_tree = generate_dendrogram_tree(out)

    for node in sorted_child_cell_sets:
        descendants = nx.descendants(dend_tree, node["node_cell_set_accession"])
        for child in node["children"]:
            if child not in descendants and child != node["node_cell_set_accession"] \
                    and node not in multi_inheritance_nodes:
                multi_inheritance_nodes.append(node)

    return multi_inheritance_nodes


def find_leaf_nodes(edges):
    leaf_nodes = set()
    for edge in edges:
        leaf_nodes.add(edge[0])

    for edge in edges:
        if edge[1] in leaf_nodes:
            leaf_nodes.remove(edge[1])

    return leaf_nodes
