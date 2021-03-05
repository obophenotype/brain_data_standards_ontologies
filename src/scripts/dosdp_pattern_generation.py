import pandas as pd
import os
import csv
import networkx as nx
import argparse

from dendrogram_tools import dend_json_2_nodes_n_edges
from template_generation_utils import read_taxonomy_details_yaml
from marker_tools import read_dendrogram_tree

ALLEN_DEND_ = 'AllenDend:'


def generate_pattern_table(dend_json_path, output_filepath):
    config = read_taxonomy_details_yaml()
    dend = dend_json_2_nodes_n_edges(dend_json_path)
    dend_tree = read_dendrogram_tree(dend_json_path)

    path_parts = dend_json_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

    taxonomy_config = get_taxonomy_configuration(config, taxon)

    if taxonomy_config:
        subtrees = get_subtrees(dend_tree, taxonomy_config)
        ensmusg_names = read_ensmusg()
        denorm_markers = get_denorm_markers(taxon, ensmusg_names)
        minimal_markers = get_minimal_markers(taxon, ensmusg_names)

        dl = []
        for o in dend['nodes']:
            d = dict()
            d['defined_class'] = ALLEN_DEND_ + o['cell_set_accession']
            d['gross_cell_type'] = get_gross_cell_type(o['cell_set_accession'], subtrees, taxonomy_config)
            d['taxon'] = taxon
            d['brain_region'] = taxonomy_config['Brain_region'][0]

            if d['defined_class'] in denorm_markers:
                d['denorm_marker_list'] = denorm_markers[d['defined_class']]
            else:
                d['denorm_marker_list'] = ''

            if d['defined_class'] in minimal_markers:
                d['minimal_marker_list'] = minimal_markers[d['defined_class']]
            else:
                d['minimal_marker_list'] = ''
            dl.append(d)

    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def get_gross_cell_type(_id, subtrees, taxonomy_config):
    gross_cell_type = ''
    for index, subtree in enumerate(subtrees):
        if _id in subtree:
            gross_cell_type = taxonomy_config['Root_nodes'][index]['Cell_type']
    return gross_cell_type


def get_subtrees(dend_tree, taxonomy_config):
    """
    For each root node in the taxonomy creates the list of subtree nodes
    Args:
        dend_tree: dendrogram networkx representation
        taxonomy_config: taxonomy configuration

    Returns: list of subtree nodes

    """
    subtrees = []
    for root_node in taxonomy_config['Root_nodes']:
        descendants = nx.descendants(dend_tree, root_node['Node'])
        descendants.add(root_node['Node'])
        subtrees.append(descendants)
    return subtrees


def get_taxonomy_configuration(config, taxonomy):
    """
    Lists all taxonomies that has a configuration in the config
    Args:
        config: configuration file

    Returns: List of taxonomy names that has a configuration

    """
    for taxonomy_config in config:
        if taxonomy_config["Taxonomy_id"] == taxonomy:
            return taxonomy_config
    return


def get_denorm_markers(taxon, ensmusg_names):
    denom_marker_path = "../templates/{}_markers_denormalized.tsv".format(taxon).replace("CCN", "CS")
    return read_markers(denom_marker_path, ensmusg_names)

def get_minimal_markers(taxon, ensmusg_names):
    marker_path = "../templates/{}_markers.tsv".format(taxon)
    return read_markers(marker_path, ensmusg_names)


def read_markers(denom_marker_path, ensmusg_names):
    markers = {}
    with open(denom_marker_path) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        # skip first row
        next(rd)
        for row in rd:
            _id = row[0]
            if not _id.startswith(ALLEN_DEND_):
                _id = ALLEN_DEND_ + _id

            names = []
            if row[2]:
                for marker in row[2].split("|"):
                    if marker in ensmusg_names:
                        names.append(ensmusg_names[marker])
                    else:
                        print(marker + " couldn't find in ensmusg.tsv")
                markers[_id] = ",".join(names)
    return markers


def read_ensmusg():
    ensmusg = {}
    with open("../templates/ensmusg.tsv") as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        # skip first 2 rows
        next(rd)
        next(rd)
        for row in rd:
            _id = row[0]
            ensmusg[_id] = row[2]
    return ensmusg
