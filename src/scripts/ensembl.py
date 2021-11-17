import os
import logging
from pathlib import Path
import pandas as pd
from template_generation_utils import read_csv, read_csv_to_dict, read_taxonomy_details_yaml, index_dendrogram
from dendrogram_tools import dend_json_2_nodes_n_edges


GENE_DB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../templates/{}.tsv")

NOMENCLATURE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/nomenclature_table_{}.csv")

DENDROGRAM = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/{}.json")

OUTPUT_MARKER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../markers/CS{}_markers2.tsv")

MARKER_COLUMNS = ["Marker1", "Marker2", "Marker3", "Marker4"]

MARKER_COLUMNS_OPTIONAL = ["Marker5"]

log = logging.getLogger(__name__)


def search_nomenclature_with_alias(nomenclature, cluster_name):
    for record in nomenclature:
        aligned_alias = str(nomenclature[record][4]).lower()
        if aligned_alias == cluster_name.lower() or \
                aligned_alias == cluster_name.replace("-", "/").lower() or \
                aligned_alias == cluster_name.replace("Micro", "Microglia").lower():
            return nomenclature[record][3]
    return None


def search_terms_in_index(term_variants, indexes):
    for term in term_variants:
        for index in indexes:
            if term in index:
                return index[term]
    return None


def normalize_raw_markers(raw_marker):
    """
    Raw marker files has different structure than the expected. Needs these modifications:
        - Extract Taxonomy_node_ID: clusterName matches cell_set_aligned_alias of the dendrogram.
        - Resolve markers: convert marker names to ensemble IDs from local DBs
    Args:
        raw_marker:
    """
    taxonomy_config = get_taxonomy_config(raw_marker)
    taxonomy_id = taxonomy_config["Taxonomy_id"]

    print("Taxonomy ID: " + taxonomy_id)
    if taxonomy_id == "CS1908210":
        print("Read dendrogram: " + taxonomy_id)
        dend = dend_json_2_nodes_n_edges(DENDROGRAM.format(taxonomy_id))
        nomenclature_indexes = [
                                index_dendrogram(dend, id_field_name="cell_set_preferred_alias", id_to_lower=True),
                                # index_dendrogram(dend, id_field_name="cell_set_aligned_alias", id_to_lower=True),
                                index_dendrogram(dend, id_field_name="cell_set_accession", id_to_lower=True),
                                index_dendrogram(dend, id_field_name="original_label", id_to_lower=True),
                                index_dendrogram(dend, id_field_name="cell_set_additional_aliases", id_to_lower=True)
                                ]
    else:
        print("Read nomenclature table: " + taxonomy_id)
        nomenclature_indexes = [read_csv_to_dict(NOMENCLATURE.format(taxonomy_id),
                                                 id_column_name="cell_set_preferred_alias", id_to_lower=True)[1],
                                read_csv_to_dict(NOMENCLATURE.format(taxonomy_id),
                                                 id_column_name="cell_set_aligned_alias", id_to_lower=True)[1],
                                read_csv_to_dict(NOMENCLATURE.format(taxonomy_id),
                                                 id_column_name="cell_set_accession", id_to_lower=True)[1],
                                read_csv_to_dict(NOMENCLATURE.format(taxonomy_id),
                                                 id_column_name="original_label", id_to_lower=True)[1],
                                read_csv_to_dict(NOMENCLATURE.format(taxonomy_id),
                                                 id_column_name="cell_set_additional_aliases", id_to_lower=True)[1],
                                ]

    gene_db_path = GENE_DB_PATH.format(str(taxonomy_config["Reference_gene_list"][0]).strip().lower())
    headers, genes_by_name = read_csv_to_dict(gene_db_path, id_column=2, delimiter="\t", id_to_lower=True)

    unmatched_markers = set()
    normalized_markers = []

    if raw_marker.endswith(".csv"):
        headers, raw_marker_data = read_csv_to_dict(raw_marker, id_column_name="clusterName")
    else:
        headers, raw_marker_data = read_csv_to_dict(raw_marker, id_column_name="clusterName", delimiter="\t")

    for cluster_name in raw_marker_data:
        normalized_data = {}
        row = raw_marker_data[cluster_name]
        cluster_name_variants = [cluster_name.lower(), cluster_name.lower().replace("-", "/"),
                                 cluster_name.replace("Micro", "Microglia").lower()]

        nomenclature_node = search_terms_in_index(cluster_name_variants, nomenclature_indexes)
        if nomenclature_node:
            node_id = nomenclature_node["cell_set_accession"]
            marker_names = get_marker_names(row)
            marker_ids = []
            for name in marker_names:
                if name:
                    if name.lower() in genes_by_name:
                        marker_ids.append(str(genes_by_name[name.lower()]["ID"]))
                    elif name.lower().replace("_", "-") in genes_by_name:
                        marker_ids.append(str(genes_by_name[name.lower().replace("_", "-")]["ID"]))
                    else:
                        unmatched_markers.add(name)

            normalized_data["Taxonomy_node_ID"] = node_id
            normalized_data["clusterName"] = nomenclature_node["cell_set_preferred_alias"]
            normalized_data["Markers"] = "|".join(marker_ids)

            normalized_markers.append(normalized_data)
        else:
            log.error("Node with cluster name '{}' couldn't be found in the nomenclature.".format(cluster_name))
            # raise Exception("Node with cluster name {} couldn't be found in the nomenclature.".format(cluster_name))

    class_robot_template = pd.DataFrame.from_records(normalized_markers)
    class_robot_template.to_csv(OUTPUT_MARKER.format(taxonomy_id.replace("CCN", "").replace("CS", "")), sep="\t", index=False)
    log.error("Following markers could not be found in the db ({}): {}".format(len(unmatched_markers),
                                                                               str(unmatched_markers)))


