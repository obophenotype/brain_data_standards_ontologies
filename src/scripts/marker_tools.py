from dendrogram_tools import tree_recurse
import json
import csv
import networkx as nx
import pandas as pd
import logging

CLUSTER = "cluster"

EXPRESSIONS = "expressions"

log = logging.getLogger(__name__)

ALLEN_ID_PREFIX = "AllenDend:"

EXPRESSION_SEPARATOR = "|"


def generate_nested_marker(dend_json_path, flat_marker_path, output_marker_path, root_terms=None):
    """Enriches existing marker file based on child relations extracted from dendrogram file.
       New maker table, following the same format as the input marker table, with each node associated with a
       non-redundant list of all markers associated with the term in the input + all markers associated with
       child terms.

        Args:
            - dend_json_path: Path of the dendrogram file
            - flat_marker_path: Path of the marker file that is compatible with the dendrogram file
            - output_marker_path: Path of the new marker file
            - root_terms: 'cell_set_accession' of terms. So that algorithm could be applied to a subtree
    """
    if root_terms is None:
        root_terms = []
    tree = read_dendrogram_tree(dend_json_path)
    marker_expressions = read_marker_file(flat_marker_path)
    marker_extended_expressions = extend_expressions(tree, marker_expressions, root_terms)
    generate_marker_table(marker_extended_expressions, output_marker_path)


def read_dendrogram_tree(dend_json_path):
    """
    Reads the dendrogram file and builds a tree representation using the edges.
    Args:
        dend_json_path: Path of the dendrogram file

    Returns: networkx directed graph that represents the taxonomy

    """
    with open(dend_json_path, 'r') as f:
        j = json.loads(f.read())

    out = {}
    tree_recurse(j, out)

    tree = nx.DiGraph()
    for edge in out['edges']:
        tree.add_edge(edge[1], edge[0])

    return tree


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
    # if root_terms is None:
    #     root_terms = []
    marker_extended_expressions = {}

    for term in marker_expressions.keys():
        extended_expressions = set(marker_expressions[term][EXPRESSIONS])

        if tree.has_node(term):
            if is_in_subtree(tree, root_terms, term):
                # enrich parent expressions with child data
                for child in nx.descendants(tree, term):
                    add_child_expressions(child, marker_expressions, extended_expressions)
        else:
            log.warning("{0} exists in markers but not in dendrogram.".format(term))

        marker_extended_expressions[term] = {EXPRESSIONS: extended_expressions,
                                             CLUSTER: marker_expressions[term][CLUSTER]}

    return marker_extended_expressions


def add_child_expressions(child, marker_expressions, extended_expressions):
    if child in marker_expressions.keys():
        for expression in marker_expressions[child][EXPRESSIONS]:
            extended_expressions.add(expression)


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
        'Markers Delimited': "TI 'expresses' % SPLIT = '|' "
    }
    template = []
    for o in marker_data.keys():
        d = dict()
        d['Taxonomy_node_ID'] = o
        d['clusterName'] = marker_data[o][CLUSTER]
        d['Markers Delimited'] = EXPRESSION_SEPARATOR.join(marker_data[o][EXPRESSIONS])
        for k in robot_marker_template_seed.keys():
            if not (k in d.keys()):
                d[k] = ''
        template.append(d)
    class_robot_template = pd.DataFrame.from_records(template)
    class_robot_template.to_csv(output_filepath, sep="\t", index=False)
