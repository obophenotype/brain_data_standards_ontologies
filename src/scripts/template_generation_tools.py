import pandas as pd
import json
import os
import logging

from dendrogram_tools import dend_json_2_nodes_n_edges
from template_generation_utils import get_synonyms_from_taxonomy, read_taxonomy_config, \
    get_subtrees, generate_dendrogram_tree, read_taxonomy_details_yaml, read_csv_to_dict,\
    read_csv, read_gene_data, read_markers, get_gross_cell_type, merge_tables, read_allen_descriptions, \
    extract_taxonomy_name_from_path
from nomenclature_tools import nomenclature_2_nodes_n_edges
from pcl_id_factory import get_class_id, get_individual_id, get_taxonomy_id, get_dataset_id, get_marker_gene_set_id
from marker_tools import get_nsforest_confidences

log = logging.getLogger(__name__)


PCL_BASE = 'http://purl.obolibrary.org/obo/PCL_'
PCL_INDV_BASE = 'http://purl.obolibrary.org/obo/pcl/'

PCL_PREFIX = 'PCL:'

MARKER_PATH = '../markers/CS{}_markers.tsv'
ALLEN_MARKER_PATH = "../markers/CS{}_Allen_markers.tsv"
NOMENCLATURE_TABLE_PATH = '../dendrograms/nomenclature_table_{}.csv'
ENSEMBLE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../templates/{}.tsv")
CROSS_SPECIES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  "../dendrograms/nomenclature_table_CCN202002270.csv")

# centralized data files
ALLEN_DESCRIPTIONS_PATH = "{}/{}/All Descriptions_{}.json"
DATASET_INFO_CSV = "{}/{}/{}_landingpage_dataset_info.csv"
TAXONOMY_INFO_CSV = "{}/{}/{}_Taxonomy_Info_Panel.csv"
NSFOREST_MARKER_CSV = "{}/NSForestMarkers/{}_{}_NSForest_Markers.csv"

EXPRESSION_SEPARATOR = "|"


