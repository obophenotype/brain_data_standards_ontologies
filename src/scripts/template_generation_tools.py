import pandas as pd
import json
import os
import logging

from dendrogram_tools import dend_json_2_nodes_n_edges
from template_generation_utils import get_synonyms_from_taxonomy, get_synonym_pairs, read_taxonomy_config, \
    get_subtrees, generate_dendrogram_tree, read_taxonomy_details_yaml, read_csv_to_dict,\
    read_csv, read_gene_data, read_markers, get_gross_cell_type, merge_tables, read_allen_descriptions
from nomenclature_tools import nomenclature_2_nodes_n_edges


log = logging.getLogger(__name__)

ALLEN_DEND_CLASS = 'http://www.semanticweb.org/brain_data_standards/AllenDendClass_'
ALLEN_DEND_INDV = 'http://www.semanticweb.org/brain_data_standards/AllenDend_'
ALLEN_DEND_INDV_PREFIX = 'AllenDend:'

MARKER_PATH = '../markers/CS{}_markers.tsv'
ALLEN_MARKER_PATH = "../markers/CS{}_Allen_markers.tsv"
NOMENCLATURE_TABLE_PATH = '../dendrograms/nomenclature_table_{}.csv'
ENSEMBLE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../templates/{}.tsv")
CROSS_SPECIES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  "../dendrograms/nomenclature_table_CCN202002270.csv")
ALLEN_DESCRIPTIONS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                       '../dendrograms/All Descriptions_{}.json')

EXPRESSION_SEPARATOR = "|"


