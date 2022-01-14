import pandas as pd
import os

from dendrogram_tools import dend_json_2_nodes_n_edges
from template_generation_utils import read_taxonomy_config, get_subtrees, read_dendrogram_tree, read_gene_data, \
    read_markers, get_gross_cell_type

MARKER_PATH = '../markers/CS{}_markers.tsv'
MARKERS_DENORMALIZED_PATH = "../markers/{}_markers_denormalized.tsv"
ALLEN_MARKER_PATH = "../markers/CS{}_Allen_markers.tsv"
ENSEMBLE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../templates/{}.tsv")

ALLEN_DEND_ = 'AllenDendClass:'


def generate_pattern_table_denormalised_markers(dend_json_path, output_filepath):
    path_parts = dend_json_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

    taxonomy_config = read_taxonomy_config(taxon)

    dend = dend_json_2_nodes_n_edges(dend_json_path)
    dend_tree = read_dendrogram_tree(dend_json_path)

    marker_path = MARKER_PATH.format(str(taxon).replace("CCN", ""))
    gene_db_path = ENSEMBLE_PATH.format(str(taxonomy_config["Reference_gene_list"][0]).strip().lower())

    if taxonomy_config:
        subtrees = get_subtrees(dend_tree, taxonomy_config)
        gene_names = read_gene_data(gene_db_path)
        denorm_markers = get_denorm_markers(taxon, gene_names)
        minimal_markers = read_markers(marker_path, gene_names)

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


def get_denorm_markers(taxon, ensmusg_names):
    denom_marker_path = MARKERS_DENORMALIZED_PATH.format(taxon).replace("CCN", "CS")
    return read_markers(denom_marker_path, ensmusg_names)


# ec_denormalised markers branch
# generate_pattern_table_denormalised_markers("../dendrograms/CCN202002013.json", "../patterns/data/default/brainCellRegionMarker.tsv")
# ec_individuals branch
# generate_pattern_table_reification("../dendrograms/CCN202002013.json", "../patterns/data/default/brainCellRegionMinimalMarkers.tsv")