def generate_ind_template(taxonomy_file_path, centralized_data_folder, output_filepath):
    path_parts = taxonomy_file_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

    if str(taxonomy_file_path).endswith(".json"):
        dend = dend_json_2_nodes_n_edges(taxonomy_file_path)
    else:
        dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
        taxon = path_parts[len(path_parts) - 1].split(".")[0].replace("nomenclature_table_", "")

    dend_tree = generate_dendrogram_tree(dend)
    taxonomy_config = read_taxonomy_config(taxon)

    taxonomy_folder_name = get_centralized_taxonomy_folder(taxonomy_config)
    allen_desc_file = ALLEN_DESCRIPTIONS_PATH.format(centralized_data_folder, taxonomy_folder_name,
                                                     taxonomy_config['Species_abbv'][0])
    allen_descriptions = read_allen_descriptions(allen_desc_file)

    subtrees = get_subtrees(dend_tree, taxonomy_config)

    robot_template_seed = {'ID': 'ID',
                           'Label': 'LABEL',
                           'PrefLabel': 'A skos:prefLabel',
                           'Entity Type': 'TI %',
                           'TYPE': 'TYPE',
                           'Property Assertions': "I 'subcluster of' SPLIT=|",
                           'Synonyms': 'A oboInOwl:hasExactSynonym SPLIT=|',
                           'Cluster_ID': "A 'cluster id'",
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
                           'Rank': "A 'cell_type_rank' SPLIT=|"
                           }
    dl = [robot_template_seed]

    synonym_properties = ['cell_set_aligned_alias',
                          'cell_set_additional_aliases']

    for o in dend['nodes']:
        d = dict()
        d['ID'] = 'PCL_INDV:' + o['cell_set_accession']
        d['TYPE'] = 'owl:NamedIndividual'
        d['Label'] = o['cell_set_label'] + ' - ' + o['cell_set_accession']
        if 'cell_set_preferred_alias' in o and o['cell_set_preferred_alias']:
            d['PrefLabel'] = o['cell_set_preferred_alias']
        else:
            d['PrefLabel'] = o['cell_set_accession']
        d['Entity Type'] = 'PCL:0010001'  # Cluster
        d['Metadata'] = json.dumps(o)
        d['Synonyms'] = '|'.join([o[prop] for prop in synonym_properties if prop in o.keys() and o[prop]])
        d['Property Assertions'] = '|'.join(
            sorted(['PCL_INDV:' + e[1] for e in dend['edges'] if e[0] == o['cell_set_accession']]))
        meta_properties = ['cell_set_preferred_alias', 'original_label', 'cell_set_label', 'cell_set_aligned_alias',
                           'cell_set_additional_aliases', 'cell_set_alias_assignee', 'cell_set_alias_citation']
        for prop in meta_properties:
            if prop in o.keys():
                d[prop] = '|'.join([prop_val.strip() for prop_val in str(o[prop]).split("|") if prop_val])
            else:
                d[prop] = ''
        d['Cluster_ID'] = o['cell_set_accession']
        if o['cell_set_accession'] in set().union(*subtrees) and o['cell_set_preferred_alias']:
            d['Exemplar_of'] = PCL_BASE + get_class_id(o['cell_set_accession'])

        if "cell_type_card" in o:
            d['Rank'] = '|'.join([cell_type.strip().replace("No", "None")
                                  for cell_type in str(o["cell_type_card"]).split(",")])

        if o['cell_set_accession'] in allen_descriptions:
            allen_data = allen_descriptions[o['cell_set_accession']]
            d['Comment'] = allen_data["summary"][0]
            if allen_data["aliases"][0]:
                d['Aliases'] = '|'.join([alias.strip() for alias in str(allen_data["aliases"][0]).split("|")])

        dl.append(d)
    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_base_class_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        if str(taxonomy_file_path).endswith(".json"):
            dend = dend_json_2_nodes_n_edges(taxonomy_file_path)
        else:
            dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
        dend_tree = generate_dendrogram_tree(dend)
        subtrees = get_subtrees(dend_tree, taxonomy_config)

        if "Reference_gene_list" in taxonomy_config:
            gene_db_path = ENSEMBLE_PATH.format(str(taxonomy_config["Reference_gene_list"][0]).strip().lower())
            gene_names = read_gene_data(gene_db_path)
            minimal_markers = read_markers(MARKER_PATH.format(taxon.replace("CCN", "").replace("CS", "")), gene_names)
            allen_markers = read_markers(ALLEN_MARKER_PATH.format(taxon.replace("CCN", "").replace("CS", "")), gene_names)
        else:
            minimal_markers = {}
            allen_markers = {}

        class_seed = ['defined_class',
                      'prefLabel',
                      'Alias_citations',
                      'Synonyms_from_taxonomy',
                      'Gross_cell_type',
                      'Taxon',
                      'Taxon_abbv',
                      'Brain_region',
                      'Minimal_markers',
                      'Allen_markers',
                      'Individual',
                      'Brain_region_abbv',
                      'Species_abbv',
                      'Cluster_ID',
                      'part_of',
                      'has_soma_location',
                      'aligned_alias',
                      'marker_gene_set'
                      ]
        class_template = []

        for o in dend['nodes']:
            if o['cell_set_accession'] in set.union(*subtrees) and (o['cell_set_preferred_alias'] or
                                                                    o['cell_set_additional_aliases']):
                d = dict()
                d['defined_class'] = PCL_BASE + get_class_id(o['cell_set_accession'])
                if o['cell_set_preferred_alias']:
                    d['prefLabel'] = o['cell_set_preferred_alias']
                elif o['cell_set_additional_aliases']:
                    d['prefLabel'] = str(o['cell_set_additional_aliases']).split(EXPRESSION_SEPARATOR)[0]
                d['Synonyms_from_taxonomy'] = get_synonyms_from_taxonomy(o)
                d['Gross_cell_type'] = get_gross_cell_type(o['cell_set_accession'], subtrees, taxonomy_config)
                d['Taxon'] = taxonomy_config['Species'][0]
                d['Taxon_abbv'] = taxonomy_config['Gene_abbv'][0]
                d['Brain_region'] = taxonomy_config['Brain_region'][0]
                d['Cluster_ID'] = o['cell_set_accession']
                if 'cell_set_alias_citation' in o and o['cell_set_alias_citation']:
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
                d['Individual'] = PCL_INDV_BASE + o['cell_set_accession']

                for index, subtree in enumerate(subtrees):
                    if o['cell_set_accession'] in subtree:
                        location_rel = taxonomy_config['Root_nodes'][index]['Location_relation']
                        if location_rel == "part_of":
                            d['part_of'] = taxonomy_config['Brain_region'][0]
                            d['has_soma_location'] = ''
                        elif location_rel == "has_soma_location":
                            d['part_of'] = ''
                            d['has_soma_location'] = taxonomy_config['Brain_region'][0]

                if "cell_set_aligned_alias" in o and o["cell_set_aligned_alias"]:
                    d['aligned_alias'] = o["cell_set_aligned_alias"]
                if o['cell_set_accession'] in minimal_markers:
                    d['marker_gene_set'] = PCL_PREFIX + get_marker_gene_set_id(o['cell_set_accession'])

                for k in class_seed:
                    if not (k in d.keys()):
                        d[k] = ''
                class_template.append(d)

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_curated_class_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        if str(taxonomy_file_path).endswith(".json"):
            dend = dend_json_2_nodes_n_edges(taxonomy_file_path)
        else:
            dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
        dend_tree = generate_dendrogram_tree(dend)
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
                               'Cross_species_text',
                               'Comment'
                               ]
        class_template = []

        for o in dend['nodes']:
            if o['cell_set_accession'] in set.union(*subtrees) and (o['cell_set_preferred_alias'] or
                                                                    o['cell_set_additional_aliases']):
                d = dict()
                d['defined_class'] = PCL_BASE + get_class_id(o['cell_set_accession'])
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