def generate_ind_template(taxonomy_file_path, output_filepath):
    path_parts = taxonomy_file_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

    if str(taxonomy_file_path).endswith(".json"):
        dend = dend_json_2_nodes_n_edges(taxonomy_file_path)
    else:
        dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
        taxon = path_parts[len(path_parts) - 1].split(".")[0].replace("nomenclature_table_", "")

    dend_tree = generate_dendrogram_tree(dend)
    taxonomy_config = read_taxonomy_config(taxon)
    allen_descriptions = read_allen_descriptions(ALLEN_DESCRIPTIONS_PATH, taxonomy_config['Species_abbv'][0])

    subtrees = get_subtrees(dend_tree, taxonomy_config)

    robot_template_seed = {'ID': 'ID',
                           'Label': 'LABEL',
                           'PrefLabel': 'A skos:prefLabel',
                           'Entity Type': 'TI %',
                           'TYPE': 'TYPE',
                           'Property Assertions': "I 'subcluster of' SPLIT=|",
                           'Synonyms': 'A oboInOwl:hasExactSynonym SPLIT=|',
                           'Function': 'TI capable_of some %',
                           'cell_set_preferred_alias': "A n2o:cell_set_preferred_alias",
                           'original_label': "A n2o:original_label",
                           'cell_set_label': "A n2o:cell_set_label",
                           'cell_set_aligned_alias': "A n2o:cell_set_aligned_alias",
                           'cell_set_additional_aliases': "A n2o:cell_set_additional_aliases SPLIT=|",
                           'cell_set_alias_assignee': "A n2o:cell_set_alias_assignee SPLIT=|",
                           'cell_set_alias_citation': "A n2o:cell_set_alias_citation SPLIT=|",
                           'Metadata': "A n2o:node_metadata",
                           'Exemplar_of': "TI 'exemplar data of' some %",
                           'Comment': "A rdfs:comment",
                           'Aliases': "A oboInOwl:hasRelatedSynonym SPLIT=|",
                           'Rank': "A BDSHELP:cell_type_rank SPLIT=|"
                           }
    dl = [robot_template_seed]

    synonym_properties = ['cell_set_aligned_alias',
                          'cell_set_additional_aliases']

    for o in dend['nodes']:
        d = dict()
        d['ID'] = 'AllenDend:' + o['cell_set_accession']
        d['TYPE'] = 'owl:NamedIndividual'
        d['Label'] = o['cell_set_label'] + ' - ' + o['cell_set_accession']
        d['PrefLabel'] = o['cell_set_preferred_alias'] + ' - ' + o['cell_set_accession']
        d['Entity Type'] = 'BDSHELP:Cluster'
        d['Metadata'] = json.dumps(o)
        d['Synonyms'] = '|'.join([o[prop] for prop in synonym_properties if prop in o.keys() and o[prop]])
        d['Property Assertions'] = '|'.join(
            ['AllenDend:' + e[1] for e in dend['edges'] if e[0] == o['cell_set_accession']])
        meta_properties = ['cell_set_preferred_alias', 'original_label', 'cell_set_label', 'cell_set_aligned_alias',
                           'cell_set_additional_aliases', 'cell_set_alias_assignee', 'cell_set_alias_citation']
        for prop in meta_properties:
            if prop in o.keys():
                d[prop] = '|'.join([prop_val.strip() for prop_val in str(o[prop]).split("|") if prop_val])
            else:
                d[prop] = ''

        if o['cell_set_accession'] in set().union(*subtrees) and o['cell_set_preferred_alias']:
            d['Exemplar_of'] = ALLEN_DEND_CLASS + o['cell_set_accession']

        d['Rank'] = '|'.join([cell_type.strip().replace("No", "None")
                              for cell_type in str(o["cell_type_card"]).split(",")])

        if o['cell_set_accession'] in allen_descriptions:
            allen_data = allen_descriptions[o['cell_set_accession']]
            d['Comment'] = allen_data["summary"][0]
            if allen_data["aliases"][0]:
                d['Aliases'] = '|'.join([alias.strip() for alias in str(allen_data["aliases"][0]).split("|")])

        # There should only be one!
        dl.append(d)
    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_base_class_template(taxonomy_file_path, all_taxonomies, output_filepath):
    path_parts = taxonomy_file_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

    if str(taxonomy_file_path).endswith(".json"):
        dend = dend_json_2_nodes_n_edges(taxonomy_file_path)
    else:
        dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
        taxon = path_parts[len(path_parts) - 1].split(".")[0].replace("nomenclature_table_", "")

    dend_tree = generate_dendrogram_tree(dend)
    taxonomy_config = read_taxonomy_config(taxon)

    marker_path = MARKER_PATH.format(str(taxon).replace("CCN", ""))
    allen_marker_path = ALLEN_MARKER_PATH.format(str(taxon).replace("CCN", ""))

    all_taxonomies.remove(taxon)
    other_taxonomy_aliases = index_taxonomies(all_taxonomies)

    if taxonomy_config:
        subtrees = get_subtrees(dend_tree, taxonomy_config)

        if "Reference_gene_list" in taxonomy_config:
            gene_db_path = ENSEMBLE_PATH.format(str(taxonomy_config["Reference_gene_list"][0]).strip().lower())
            gene_names = read_gene_data(gene_db_path)
            minimal_markers = read_markers(marker_path, gene_names)
            allen_markers = read_markers(allen_marker_path, gene_names)
        else:
            minimal_markers = {}
            allen_markers = {}

        class_seed = ['defined_class',
                      'prefLabel',
                      'Alias_citations',
                      'Synonyms_from_taxonomy',
                      'Comment',
                      'Gross_cell_type',
                      'Taxon',
                      'Brain_region',
                      'Minimal_markers',
                      'Allen_markers',
                      'Individual',
                      'Brain_region_abbv',
                      'Species_abbv',
                      'part_of',
                      'has_soma_location',
                      'homologous_to'
                      ]
        class_template = []

        for o in dend['nodes']:
            if o['cell_set_accession'] in set.union(*subtrees) and (o['cell_set_preferred_alias'] or
                                                                    o['cell_set_additional_aliases']):
                d = dict()
                d['defined_class'] = ALLEN_DEND_CLASS + o['cell_set_accession']
                if o['cell_set_preferred_alias']:
                    d['prefLabel'] = o['cell_set_preferred_alias']
                elif o['cell_set_additional_aliases']:
                    d['prefLabel'] = str(o['cell_set_additional_aliases']).split(EXPRESSION_SEPARATOR)[0]
                d['Synonyms_from_taxonomy'] = get_synonyms_from_taxonomy(o)
                d['Comment'] = get_synonym_pairs(o)
                d['Gross_cell_type'] = get_gross_cell_type(o['cell_set_accession'], subtrees, taxonomy_config)
                d['Taxon'] = taxonomy_config['Species'][0]
                d['Brain_region'] = taxonomy_config['Brain_region'][0]
                if o['cell_set_alias_citation']:
                    alias_citations = [citation.strip() for citation in str(o["cell_set_alias_citation"]).split("|")
                                       if citation and citation.strip()]
                    d["Alias_citations"] = "|".join(alias_citations)
                if o['cell_set_accession'] in minimal_markers:
                    d['Minimal_markers'] = minimal_markers[o['cell_set_accession']]
                if o['cell_set_accession'] in allen_markers:
                    d['Allen_markers'] = allen_markers[o['cell_set_accession']]
                else:
                    d['Allen_markers'] = ''
                if 'Brain_region_abbv' in taxonomy_config:
                    d['Brain_region_abbv'] = taxonomy_config['Brain_region_abbv'][0]
                if 'Species_abbv' in taxonomy_config:
                    d['Species_abbv'] = taxonomy_config['Species_abbv'][0]
                d['Individual'] = ALLEN_DEND_INDV_PREFIX + o['cell_set_accession']

                for index, subtree in enumerate(subtrees):
                    if o['cell_set_accession'] in subtree:
                        location_rel = taxonomy_config['Root_nodes'][index]['Location_relation']
                        if location_rel == "part_of":
                            d['part_of'] = taxonomy_config['Brain_region'][0]
                            d['has_soma_location'] = ''
                        elif location_rel == "has_soma_location":
                            d['part_of'] = ''
                            d['has_soma_location'] = taxonomy_config['Brain_region'][0]

                homologous_to = list()
                for other_aliases in other_taxonomy_aliases:
                    if o["cell_set_aligned_alias"] and str(o["cell_set_aligned_alias"]).lower() in other_aliases:
                        homologous_to.append(ALLEN_DEND_CLASS + other_aliases[str(o["cell_set_aligned_alias"])
                                             .lower()]["cell_set_accession"])
                d['homologous_to'] = "|".join(homologous_to)

                for k in class_seed:
                    if not (k in d.keys()):
                        d[k] = ''
                class_template.append(d)

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_curated_class_template(taxonomy_file_path, output_filepath):
    path_parts = taxonomy_file_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

    if str(taxonomy_file_path).endswith(".json"):
        dend = dend_json_2_nodes_n_edges(taxonomy_file_path)
    else:
        dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
        taxon = path_parts[len(path_parts) - 1].split(".")[0].replace("nomenclature_table_", "")

    dend_tree = generate_dendrogram_tree(dend)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        subtrees = get_subtrees(dend_tree, taxonomy_config)
        class_curation_seed = ['defined_class',
                               'Curated_synonyms',
                               'Classification',
                               'Classification_comment',
                               'Classification_pub',
                               'Expresses',
                               'Expresses_comment',
                               'Expresses_pub',
                               'Projection_type',
                               'Layers',
                               'Definition'
                               ]
        class_template = []

        for o in dend['nodes']:
            if o['cell_set_accession'] in set.union(*subtrees) and (o['cell_set_preferred_alias'] or
                                                                    o['cell_set_additional_aliases']):
                d = dict()
                d['defined_class'] = ALLEN_DEND_CLASS + o['cell_set_accession']
                if o['cell_set_preferred_alias']:
                    d['prefLabel'] = o['cell_set_preferred_alias']
                elif o['cell_set_additional_aliases']:
                    d['prefLabel'] = str(o['cell_set_additional_aliases']).split(EXPRESSION_SEPARATOR)[0]

                for k in class_curation_seed:
                    if not (k in d.keys()):
                        d[k] = ''
                class_template.append(d)

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_non_taxonomy_classification_template(taxonomy_file_path, output_filepath):
    path_parts = taxonomy_file_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

    if str(taxonomy_file_path).endswith(".json"):
        dend = dend_json_2_nodes_n_edges(taxonomy_file_path)
    else:
        dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
        taxon = path_parts[len(path_parts) - 1].split(".")[0].replace("nomenclature_table_", "")

    # dend_nodes = index_dendrogram(dend)

    cell_set_accession = 3
    child_cell_set_accessions = 14
    nomenclature_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     NOMENCLATURE_TABLE_PATH.format(taxon))

    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config and os.path.exists(nomenclature_path):
        nomenclature_records = read_csv(nomenclature_path, id_column=cell_set_accession)
        nomenclature_template = []

        non_taxo_roots = {}
        for root in taxonomy_config['non_taxonomy_roots']:
            non_taxo_roots[root["Node"]] = root["Cell_type"]

        for record in nomenclature_records:
            columns = nomenclature_records[record]
            if columns[cell_set_accession] in non_taxo_roots:
                # dendrogram is not mandatory for human & marmoset
                # if columns[cell_set_accession] in dend_nodes:
                #     raise Exception("Node {} exists both in dendrogram and nomenclature of the taxonomy: {}."
                #                     .format(columns[cell_set_accession], taxon))
                children = columns[child_cell_set_accessions].split("|")
                for child in children:
                    # child of root with cell_set_preferred_alias
                    if child not in non_taxo_roots and nomenclature_records[child][0]:
                        d = dict()
                        d['defined_class'] = ALLEN_DEND_CLASS + child
                        d['Classification'] = non_taxo_roots[columns[cell_set_accession]]
                        nomenclature_template.append(d)

        class_robot_template = pd.DataFrame.from_records(nomenclature_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_cross_species_template(taxonomy_file_path, output_filepath):
    path_parts = taxonomy_file_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

    if str(taxonomy_file_path).endswith(".json"):
        dend = dend_json_2_nodes_n_edges(taxonomy_file_path)
    else:
        dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
        taxon = path_parts[len(path_parts) - 1].split(".")[0].replace("nomenclature_table_", "")

    dend_tree = generate_dendrogram_tree(dend)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        subtrees = get_subtrees(dend_tree, taxonomy_config)
        cross_species_template = []

        headers, cs_by_preferred_alias = read_csv_to_dict(CROSS_SPECIES_PATH,
                                                          id_column_name="cell_set_preferred_alias", id_to_lower=True)
        headers, cs_by_aligned_alias = read_csv_to_dict(CROSS_SPECIES_PATH,
                                                        id_column_name="cell_set_aligned_alias", id_to_lower=True)

        for o in dend['nodes']:
            if o['cell_set_accession'] in set.union(*subtrees) and (o['cell_set_preferred_alias'] or
                                                                    o['cell_set_additional_aliases']):
                cross_species_classes = set()
                if o["cell_set_aligned_alias"] and str(o["cell_set_aligned_alias"]).lower() in cs_by_aligned_alias:
                    cross_species_classes.add(ALLEN_DEND_CLASS + cs_by_aligned_alias[str(o["cell_set_aligned_alias"])
                                              .lower()]["cell_set_accession"])

                if "cell_set_additional_aliases" in o and o["cell_set_additional_aliases"]:
                    additional_aliases = str(o["cell_set_additional_aliases"]).lower().split(EXPRESSION_SEPARATOR)
                    for additional_alias in additional_aliases:
                        if additional_alias in cs_by_preferred_alias:
                            cross_species_classes.add(ALLEN_DEND_CLASS +
                                                      cs_by_preferred_alias[additional_alias]["cell_set_accession"])

                if len(cross_species_classes):
                    d = dict()
                    d['defined_class'] = ALLEN_DEND_CLASS + o['cell_set_accession']
                    d['cross_species_classes'] = EXPRESSION_SEPARATOR.join(cross_species_classes)

                    cross_species_template.append(d)

        class_robot_template = pd.DataFrame.from_records(cross_species_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_taxonomies_template(taxonomy_metadata_path, output_filepath):
    taxon_configs = read_taxonomy_details_yaml()
    headers, taxonomies_metadata = read_csv_to_dict(taxonomy_metadata_path)

    robot_template_seed = {'ID': 'ID',
                           'TYPE': 'TYPE',
                           'Entity Type': 'TI %',
                           'Label': 'LABEL',
                           'Number of Cell Types': 'A BDSHELP:cell_types_count',
                           'Number of Cell Subclasses': 'A BDSHELP:cell_subclasses_count',
                           'Number of Cell Classes': 'A BDSHELP:cell_classes_count',
                           'Anatomic Region': "A BDSHELP:has_brain_region",
                           'Species Label': 'A skos:prefLabel',
                           'Age': 'A BDSHELP:has_age',
                           'Sex': 'A BDSHELP:has_sex',
                           'Primary Citation': "A oboInOwl:hasDbXref"
                           }
    dl = [robot_template_seed]

    for taxon_config in taxon_configs:
        d = dict()
        d['ID'] = 'AllenDend:' + taxon_config["Taxonomy_id"]
        d['TYPE'] = 'owl:NamedIndividual'
        d['Entity Type'] = 'BDSHELP:Taxonomy'
        d['Label'] = taxon_config["Taxonomy_id"]
        d['Anatomic Region'] = taxon_config['Brain_region'][0]
        d['Primary Citation'] = taxon_config['PMID'][0]
        if taxon_config["Taxonomy_id"] in taxonomies_metadata:
            taxonomy_metadata = taxonomies_metadata[taxon_config["Taxonomy_id"]]
            d['Number of Cell Types'] = taxonomy_metadata["Cell Types"]
            d['Number of Cell Subclasses'] = taxonomy_metadata["Cell Subclasses"]
            d['Number of Cell Classes'] = taxonomy_metadata["Cell Classes"]
            d['Species Label'] = taxonomy_metadata["Species"]
            d['Age'] = taxonomy_metadata["Age"]
            d['Sex'] = taxonomy_metadata["Sex"]

        dl.append(d)
    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_app_specific_template(taxonomy_file_path, output_filepath):
    if str(taxonomy_file_path).endswith(".json"):
        dend = dend_json_2_nodes_n_edges(taxonomy_file_path)
    else:
        dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)

    robot_template_seed = {'ID': 'ID',
                           'TYPE': 'TYPE',
                           'cell_set_color': "A ALLENHELP:cell_set_color"
                           }
    dl = [robot_template_seed]

    for o in dend['nodes']:
        if o["cell_set_color"]:
            d = dict()
            d['ID'] = 'AllenDend:' + o['cell_set_accession']
            d['TYPE'] = 'owl:NamedIndividual'
            d['cell_set_color'] = str(o["cell_set_color"]).strip()
            dl.append(d)

    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def index_taxonomies(taxonomies):
    index = list()
    for taxonomy in taxonomies:
        nomenclature_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         NOMENCLATURE_TABLE_PATH.format(taxonomy))
        headers, records = read_csv_to_dict(nomenclature_path, id_column_name="cell_set_aligned_alias",
                                            id_to_lower=True)
        index.append(records)

    return index


def merge_class_templates(base_tsv, curation_tsv, output_filepath):
    """
    Applies all columns of the curation_tsv to the base_tsv and generates a new merged class template in the
    output_filepath.
    Args:
        base_tsv: Path of the base table to add new columns.
        curation_tsv: Path of the manual curations' table
        output_filepath: Output file path
    """
    merge_tables(base_tsv, curation_tsv, output_filepath)
