import logging
import csv
import requests
import pandas as pd

from template_generation_utils import read_csv

ENSEMBLE_SERVICE = "https://rest.ensembl.org/xrefs/symbol/{}/{}?content-type=application/json"

raw_markers_taxonomies = {"../markers/raw/AIBS_M1_NSForest_v2_marmoset_ALL_Results.csv": "201912132",
                          "../markers/raw/AIBS_M1_NSForest_v2_human_ALL_Results.csv": "201912131"}

marker_dbs = {"201912132": "../markers/raw/Marmoset genes ASM275486v1.csv",
              "201912131": "../markers/raw/Human genes GRCh38.p13.csv"}

species_mapping = {"201912132": "marmoset",
                   "201912131": "human"}

NOMENCLATURE = "../dendrograms/nomenclature_table_CCN{}.csv"

OUTPUT_MARKER = "../markers/CS{}_markers.tsv"

log = logging.getLogger(__name__)


def get_marker_db_by_name(taxonomy):
    return read_csv(marker_dbs[taxonomy], id_column=3, delimiter=",", id_to_lower=True)


def get_marker_db_by_synonyms(taxonomy):
    return read_csv(marker_dbs[taxonomy], id_column=4, delimiter=",", id_to_lower=True)


def get_marker_db_by_id(taxonomy):
    return read_csv(marker_dbs[taxonomy], id_column=0, delimiter=",")


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
                return index[term][3]
    return None


def lookup_marker(taxonomy, symbol):
    # specie = species_mapping[taxonomy]
    # response = requests.get(ENSEMBLE_SERVICE.format(specie, symbol))
    # data = response.json()
    #
    # _id = None
    # if len(data) == 1:
    #     _id = "ensembl:" + data[0]["id"]
    # return _id
    return None


def normalize_raw_markers(raw_marker):
    """
    Raw marker files has different structure than the expected. Needs these modifications:
        - Extract Taxonomy_node_ID: clusterName matches cell_set_aligned_alias of the dendrogram.
        - Resolve markers: convert marker names to ensemble IDs from local DBs
        - Lookup missing markers from rest service
    Args:
        raw_marker:
    """
    taxonomy = raw_markers_taxonomies[raw_marker]

    # indexes with preferred_alias, aligned_alias and additional_alias
    nomenclature_indexes = [read_csv(NOMENCLATURE.format(taxonomy), id_column=0, id_to_lower=True),
                            read_csv(NOMENCLATURE.format(taxonomy), id_column=4, id_to_lower=True),
                            read_csv(NOMENCLATURE.format(taxonomy), id_column=5, id_to_lower=True)]

    marker_db = get_marker_db_by_name(taxonomy)
    marker_db_synonyms = get_marker_db_by_synonyms(taxonomy)

    unmatched_markers = set()
    normalized_markers = []
    with open(raw_marker) as fd:
        rd = csv.reader(fd, delimiter=",", quotechar='"')
        next(rd)  # skip first row
        for row in rd:
            normalized_data = {}
            cluster_name = row[0]
            cluster_name_variants = [cluster_name.lower(), cluster_name.lower().replace("-", "/"),
                                     cluster_name.replace("Micro", "Microglia").lower()]

            node_id = search_terms_in_index(cluster_name_variants, nomenclature_indexes)
            if node_id:
                marker_names = [row[7], row[8], row[9], row[10], row[11]]
                marker_ids = []
                for name in marker_names:
                    if name:
                        if name.lower() in marker_db:
                            marker_ids.append("ensembl:" + str(marker_db[name.lower()][0]))
                        elif name.lower() in marker_db_synonyms:
                            marker_ids.append("ensembl:" + str(marker_db_synonyms[name.lower()][0]))
                        else:
                            marker = lookup_marker(taxonomy, name)
                            if marker:
                                marker_ids.append(marker)
                            else:
                                unmatched_markers.add(name)

                normalized_data["Taxonomy_node_ID"] = node_id
                normalized_data["clusterName"] = cluster_name
                normalized_data["Markers"] = "|".join(marker_ids)

                normalized_markers.append(normalized_data)
            else:
                log.error("Node with cluster name '{}' couldn't be found in the nomenclature.".format(cluster_name))
                # raise Exception("Node with cluster name {} couldn't be found in the nomenclature.".format(cluster_name))

    class_robot_template = pd.DataFrame.from_records(normalized_markers)
    class_robot_template.to_csv(OUTPUT_MARKER.format(taxonomy), sep="\t", index=False)
    log.error("Following markers could not be found in the db ({}): {}".format(len(unmatched_markers),
                                                                               str(unmatched_markers)))


def generate_marker_template(taxon, output_file):
    marker_db = get_marker_db_by_id(taxon)

    markers = set()
    with open(OUTPUT_MARKER.format(taxon)) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        next(rd)  # skip first row
        for row in rd:
            markers.update(row[2].split("|"))

    marker_records = []
    for marker in markers:
        record = {}

        if marker:
            record["defined_class"] = marker
            record["TYPE"] = "SO:0000704"
            record["NAME"] = marker_db[marker.replace("ensembl:", "")][3]

            marker_records.append(record)

    class_robot_template = pd.DataFrame.from_records(marker_records)
    class_robot_template.to_csv(output_file, sep="\t", index=False)


# generates marker files
# normalize_raw_markers("../markers/raw/AIBS_M1_NSForest_v2_marmoset_ALL_Results.csv")
# normalize_raw_markers("../markers/raw/AIBS_M1_NSForest_v2_human_ALL_Results.csv")

# generates marker dosdp templates
# generate_marker_template("201912131", "../patterns/data/bds/ensg_data.tsv")
# generate_marker_template("201912132", "../patterns/data/bds/enscjag_data.tsv")
