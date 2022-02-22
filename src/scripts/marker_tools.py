import csv
import networkx as nx
import pandas as pd
import logging
import os

from template_generation_utils import get_root_nodes, read_taxonomy_config, generate_dendrogram_tree, index_dendrogram, read_csv_to_dict
from dendrogram_tools import dend_json_2_nodes_n_edges
from nomenclature_tools import nomenclature_2_nodes_n_edges

CLUSTER = "cluster"
EXPRESSIONS = "expressions"
ALLEN_ID_PREFIX = "AllenDend:"
EXPRESSION_SEPARATOR = "|"
MARKER_PATH = '../markers/CS{}_markers.tsv'

log = logging.getLogger(__name__)


def generate_denormalised_marker_template(taxonomy_file_path, output_marker_path):
    """
    Enriches existing marker file based on inheritance relations extracted from dendrogram file.
    New maker table, following the same format as the input marker table, with each node associated with a
    non-redundant list of all markers associated with the term in the input + all markers associated with parent terms.
    Args:
        dend_json_path: Path of the dendrogram file
        output_marker_path: Path of the new marker file

    """
    path_parts = taxonomy_file_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]
    if str(taxonomy_file_path).endswith(".json"):
        dend = dend_json_2_nodes_n_edges(taxonomy_file_path)
    else:
        dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
        taxon = path_parts[len(path_parts) - 1].split(".")[0].replace("nomenclature_table_", "")

    taxonomy_config = read_taxonomy_config(taxon)

    root_nodes = get_root_nodes(taxonomy_config)

    marker_path = MARKER_PATH.format(str(taxon).replace("CCN", "").replace("CS", ""))
    generate_denormalised_marker(dend, marker_path, output_marker_path, root_nodes)


def generate_denormalised_marker(dend_data, flat_marker_path, output_marker_path, root_terms=None):
    """Enriches existing marker file based on inheritance relations extracted from dendrogram file.
       New maker table, following the same format as the input marker table, with each node associated with a
       non-redundant list of all markers associated with the term in the input + all markers associated with
       parent terms.

        Args:
            - dend_data: Dendrogram data
            - flat_marker_path: Path of the marker file that is compatible with the dendrogram file
            - output_marker_path: Path of the new marker file
            - root_terms: 'cell_set_accession' of terms. So that algorithm could be applied to a subtree
    """
    if root_terms is None:
        root_terms = []
    tree = generate_dendrogram_tree(dend_data)
    marker_expressions = read_marker_file(flat_marker_path)
    marker_extended_expressions = extend_expressions(tree, marker_expressions, root_terms)
    generate_marker_table(marker_extended_expressions, output_marker_path)


def read_marker_file(flat_marker_path):
    """
    Read marker file and build a dictionary of node and related expressions.
    Args:
        flat_marker_path: path of the input markers file

    Returns: dictionary of node expressions
        {"ID": ["expression1", "expression2"]}

    """
    marker_expressions = {}
    with open(flat_marker_path) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        # skip first row
        next(rd)
        for row in rd:
            _id = row[0].replace(ALLEN_ID_PREFIX, "")
            if not (_id in marker_expressions.keys()):
                marker_expressions[_id] = {EXPRESSIONS: row[2].split(EXPRESSION_SEPARATOR), CLUSTER: row[1]}
            else:
                log.warning("Redundant id [{0}] in markers file".format(_id))

    return marker_expressions


def extend_expressions(tree, marker_expressions, root_terms=None):
    """
    Utilizes tree to extend expression definitions of the marker expressions
    Args:
        tree: networkx directed graph that represents the taxonomy
        marker_expressions: marker file content as dict
        root_terms: 'cell_set_accession' of terms. So that algorithm could be applied to a subtree

    Returns: new marker file content with taxonomy based expression enrichment

    """
    check_root_terms(root_terms, marker_expressions)
    marker_extended_expressions = {}

    for term in marker_expressions.keys():
        extended_expressions = set(marker_expressions[term][EXPRESSIONS])

        if tree.has_node(term):
            if is_in_subtree(tree, root_terms, term):
                inherit_parent_expressions(tree, root_terms, term, marker_expressions, extended_expressions)
        else:
            log.warning("{0} exists in markers but not in dendrogram.".format(term))

        marker_extended_expressions[term] = {EXPRESSIONS: extended_expressions,
                                             CLUSTER: marker_expressions[term][CLUSTER]}

    return marker_extended_expressions


def check_root_terms(root_terms, marker_expressions):
    """
    Root nodes get no markers; markers on the root node should not be inherited
    Args:
        root_terms: 'cell_set_accession' of terms. So that algorithm could be applied to a subtree
        marker_expressions: marker file content as dict
    """
    if root_terms:
        for root in root_terms:
            if root in marker_expressions.keys():
                marker_expressions[root][EXPRESSIONS] = set()


