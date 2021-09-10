import pandas as pd
import json
import os
import logging

from dendrogram_tools import dend_json_2_nodes_n_edges
from template_generation_utils import get_synonyms_from_taxonomy, get_synonym_pairs, read_taxonomy_config, \
    get_subtrees, read_dendrogram_tree, get_dend_subtrees, index_dendrogram,\
    read_csv, read_ensemble_data, read_markers, get_gross_cell_type, merge_tables


log = logging.getLogger(__name__)

ALLEN_DEND_CLASS = 'http://www.semanticweb.org/brain_data_standards/AllenDendClass_'
ALLEN_DEND_INDV = 'http://www.semanticweb.org/brain_data_standards/AllenDend_'
ALLEN_DEND_INDV_PREFIX = 'AllenDend:'

MARKER_PATH = '../markers/CS{}_markers.tsv'
ALLEN_MARKER_PATH = "../markers/CS{}_Allen_markers.tsv"
NOMENCLATURE_TABLE_PATH = '../dendrograms/nomenclature_table_{}.csv'
ENSEMBLE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../templates/{}.tsv")

EXPRESSION_SEPARATOR = "|"


def generate_ind_template(dend_json_path, output_filepath):
    dend = dend_json_2_nodes_n_edges(dend_json_path)
    robot_template_seed = {'ID': 'ID',
                           'Label': 'LABEL',
                           'PrefLabel': 'A skos:prefLabel',
                           'Entity Type': 'TI %',
                           'TYPE': 'TYPE',
                           'Property Assertions': "I BDSHELP:subcluster_of SPLIT=|",
                           'Synonyms': 'A oboInOwl:hasExactSynonym',
                           'Function': 'TI capable_of some %',
                           'cell_set_preferred_alias': "A n2o:cell_set_preferred_alias",
                           'original_label': "A n2o:original_label",
                           'cell_set_label': "A n2o:cell_set_label",
                           'cell_set_aligned_alias': "A n2o:cell_set_aligned_alias",
                           'cell_set_additional_aliases': "A n2o:cell_set_additional_aliases SPLIT=|",
                           'cell_set_alias_assignee': "A n2o:cell_set_alias_assignee SPLIT=|",
                           'cell_set_alias_citation': "A n2o:cell_set_alias_citation SPLIT=|",
                           'Metadata': "A n2o:node_metadata",
                           'Exemplar_of': "TI exemplar_of some %"
                           }
    dl = [robot_template_seed]

    synonym_properties = ['original_label',
                          'cell_set_aligned_alias',
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
            d[prop] = o[prop] if prop in o.keys() else ''

        if o['cell_set_accession'] in set().union(*get_dend_subtrees(dend_json_path)) and o['cell_set_preferred_alias']:
            d['Exemplar_of'] = ALLEN_DEND_CLASS + o['cell_set_accession']

        # There should only be one!
        dl.append(d)
    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_base_class_template(dend_json_path, output_filepath):
    dend = dend_json_2_nodes_n_edges(dend_json_path)
    dend_tree = read_dendrogram_tree(dend_json_path)

    path_parts = dend_json_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

    taxonomy_config = read_taxonomy_config(taxon)

    marker_path = MARKER_PATH.format(str(taxon).replace("CCN", ""))
    allen_marker_path = ALLEN_MARKER_PATH.format(str(taxon).replace("CCN", ""))
    ensemble_path = ENSEMBLE_PATH.format(str(taxonomy_config["Ensemble_data"]).strip().lower())

    if taxonomy_config:
        subtrees = get_subtrees(dend_tree, taxonomy_config)
        ensmusg_names = read_ensemble_data(ensemble_path)
        minimal_markers = read_markers(marker_path, ensmusg_names)
        allen_markers = read_markers(allen_marker_path, ensmusg_names)

        robot_class_curation_seed = ['defined_class',
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
                                     'has_soma_location'
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
                    alias_citations = list()
                    for citation in str(o['cell_set_alias_citation']).split("|"):
                        if citation and citation.strip():
                            alias_citations.append("DOI:" + citation)
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

                for k in robot_class_curation_seed:
                    if not (k in d.keys()):
                        d[k] = ''
                class_template.append(d)

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_curated_class_template(dend_json_path, output_filepath):
    dend = dend_json_2_nodes_n_edges(dend_json_path)
    dend_tree = read_dendrogram_tree(dend_json_path)

    path_parts = dend_json_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        subtrees = get_subtrees(dend_tree, taxonomy_config)
        robot_class_curation_seed = ['defined_class',
                                     'Curated_synonyms',
                                     'Classification',
                                     'Classification_comment',
                                     'Classification_pub',
                                     'Expresses',
                                     'Expresses_comment',
                                     'Expresses_pub',
                                     'Projection_type',
                                     'Layers'
                                     ]
        class_template = []

        for o in dend['nodes']:
            if o['cell_set_accession'] in set.union(*subtrees) and (o['cell_set_preferred_alias'] or
                                                                    o['cell_set_additional_aliases']):
                d = dict()
                d['defined_class'] = ALLEN_DEND_CLASS + o['cell_set_accession']

                for k in robot_class_curation_seed:
                    if not (k in d.keys()):
                        d[k] = ''
                class_template.append(d)

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_non_taxonomy_classification_template(dend_json_path, output_filepath):
    dend = dend_json_2_nodes_n_edges(dend_json_path)
    dend_nodes = index_dendrogram(dend)

    path_parts = dend_json_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

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
                if columns[cell_set_accession] in dend_nodes:
                    raise Exception("Node {} exists both in dendrogram and nomenclature of the taxonomy: {}."
                                    .format(columns[cell_set_accession], taxon))
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
