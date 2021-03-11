import pandas as pd
import os
import csv

from dendrogram_tools import dend_json_2_nodes_n_edges
from template_generation_utils import read_taxonomy_config, get_subtrees
from marker_tools import read_dendrogram_tree

MARKERS_PATH = "../markers/{}_markers.tsv"
MARKERS_DENORMALIZED_PATH = "../markers/{}_markers_denormalized.tsv"

ALLEN_DEND_ = 'AllenDendClass:'


def generate_pattern_table(dend_json_path, output_filepath):
    path_parts = dend_json_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

    taxonomy_config = read_taxonomy_config(taxon)

    dend = dend_json_2_nodes_n_edges(dend_json_path)
    dend_tree = read_dendrogram_tree(dend_json_path)

    if taxonomy_config:
        subtrees = get_subtrees(dend_tree, taxonomy_config)
        ensmusg_names = read_ensmusg()
        denorm_markers = get_denorm_markers(taxon, ensmusg_names)
        minimal_markers = get_minimal_markers(taxon, ensmusg_names)

        dl = []
        for o in dend['nodes']:
            if o['cell_set_accession'] in set.union(*subtrees):
                d = dict()
                d['defined_class'] = ALLEN_DEND_ + o['cell_set_accession']
                d['gross_cell_type'] = get_gross_cell_type(o['cell_set_accession'], subtrees, taxonomy_config)
                d['taxon'] = taxonomy_config['Species'][0]
                d['brain_region'] = taxonomy_config['Brain_region'][0]

                if o['cell_set_accession'] in denorm_markers:
                    d['denorm_marker_list'] = denorm_markers[o['cell_set_accession']]
                    d['minimal_marker_list'] = minimal_markers[o['cell_set_accession']]
                else:
                    d['denorm_marker_list'] = ''
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


def get_denorm_markers(taxon, ensmusg_names):
    denom_marker_path = MARKERS_DENORMALIZED_PATH.format(taxon).replace("CCN", "CS")
    return read_markers(denom_marker_path, ensmusg_names)


def get_minimal_markers(taxon, ensmusg_names):
    marker_path = MARKERS_PATH.format(taxon).replace("CCN", "CS")
    return read_markers(marker_path, ensmusg_names)


def read_markers(marker_path, ensmusg_names):
    markers = {}
    with open(marker_path) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        # skip first row
        next(rd)
        for row in rd:
            _id = row[0]

            names = []
            if row[2]:
                for marker in row[2].split("|"):
                    if marker in ensmusg_names:
                        names.append(ensmusg_names[marker])
                    else:
                        print(marker + " couldn't find in ensmusg.tsv")
                markers[_id] = ",".join(sorted(names))
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


generate_pattern_table("../dendrograms/CCN202002013.json", "../patterns/data/default/brainCellRegionMarker.tsv")