def generate_homologous_to_template(taxonomy_file_path, all_base_files, output_filepath):
    """
    Homologous_to relations require a separate template. If this operation is driven by the nomenclature tables,
    some dangling classes may be generated due to root classes that don't have a class and should not be aligned.
    So, instead of nomenclature tables, base files are used for populating homologous to relations. This ensures all
    alignments has a corresponding class.
    Args:
        taxonomy_file_path: path of the taxonomy file
        all_base_files: paths of the all class template base files
        output_filepath: template output file path
    """
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    other_taxonomy_aliases = index_base_files([t for t in all_base_files if taxon not in t])

    if taxonomy_config:
        if str(taxonomy_file_path).endswith(".json"):
            dend = dend_json_2_nodes_n_edges(taxonomy_file_path)
        else:
            dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
        dend_tree = generate_dendrogram_tree(dend)
        subtrees = get_subtrees(dend_tree, taxonomy_config)

        data_template = []

        for o in dend['nodes']:
            if o['cell_set_accession'] in set.union(*subtrees) and (o['cell_set_preferred_alias'] or
                                                                    o['cell_set_additional_aliases']):
                d = dict()
                d['defined_class'] = PCL_BASE + get_class_id(o['cell_set_accession'])
                homologous_to = list()
                for other_aliases in other_taxonomy_aliases:
                    if "cell_set_aligned_alias" in o and o["cell_set_aligned_alias"] \
                            and str(o["cell_set_aligned_alias"]).lower() in other_aliases:
                        homologous_to.append(other_aliases[str(o["cell_set_aligned_alias"])
                                             .lower()]["defined_class"])
                d['homologous_to'] = "|".join(homologous_to)

                data_template.append(d)

        robot_template = pd.DataFrame.from_records(data_template)
        robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_non_taxonomy_classification_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)

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
                        d['defined_class'] = PCL_BASE + get_class_id(child)
                        d['Classification'] = non_taxo_roots[columns[cell_set_accession]]
                        nomenclature_template.append(d)

        class_robot_template = pd.DataFrame.from_records(nomenclature_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_cross_species_template(taxonomy_file_path, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        if str(taxonomy_file_path).endswith(".json"):
            dend = dend_json_2_nodes_n_edges(taxonomy_file_path)
        else:
            dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
        dend_tree = generate_dendrogram_tree(dend)
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
                    cross_species_classes.add(PCL_BASE + get_class_id(cs_by_aligned_alias[str(o["cell_set_aligned_alias"])
                                              .lower()]["cell_set_accession"]))

                if "cell_set_additional_aliases" in o and o["cell_set_additional_aliases"]:
                    additional_aliases = str(o["cell_set_additional_aliases"]).lower().split(EXPRESSION_SEPARATOR)
                    for additional_alias in additional_aliases:
                        if additional_alias in cs_by_preferred_alias:
                            cross_species_classes.add(PCL_BASE + get_class_id(
                                                      cs_by_preferred_alias[additional_alias]["cell_set_accession"]))

                if len(cross_species_classes):
                    d = dict()
                    d['defined_class'] = PCL_BASE + get_class_id(o['cell_set_accession'])
                    d['cross_species_classes'] = EXPRESSION_SEPARATOR.join(cross_species_classes)

                    cross_species_template.append(d)

        class_robot_template = pd.DataFrame.from_records(cross_species_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_taxonomies_template(centralized_data_folder, output_filepath):
    taxon_configs = read_taxonomy_details_yaml()

    robot_template_seed = {'ID': 'ID',
                           'TYPE': 'TYPE',
                           'Entity Type': 'TI %',
                           'Label': 'LABEL',
                           'Number of Cell Types': "A 'cell_types_count'",
                           'Number of Cell Subclasses': "A 'cell_subclasses_count'",
                           'Number of Cell Classes': "A 'cell_classes_count'",
                           'Anatomic Region': "A 'has_brain_region'",
                           'Species Label': "A skos:prefLabel",
                           'Age': "A 'has_age'",
                           'Sex': "A 'has_sex'",
                           'Primary Citation': "A oboInOwl:hasDbXref",
                           'Title': "A dcterms:title",
                           'Description': "A rdfs:comment",
                           'Attribution': "A dcterms:provenance",
                           'SubDescription': "A dcterms:description",
                           'Anatomy': "A dcterms:subject",
                           'Anatomy_image': "A dcterms:relation"
                           }
    dl = [robot_template_seed]

    for taxon_config in taxon_configs:
        d = dict()
        d['ID'] = 'PCL_INDV:' + taxon_config["Taxonomy_id"]
        d['TYPE'] = 'owl:NamedIndividual'
        d['Entity Type'] = 'PCL:0010002'  # Taxonomy
        d['Label'] = taxon_config["Taxonomy_id"]
        d['Anatomic Region'] = taxon_config['Brain_region'][0]
        d['Primary Citation'] = taxon_config['PMID'][0]

        add_taxonomy_info_panel_properties(centralized_data_folder, d, taxon_config)

        dl.append(d)
    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def add_taxonomy_info_panel_properties(centralized_data_folder, d, taxon_config):
    expected_folder_name = get_centralized_taxonomy_folder(taxon_config)
    taxonomy_metadata_path = TAXONOMY_INFO_CSV.format(centralized_data_folder, expected_folder_name,
                                                      taxon_config["Taxonomy_id"])
    print(taxonomy_metadata_path)
    if os.path.isfile(taxonomy_metadata_path):
        headers, taxonomies_metadata = read_csv_to_dict(taxonomy_metadata_path)
        taxonomy_metadata = taxonomies_metadata[taxon_config["Taxonomy_id"]]
        d['Number of Cell Types'] = taxonomy_metadata["Cell Types"]
        d['Number of Cell Subclasses'] = taxonomy_metadata["Cell Subclasses"]
        d['Number of Cell Classes'] = taxonomy_metadata["Cell Classes"]
        d['Species Label'] = taxonomy_metadata["Species"]
        d['Age'] = taxonomy_metadata["Age"]
        d['Sex'] = taxonomy_metadata["Sex"]
        d['Title'] = taxonomy_metadata["header"]
        d['Description'] = taxonomy_metadata["mainDescription"]
        d['Attribution'] = taxonomy_metadata["attribution"]
        d['SubDescription'] = taxonomy_metadata["subDescription"]
        d['Anatomy'] = taxonomy_metadata["Anatomy"]
        if "Anatomy_image" in taxonomy_metadata:
            d['Anatomy_image'] = taxonomy_metadata["Anatomy_image"]
    else:
        raise ValueError("Couldn't find taxonomy '{}' landingpage dataset info file at: '{}'"
                         .format(taxon_config["Taxonomy_id"], taxonomy_metadata_path))


def generate_datasets_template(centralized_data_folder, output_filepath):
    path_parts = output_filepath.split(os.path.sep)
    taxonomy_id = str(path_parts[len(path_parts) - 1]).split("_")[0]
    taxonomy_config = read_taxonomy_config(taxonomy_id)

    expected_file_name = DATASET_INFO_CSV.format(centralized_data_folder,
                                                 get_centralized_taxonomy_folder(taxonomy_config), taxonomy_id)

    if os.path.isfile(expected_file_name):
        headers, dataset_metadata = read_csv_to_dict(expected_file_name, generated_ids=True)

        robot_template_seed = {'ID': 'ID',
                               'TYPE': 'TYPE',
                               'Entity Type': 'TI %',
                               'Label': 'LABEL',
                               'PrefLabel': 'A skos:prefLabel',
                               'Symbol': 'A IAO:0000028',
                               'Taxonomy': 'AI schema:includedInDataCatalog',
                               'Cell Count': "AT 'cell_count'^^xsd:integer",
                               'Nuclei Count': "AT 'nuclei_count'^^xsd:integer",
                               'Dataset': "A schema:headline",
                               'Species': "A schema:assesses",
                               'Region': "A schema:position",
                               'Description': "A rdfs:comment",
                               'Download Link': "A schema:archivedAt",
                               'Explore Link': "A schema:discussionUrl"
                               }
        dl = [robot_template_seed]

        dataset_index = 0
        for dataset in dataset_metadata:
            d = dict()
            d['ID'] = 'PCL:' + get_dataset_id(taxonomy_id, dataset_index)
            d['TYPE'] = 'owl:NamedIndividual'
            d['Entity Type'] = 'schema:Dataset'  # Taxonomy
            d['Label'] = dataset_metadata[dataset]['Ontology Name']
            d['PrefLabel'] = dataset_metadata[dataset]['Dataset']
            d['Symbol'] = dataset_metadata[dataset]['Ontology Symbol']
            d['Taxonomy'] = 'PCL_INDV:' + taxonomy_id
            cells_nuclei = dataset_metadata[dataset]['cells/nuclei']
            if 'nuclei' in cells_nuclei:
                d['Nuclei Count'] = int(''.join(c for c in cells_nuclei if c.isdigit()))
            elif 'cells' in cells_nuclei:
                d['Cell Count'] = int(''.join(c for c in cells_nuclei if c.isdigit()))
            d['Dataset'] = dataset_metadata[dataset]['dataset_number']
            d['Species'] = dataset_metadata[dataset]['species']
            d['Region'] = dataset_metadata[dataset]['region']
            d['Description'] = dataset_metadata[dataset]['text']
            d['Download Link'] = dataset_metadata[dataset]['download_link']
            d['Explore Link'] = dataset_metadata[dataset]['explore_link']

            dataset_index += 1
            dl.append(d)
        robot_template = pd.DataFrame.from_records(dl)
        robot_template.to_csv(output_filepath, sep="\t", index=False)
    else:
        raise ValueError("Couldn't find taxonomy '{}' landingpage dataset info file at: '{}'"
                         .format(taxonomy_id, expected_file_name))


def generate_marker_gene_set_template(taxonomy_file_path, centralized_data_folder, output_filepath):
    taxon = extract_taxonomy_name_from_path(taxonomy_file_path)
    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        if str(taxonomy_file_path).endswith(".json"):
            dend = dend_json_2_nodes_n_edges(taxonomy_file_path)
        else:
            dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
        dend_tree = generate_dendrogram_tree(dend)
        subtrees = get_subtrees(dend_tree, taxonomy_config)

        if "Reference_gene_list" in taxonomy_config:
            gene_db_path = ENSEMBLE_PATH.format(str(taxonomy_config["Reference_gene_list"][0]).strip().lower())
            gene_names = read_gene_data(gene_db_path)
            minimal_markers = read_markers(MARKER_PATH.format(taxon.replace("CCN", "").replace("CS", "")), gene_names)
        else:
            minimal_markers = {}

        ns_forest_marker_file = NSFOREST_MARKER_CSV.format(centralized_data_folder,
                                                           taxonomy_config['Species_abbv'][0],
                                                           taxonomy_config['Brain_region_abbv'][0])
        confidences = get_nsforest_confidences(taxon, dend, ns_forest_marker_file)

        class_seed = ['defined_class',
                      'Marker_set_of',
                      'Minimal_markers',
                      'Brain_region_abbv',
                      'Species_abbv',
                      'Brain_region',
                      'Parent',
                      'FBeta_confidence_score'
                      ]
        class_template = []

        for o in dend['nodes']:
            if o['cell_set_accession'] in set.union(*subtrees) and (o['cell_set_preferred_alias'] or
                                                                    o['cell_set_additional_aliases']):
                if o['cell_set_accession'] in minimal_markers:
                    d = dict()
                    d['defined_class'] = PCL_BASE + get_marker_gene_set_id(o['cell_set_accession'])
                    d['Marker_set_of'] = o['cell_set_preferred_alias']
                    d['Minimal_markers'] = minimal_markers[o['cell_set_accession']]
                    if 'Brain_region_abbv' in taxonomy_config:
                        d['Brain_region_abbv'] = taxonomy_config['Brain_region_abbv'][0]
                    if 'Species_abbv' in taxonomy_config:
                        d['Species_abbv'] = taxonomy_config['Species_abbv'][0]
                    d['Brain_region'] = taxonomy_config['Brain_region'][0]
                    d['Parent'] = "SO:0001260"  # sequence collection
                    if o['cell_set_accession'] in confidences:
                        d['FBeta_confidence_score'] = confidences[o['cell_set_accession']]

                    for k in class_seed:
                        if not (k in d.keys()):
                            d[k] = ''
                    class_template.append(d)

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


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
        if "cell_set_color" in o and o["cell_set_color"]:
            d = dict()
            d['ID'] = 'PCL_INDV:' + o['cell_set_accession']
            d['TYPE'] = 'owl:NamedIndividual'
            d['cell_set_color'] = str(o["cell_set_color"]).strip()
            dl.append(d)

    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_obsolete_ind_template(taxonomy_file_path, centralized_data_folder, output_filepath):
    """
    Individuals with PCL IDs are obsoleted (now using accession ID)
    Args:
        taxonomy_file_path:
        centralized_data_folder:
        output_filepath:

    Returns:
    """
    path_parts = taxonomy_file_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

    if str(taxonomy_file_path).endswith(".json"):
        dend = dend_json_2_nodes_n_edges(taxonomy_file_path)
    else:
        dend = nomenclature_2_nodes_n_edges(taxonomy_file_path)
        taxon = path_parts[len(path_parts) - 1].split(".")[0].replace("nomenclature_table_", "")

    dend_tree = generate_dendrogram_tree(dend)
    taxonomy_config = read_taxonomy_config(taxon)

    taxonomy_folder_name = get_centralized_taxonomy_folder(taxonomy_config)
    allen_desc_file = ALLEN_DESCRIPTIONS_PATH.format(centralized_data_folder, taxonomy_folder_name,
                                                     taxonomy_config['Species_abbv'][0])
    allen_descriptions = read_allen_descriptions(allen_desc_file)

    robot_template_seed = {'ID': 'ID',
                           'Label': 'LABEL',
                           'PrefLabel': 'A skos:prefLabel',
                           'Obsoleted By': 'AI obo:IAO_0100001',
                           'Obsolete': 'AT owl:deprecated^^xsd:boolean',
                           'Entity Type': 'TI %',
                           'TYPE': 'TYPE',
                           'Synonyms': 'A oboInOwl:hasExactSynonym SPLIT=|',
                           'Cluster_ID': "A 'cluster id'",
                           'cell_set_preferred_alias': "A n2o:cell_set_preferred_alias",
                           'original_label': "A n2o:original_label",
                           'cell_set_label': "A n2o:cell_set_label",
                           'cell_set_aligned_alias': "A n2o:cell_set_aligned_alias",
                           'cell_set_additional_aliases': "A n2o:cell_set_additional_aliases SPLIT=|",
                           'cell_set_alias_assignee': "A n2o:cell_set_alias_assignee SPLIT=|",
                           'cell_set_alias_citation': "A n2o:cell_set_alias_citation SPLIT=|",
                           'Metadata': "A n2o:node_metadata",
                           'Comment': "A rdfs:comment",
                           'Aliases': "A oboInOwl:hasRelatedSynonym SPLIT=|",
                           'Rank': "A 'cell_type_rank' SPLIT=|"
                           }
    dl = [robot_template_seed]

    synonym_properties = ['cell_set_aligned_alias',
                          'cell_set_additional_aliases']

    for o in dend['nodes']:
        d = dict()
        d['ID'] = 'PCL:' + get_individual_id(o['cell_set_accession'])
        d['TYPE'] = 'owl:NamedIndividual'
        d['Comment'] = 'This term has been obsoleted and replaced with updated by an updated term from the ' \
                       'Brain Data Standards ontology, please see \'term replaced by\' axiom to for the new term.'
        d['Obsoleted By'] = 'PCL_INDV:' + o['cell_set_accession']
        d['Obsolete'] = 'true'
        d['Label'] = 'obsolete ' + o['cell_set_label'] + ' - ' + o['cell_set_accession']
        if 'cell_set_preferred_alias' in o and o['cell_set_preferred_alias']:
            d['PrefLabel'] = 'obsolete ' + o['cell_set_preferred_alias']
        else:
            d['PrefLabel'] = 'obsolete ' + o['cell_set_accession']
        d['Entity Type'] = 'PCL:0010001'  # Cluster
        d['Metadata'] = json.dumps(o)
        d['Synonyms'] = '|'.join([o[prop] for prop in synonym_properties if prop in o.keys() and o[prop]])
        meta_properties = ['cell_set_preferred_alias', 'original_label', 'cell_set_label', 'cell_set_aligned_alias',
                           'cell_set_additional_aliases', 'cell_set_alias_assignee', 'cell_set_alias_citation']
        for prop in meta_properties:
            if prop in o.keys():
                d[prop] = '|'.join([prop_val.strip() for prop_val in str(o[prop]).split("|") if prop_val])
            else:
                d[prop] = ''
        d['Cluster_ID'] = o['cell_set_accession']

        if "cell_type_card" in o:
            d['Rank'] = '|'.join([cell_type.strip().replace("No", "None")
                                  for cell_type in str(o["cell_type_card"]).split(",")])

        if o['cell_set_accession'] in allen_descriptions:
            allen_data = allen_descriptions[o['cell_set_accession']]
            if allen_data["aliases"][0]:
                d['Aliases'] = '|'.join([alias.strip() for alias in str(allen_data["aliases"][0]).split("|")])

        dl.append(d)

    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_obsolete_taxonomies_template(centralized_data_folder, output_filepath):
    """
    Taxonomy nodes with PCL IDs are obsoleted (now using accession ID)
    """
    taxon_configs = read_taxonomy_details_yaml()

    robot_template_seed = {'ID': 'ID',
                           'TYPE': 'TYPE',
                           'Entity Type': 'TI %',
                           'Label': 'LABEL',
                           'Obsoleted By': 'AI obo:IAO_0100001',
                           'Obsolete': 'AT owl:deprecated^^xsd:boolean',
                           'Comment': "A rdfs:comment",
                           'Anatomic Region': "A 'has_brain_region'",
                           'Primary Citation': "A oboInOwl:hasDbXref"
                           }
    dl = [robot_template_seed]

    for taxon_config in taxon_configs:
        d = dict()
        d['ID'] = 'PCL:' + get_taxonomy_id(taxon_config["Taxonomy_id"])
        d['TYPE'] = 'owl:NamedIndividual'
        d['Entity Type'] = 'PCL:0010002'  # Taxonomy
        d['Label'] = 'obsolete ' + taxon_config["Taxonomy_id"]
        d['Comment'] = 'This term has been obsoleted and replaced with updated by an updated term from the ' \
                       'Brain Data Standards ontology, please see \'term replaced by\' axiom to for the new term.'
        d['Obsoleted By'] = 'PCL_INDV:' + taxon_config["Taxonomy_id"]
        d['Obsolete'] = 'true'
        d['Anatomic Region'] = taxon_config['Brain_region'][0]
        d['Primary Citation'] = taxon_config['PMID'][0]
        dl.append(d)
    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def index_base_files(base_files):
    index = list()
    for base_file in base_files:
        headers, records = read_csv_to_dict(base_file, delimiter="\t", id_column_name="aligned_alias",
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


def get_centralized_taxonomy_folder(taxonomy_config):
    """
    Expected folder name is: lower(Species_abbv) + Brain_region_abbv + "_" + Taxonomy_id
    Args:
        taxonomy_config: taxonomy configuration

    Returns: expected centralized data location for the given taxonomy
    """
    return str(taxonomy_config['Species_abbv'][0]).lower() + taxonomy_config['Brain_region_abbv'][0] \
           + "_" + taxonomy_config["Taxonomy_id"]
