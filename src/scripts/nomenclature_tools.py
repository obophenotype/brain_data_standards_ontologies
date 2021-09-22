from template_generation_utils import read_csv


NOMENCLATURE_COLUMNS = ['cell_set_preferred_alias', 'original_label', 'cell_set_label', 'cell_set_accession',
                        'cell_set_aligned_alias', 'cell_set_additional_alias', 'cell_set_alias_assignee',
                        'cell_set_alias_citation', 'cell_set_structure', 'cell_set_ontology_tag', 'taxonomy_id',
                        'species', 'modality', 'taxonomy_description', 'child_cell_set_accessions', 'cell_type_card']


def nomenclature_2_nodes_n_edges(taxonomy_file_path):
    out = dict()
    out['nodes'] = []
    out['edges'] = set()

    nomenclature_records = read_csv(taxonomy_file_path, id_column=NOMENCLATURE_COLUMNS.index('cell_set_accession'))
    for node_cell_set_accession in nomenclature_records:
        columns = nomenclature_records[node_cell_set_accession]
        node = {prop: columns[NOMENCLATURE_COLUMNS.index(prop)] for prop in NOMENCLATURE_COLUMNS}
        out['nodes'].append(node)

        children_str = columns[NOMENCLATURE_COLUMNS.index('child_cell_set_accessions')]
        if children_str:
            children = children_str.strip().split('|')
            for child in children:
                out['edges'].add((child, node_cell_set_accession))
    return out
