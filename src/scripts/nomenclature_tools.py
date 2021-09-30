from template_generation_utils import read_csv


NOMENCLATURE_COLUMNS = ['cell_set_preferred_alias', 'original_label', 'cell_set_label', 'cell_set_accession',
                        'cell_set_aligned_alias', 'cell_set_additional_alias', 'cell_set_alias_assignee',
                        'cell_set_alias_citation', 'cell_set_structure', 'cell_set_ontology_tag', 'taxonomy_id',
                        'species', 'modality', 'taxonomy_description', 'child_cell_set_accessions', 'cell_type_card']


def nomenclature_2_nodes_n_edges(taxonomy_file_path):
    out = dict()
    out['nodes'] = []
    out['edges'] = set()

    child_cell_sets = list()
    nomenclature_records = read_csv(taxonomy_file_path, id_column=NOMENCLATURE_COLUMNS.index('cell_set_accession'))
    for node_cell_set_accession in nomenclature_records:
        columns = nomenclature_records[node_cell_set_accession]
        node = {prop: columns[NOMENCLATURE_COLUMNS.index(prop)] for prop in NOMENCLATURE_COLUMNS}
        out['nodes'].append(node)

        children_str = columns[NOMENCLATURE_COLUMNS.index('child_cell_set_accessions')]
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
            print(child_cell_sets["node_cell_set_accession"] + " <-- " + parent_node["node_cell_set_accession"])
            out['edges'].add((child_cell_sets["node_cell_set_accession"], parent_node["node_cell_set_accession"]))

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
