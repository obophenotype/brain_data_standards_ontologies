import os
import logging
import csv
import requests
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

MYGENE_ENDPOINT = "https://mygene.info/v3/gene/{geneid}?fields=alias%2Cother_names&dotfield=false"
MYGENE_BATCH_ENDPOINT = "https://mygene.info/v3/gene?fields=alias%2Cother_names"

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
    species_abbv = get_species_for_gene_db(gene_db_path).lower()

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
                    if species_abbv + " " + name.lower() in genes_by_name:
                        marker_ids.append(str(genes_by_name[species_abbv + " " + name.lower()]["ID"]))
                    elif species_abbv + " " + name.lower().replace("_", "-") in genes_by_name:
                        marker_ids.append(str(genes_by_name[species_abbv + " " + name.lower().replace("_", "-")]["ID"]))
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
    brain_region = "M1"  # default

    # handles Human_MTG
    if species_name != nsforest_name:
        brain_region = nsforest_name.split("_")[1].strip()
    elif species_name == "Mouse":
        brain_region = "MOp"

    taxonomy_configs = read_taxonomy_details_yaml()

    taxonomy_config = None
    for config in taxonomy_configs:
        print(brain_region)
        if species_name in config["Species_abbv"] and brain_region in config["Brain_region_abbv"]:
            taxonomy_config = config

    if taxonomy_config:
        return taxonomy_config
    else:
        raise ValueError("Species abbreviation '" + species_name + "' couldn't be found in the taxonomy configurations.")


def get_species_for_gene_db(gene_db_path):
    gene_db_name = Path(gene_db_path).stem.split(".")[0]

    taxonomy_configs = read_taxonomy_details_yaml()

    taxonomy_config = None
    for config in taxonomy_configs:
        if gene_db_name.lower() in (name.lower() for name in config["Reference_gene_list"]):
            taxonomy_config = config

    if taxonomy_config:
        return taxonomy_config["Gene_abbv"][0]
    else:
        raise ValueError("Reference_gene_list for gene_db '" + gene_db_path +
                         "' couldn't be found in the taxonomy configurations.")


def fix_gene_database(gene_db_path, gene_prefix):
    headers, genes_by_name = read_csv_to_dict(gene_db_path, id_column=1, delimiter="\t")
    species_abbv = get_species_for_gene_db(gene_db_path)

    with open(gene_db_path.replace(".tsv", "_2.tsv"), mode='w') as out:
        writer = csv.writer(out, delimiter="\t", quotechar='"')
        writer.writerow(["ID", "TYPE", "NAME"])
        writer.writerow(["ID", "SC %", "A rdfs:label"])

        print(headers)
        for gene in genes_by_name:
            writer.writerow([gene_prefix + gene.replace("\"", ""), "SO:0000704",
                             genes_by_name[gene]["gene_name"] + " (" + species_abbv + ")"])


def fix_gene_database_species(gene_db_path):
    headers, genes_by_id = read_csv_to_dict(gene_db_path, id_column=0, delimiter="\t")
    species_abbv = get_species_for_gene_db(gene_db_path)

    with open(gene_db_path.replace(".tsv", "_2.tsv"), mode='w') as out:
        writer = csv.writer(out, delimiter="\t", quotechar='"')
        writer.writerow(["ID", "TYPE", "NAME"])
        writer.writerow(["ID", "SC %", "A rdfs:label"])

        print(headers)
        for gene in genes_by_id:
            writer.writerow([genes_by_id[gene]["ID"], genes_by_id[gene]["TYPE"],
                             genes_by_id[gene]["NAME"] + " (" + species_abbv + ")"])


def add_cluster_name_to_marker(marker_path):
    path_parts = marker_path.split(os.path.sep)
    taxonomy_id = path_parts[len(path_parts) - 1].split("_")[0].replace("CS", "CCN")

    marker_data = read_csv_to_dict(marker_path, id_column_name="Taxonomy_node_ID", delimiter="\t")[1]
    nomenclature = read_csv_to_dict(NOMENCLATURE.format(taxonomy_id), id_column_name="cell_set_accession")[1]

    normalized_markers = []
    for accession_id in marker_data:
        normalized_data = {"Taxonomy_node_ID": accession_id,
                           "clusterName": nomenclature[accession_id]["original_label"],
                           "Markers": marker_data[accession_id]["Markers"]}

        normalized_markers.append(normalized_data)

    class_robot_template = pd.DataFrame.from_records(normalized_markers)
    class_robot_template.to_csv(OUTPUT_MARKER.format(taxonomy_id.replace("CCN", "").replace("CS", "")), sep="\t", index=False)