def inherit_parent_expressions(tree, root_terms, term, marker_expressions, extended_expressions):
    """
    Enrich child node data with the parent data. Parent and child both must be in the subtree.
    Args:
        tree: networkx directed graph that represents the taxonomy tree
        root_terms: list of root terms to define subtrees
        term: child node to enrich
        marker_expressions: marker data
        extended_expressions: set of expressions to be enriched with the parent data

    """
    for parent in nx.ancestors(tree, term):
        if is_in_subtree(tree, root_terms, parent) and parent in marker_expressions.keys():
            extended_expressions.update(marker_expressions[parent][EXPRESSIONS])


def is_in_subtree(tree, root_terms, term):
    """
    Checks if given term is under subtree of given root_terms in the tree
    Args:
        tree: networkx directed graph that represents the taxonomy tree
        root_terms: list of root terms to check their subtrees
        term: term to check

    Returns: true if term is in one of the subtrees of given root terms, false otherwise

    """
    ancestors = nx.ancestors(tree, term)
    ancestors.add(term)
    if not root_terms:
        # list is empty
        return True
    return not ancestors.isdisjoint(root_terms)


def generate_marker_table(marker_data, output_filepath):
    """
    Generates marker table in the given location
    Args:
        marker_data: table data
        output_filepath: output file location

    """
    robot_marker_template_seed = {
        'Taxonomy_node_ID': 'ID',
        'clusterName': 'clusterName',
        'Markers': "TI 'expresses' % SPLIT=|"
    }
    template = []
    for o in marker_data.keys():
        d = dict()
        d['Taxonomy_node_ID'] = o
        d['clusterName'] = marker_data[o][CLUSTER]
        d['Markers'] = EXPRESSION_SEPARATOR.join(sorted(marker_data[o][EXPRESSIONS]))
        for k in robot_marker_template_seed.keys():
            if not (k in d.keys()):
                d[k] = ''
        template.append(d)
    class_robot_template = pd.DataFrame.from_records(template)
    class_robot_template.to_csv(output_filepath.replace("CCN", "CS"), sep="\t", index=False)


def get_nsforest_confidences(taxon, dend, ns_forest_marker_file):
    """
    Each NS forest marker files has a non-standard tabular structure. This function aligns cluster names mentioned in
    the marker file with the dendrogram nodes and prepares a dict of accession_id - confidence_score.
    Args:
        taxon: taxonomy id
        dend: dendrogram file
        ns_forest_marker_file: path of the marker file
    """
    nomenclature_indexes = [
                            index_dendrogram(dend, id_field_name="cell_set_preferred_alias", id_to_lower=True),
                            index_dendrogram(dend, id_field_name="cell_set_accession", id_to_lower=True),
                            index_dendrogram(dend, id_field_name="original_label", id_to_lower=True),
                            index_dendrogram(dend, id_field_name="cell_set_additional_aliases", id_to_lower=True)
                            ]

    if taxon != "CS1908210":
        nomenclature_indexes.append(index_dendrogram(dend, id_field_name="cell_set_aligned_alias", id_to_lower=True))

    confidence_map = dict()

    if os.path.isfile(ns_forest_marker_file):
        headers, raw_marker_data = read_csv_to_dict(ns_forest_marker_file, id_column_name="clusterName")
    else:
        # human mtg file extension is outlier
        headers, raw_marker_data = read_csv_to_dict(str(ns_forest_marker_file).replace(".csv", ".tsv"),
                                                    id_column_name="clusterName", delimiter="\t")

    for cluster_name in raw_marker_data:
        cluster_name_variants = [cluster_name.lower(), cluster_name.lower().replace("-", "/"),
                                 cluster_name.replace("Micro", "Microglia").lower(),
                                 ("(Mouse " + cluster_name + ")-like").lower(),
                                 ("(Mouse " + cluster_name.replace("-", "/") + ")-like").lower()]

        nomenclature_node = search_terms_in_index(cluster_name_variants, nomenclature_indexes)
        if nomenclature_node:
            node_id = nomenclature_node["cell_set_accession"]
            confidence_map[node_id] = raw_marker_data[cluster_name]["f-measure"]
        else:
            raise ValueError("Node with cluster name '{}' couldn't be found in the nomenclature of {}."
                             .format(cluster_name, taxon))

    return confidence_map


def search_terms_in_index(term_variants, indexes):
    for term in term_variants:
        for index in indexes:
            if term in index:
                return index[term]
    return None