def get_marker_names(row):
    marker_names = list()
    for column in MARKER_COLUMNS:
        marker_names.append(row[column].split("|")[0].strip())

    for column in MARKER_COLUMNS_OPTIONAL:
        if column in row:  # don't want hard fail
            marker_names.append(row[column].split("|")[0].strip())

    return marker_names


def get_taxonomy_config(raw_marker_path):
    species_name = Path(raw_marker_path).stem.split("_")[0]
    nsforest_name = Path(raw_marker_path).stem.split("_NSForest")[0]
    brain_region = None

    # handles Human_MTG
    if species_name is not nsforest_name:
        brain_region = nsforest_name.strip("_")[1].strip()

    taxonomy_configs = read_taxonomy_details_yaml()

    taxonomy_config = None
    for config in taxonomy_configs:
        if brain_region and brain_region in config["Brain_region_abbv"]:
            if species_name in config["Species_abbv"]:
                taxonomy_config = config
        elif species_name in config["Species_abbv"]:
            taxonomy_config = config

    if taxonomy_config:
        return taxonomy_config
    else:
        raise ValueError("Species abbreviation '" + species_name + "' couldn't be found in the taxonomy configurations.")


# def generate_marker_template(taxon, output_file):
#     marker_db = get_marker_db_by_id(taxon)
#
#     markers = set()
#     with open(OUTPUT_MARKER.format(taxon)) as fd:
#         rd = csv.reader(fd, delimiter="\t", quotechar='"')
#         next(rd)  # skip first row
#         for row in rd:
#             markers.update(row[2].split("|"))
#
#     marker_records = []
#     for marker in markers:
#         record = {}
#
#         if marker:
#             record["defined_class"] = marker
#             record["TYPE"] = "SO:0000704"
#             record["NAME"] = marker_db[marker.replace("ensembl:", "")][3]
#
#             marker_records.append(record)
#
#     class_robot_template = pd.DataFrame.from_records(marker_records)
#     class_robot_template.to_csv(output_file, sep="\t", index=False)


# generates marker files
# normalize_raw_markers("../markers/raw/Marmoset_NSForest_Markers.csv")
# normalize_raw_markers("../markers/raw/Human_NSForest_Markers.csv")
normalize_raw_markers("../markers/raw/Human_MTG_NSForest_Markers.tsv")
# normalize_raw_markers("../markers/raw/Mouse_NSForest_Markers.csv")


# generates marker dosdp templates
# generate_marker_template("201912131", "../patterns/data/bds/ensg_data.tsv")
# generate_marker_template("201912132", "../patterns/data/bds/enscjag_data.tsv")