def add_mygene_synonyms(gene_db_path):
    """
    Reads an existing gene database and queries mygene api to get synonyms.
    """
    headers, genes_by_id = read_csv_to_dict(gene_db_path, id_column=0, delimiter="\t")
    gene_ids = [gene for gene in genes_by_id if ":" in gene]

    synonyms = mygene_get_synonyms_in_batches(gene_ids, 1000)

    with open(gene_db_path.replace(".tsv", "_mygene.tsv"), mode='w') as out:
        writer = csv.writer(out, delimiter="\t", quotechar='"')
        writer.writerow(["ID", "TYPE", "NAME", "SYNONYMS"])
        writer.writerow(["ID", "SC %", "A rdfs:label", "A oboInOwl:hasExactSynonym SPLIT=|"])

        for gene in genes_by_id:
            if ":" in gene:
                writer.writerow([genes_by_id[gene]["ID"], genes_by_id[gene]["TYPE"],
                                 genes_by_id[gene]["NAME"], "|".join(synonyms[gene.split(":")[1]])])

    log.info("MyGene crawling completed.")


def mygene_get_synonyms_in_batches(gene_ids, batch_size):
    synonyms = dict()
    chunks = get_chunks(gene_ids, batch_size)
    i = 0
    for chunk in chunks:
        i += 1
        print("Processing chunk :" + str(i) + " of " + str(len(gene_ids) / batch_size))
        synonyms.update(mygene_get_synonyms(chunk))
    return synonyms


def get_chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def mygene_get_synonyms(genes):
    """
    Queries alias and other_names for the given gene.

    Return: list of synonyms
    """
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(MYGENE_BATCH_ENDPOINT, data=(encode_gene_list(genes)), headers=headers)

    gene_synonyms = dict()
    if r.status_code == 200:
        response = r.json()
        for query in response:
            synonyms = set()
            gene_id = query["query"]
            if "alias" in query:
                if isinstance(query["alias"], list):
                    synonyms.update(query["alias"])
                else:
                    synonyms.add(query["alias"])
            if "other_names" in query:
                if isinstance(query["other_names"], list):
                    synonyms.update(query["other_names"])
                else:
                    synonyms.add(query["other_names"])
            gene_synonyms[gene_id] = synonyms
    else:
        log.error("!! Error occurred while querying mygene: " + "\n" + r.text)

    return gene_synonyms


def encode_gene_list(genes):
    gene_ids = [gene.split(":")[1] for gene in genes]
    return "ids=" + ",".join(gene_ids)


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
# normalize_raw_markers("../markers/raw/Human_MTG_NSForest_Markers.tsv")
# normalize_raw_markers("../markers/raw/Mouse_NSForest_Markers.csv")


# generates marker dosdp templates
# generate_marker_template("201912131", "../patterns/data/bds/ensg_data.tsv")
# generate_marker_template("201912132", "../patterns/data/bds/enscjag_data.tsv")

# fix_gene_database(GENE_DB_PATH.format("simple_human"), "entrez:")
# fix_gene_database(GENE_DB_PATH.format("ensmusg"), "ensembl:")

# fix_gene_database_species(GENE_DB_PATH.format("simple_human"))
# fix_gene_database_species(GENE_DB_PATH.format("simple_marmoset"))
# fix_gene_database_species(GENE_DB_PATH.format("ensmusg"))

# markers provided by Brian don't have clusterName, add them
# add_cluster_name_to_marker("../markers/CS202002013_markers.tsv")

# add_mygene_synonyms(GENE_DB_PATH.format("simple_human"))
# add_mygene_synonyms(GENE_DB_PATH.format("simple_marmoset"))
# add_mygene_synonyms(GENE_DB_PATH.format("ensmusg"))

