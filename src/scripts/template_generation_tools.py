import pandas as pd
import json
import os

from dendrogram_tools import dend_json_2_nodes_n_edges
from template_generation_utils import get_synonyms_from_taxonomy, get_synonym_pairs, get_root_nodes, \
    get_max_marker_count, read_taxonomy_config, get_subtrees
from marker_tools import read_dendrogram_tree, read_marker_file, extend_expressions, EXPRESSIONS, EXPRESSION_SEPARATOR

# TODO - refactor with generic template generation function


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
                           'Metadata': "A n2o:node_metadata"
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

        # There should only be one!
        dl.append(d)
    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_curated_class_template(dend_json_path, output_filepath):
    dend = dend_json_2_nodes_n_edges(dend_json_path)
    dend_tree = read_dendrogram_tree(dend_json_path)

    path_parts = dend_json_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        subtrees = get_subtrees(dend_tree, taxonomy_config)
        robot_class_curation_seed = {'ID': 'ID',
                                     'prefLabel': 'A skos:prefLabel',
                                     'Synonyms_from_taxonomy': "A oboInOwl:hasExactSynonym SPLIT=|",
                                     'Curated_synonyms': "A oboInOwl:hasExactSynonym SPLIT=|",
                                     'Comment': 'A rdfs:comment',
                                     'Classification': 'SC %',
                                     'Classification_comment': ">A rdfs:comment",
                                     'Classification_pub': ">A oboInOwl:hasDbXref SPLIT=|"
                                     }
        class_template = [robot_class_curation_seed]

        for o in dend['nodes']:
            if o['cell_set_accession'] in set.union(*subtrees) and o['cell_set_preferred_alias']:
                d = dict()
                d['ID'] = 'http://www.semanticweb.org/brain_data_standards/AllenDendClass_' + o['cell_set_accession']
                if o['cell_set_preferred_alias']:
                    d['prefLabel'] = o['cell_set_preferred_alias']
                d['Synonyms_from_taxonomy'] = get_synonyms_from_taxonomy(o)
                d['Comment'] = get_synonym_pairs(o)
                for k in robot_class_curation_seed.keys():
                    if not (k in d.keys()):
                        d[k] = ''
                class_template.append(d)

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_equivalent_class_reification_template(dend_json_path, output_filepath):
    dend = dend_json_2_nodes_n_edges(dend_json_path)
    dend_tree = read_dendrogram_tree(dend_json_path)

    path_parts = dend_json_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]
    config_yaml = read_taxonomy_config(taxon)

    subtrees = get_subtrees(dend_tree, config_yaml)

    robot_class_equivalent_seed = {'ID': 'ID',
                                   'Exemplar': "EC CL:0000003 and 'has_exemplar' value %"
                                   }

    equivalent_template = [robot_class_equivalent_seed]

    for o in dend['nodes']:
        if o['cell_set_accession'] in set().union(*subtrees) and o['cell_set_preferred_alias']:
            d = dict()
            d['ID'] = 'http://www.semanticweb.org/brain_data_standards/AllenDendClass_' + o['cell_set_accession']
            d['Exemplar'] = 'AllenDend:' + o['cell_set_accession']
            equivalent_template.append(d)

    equivalent_robot_template = pd.DataFrame.from_records(equivalent_template)
    equivalent_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_equivalent_class_marker_template(dend_json_path, marker_path, output_filepath):
    dend = dend_json_2_nodes_n_edges(dend_json_path)
    dend_tree = read_dendrogram_tree(dend_json_path)

    path_parts = dend_json_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]
    config_yaml = read_taxonomy_config(taxon)

    subtrees = get_subtrees(dend_tree, config_yaml)
    root_nodes = get_root_nodes(config_yaml)

    denormalized_markers = extend_expressions(dend_tree, read_marker_file(marker_path), root_nodes)

    robot_class_equivalent_seed = {'ID': 'ID',
                                   'CLASS_TYPE': 'CLASS_TYPE',
                                   # 'Definition': 'A IAO:0000115',
                                   'Evidence': 'AI RO:0002558',
                                   'Gross_cell_type': 'C %',
                                   'Brain_region': "C 'has soma location' some %"
                                   # 'Brain_region': "C {} some %".format(config_yaml
                                   #                                      ['Root_nodes'][0]['Location_relation'])
                                   }

    for i in range(get_max_marker_count(denormalized_markers)):
        robot_class_equivalent_seed['Marker' + str(i+1)] = "C expresses some %"

    equivalent_template = [robot_class_equivalent_seed]

    for o in dend['nodes']:
        if o['cell_set_accession'] in set().union(*subtrees) and o['cell_set_accession'] in denormalized_markers.keys():
            d = dict()
            d['ID'] = 'http://www.semanticweb.org/brain_data_standards/AllenDendClass_' + o['cell_set_accession']
            d['CLASS_TYPE'] = 'equivalent'
            d['Evidence'] = 'http://www.semanticweb.org/brain_data_standards/AllenDend_' + o['cell_set_accession']

            for index, subtree in enumerate(subtrees):
                if o['cell_set_accession'] in subtree:
                    d['Gross_cell_type'] = config_yaml['Root_nodes'][index]['Cell_type']

            d['Brain_region'] = config_yaml['Brain_region'][0]
            # d['Definition'] = "A {Gross_cell_type} with a soma in the {Brain_region}, which expresses: " \
            #                   "".format(Gross_cell_type=d['Gross_cell_type'], Brain_region=d['Brain_region']) \
            #                   + ' and '.join(denormalized_markers[o['cell_set_accession']][EXPRESSIONS])

            for index, marker in enumerate(denormalized_markers[o['cell_set_accession']][EXPRESSIONS], start=1):
                d['Marker' + str(index)] = marker

            equivalent_template.append(d)

    equivalent_robot_template = pd.DataFrame.from_records(equivalent_template)
    equivalent_robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_minimal_marker_template(dend_json_path, flat_marker_path, output_marker_path):
    marker_expressions = read_marker_file(flat_marker_path)

    dend = dend_json_2_nodes_n_edges(dend_json_path)
    dend_tree = read_dendrogram_tree(dend_json_path)

    path_parts = dend_json_path.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0]

    taxonomy_config = read_taxonomy_config(taxon)

    if taxonomy_config:
        subtrees = get_subtrees(dend_tree, taxonomy_config)
        robot_class_curation_seed = {'ID': "ID",
                                     'Markers': "SC 'expresses' some % SPLIT=|",
                                     'part_of': "SC 'part of' some %",
                                     'has_soma_location': "SC 'has soma location' some %",
                                     'gross_cell_type': "SC %"
                                     }
        class_template = [robot_class_curation_seed]

        for o in dend['nodes']:
            if o['cell_set_accession'] in set.union(*subtrees) and o['cell_set_preferred_alias'] and \
                    o['cell_set_accession'] in marker_expressions:
                d = dict()
                d['ID'] = 'http://www.semanticweb.org/brain_data_standards/AllenDendClass_' + o['cell_set_accession']
                d['Markers'] = EXPRESSION_SEPARATOR.join(marker_expressions[o['cell_set_accession']][EXPRESSIONS])
                class_template.append(d)

                for index, subtree in enumerate(subtrees):
                    if o['cell_set_accession'] in subtree:
                        location_rel = taxonomy_config['Root_nodes'][index]['Location_relation']
                        if location_rel == "part_of":
                            d['part_of'] = taxonomy_config['Brain_region'][0]
                            d['has_soma_location'] = ''
                        elif location_rel == "has_soma_location":
                            d['part_of'] = ''
                            d['has_soma_location'] = taxonomy_config['Brain_region'][0]

                for index, subtree in enumerate(subtrees):
                    if o['cell_set_accession'] in subtree:
                        d['gross_cell_type'] = taxonomy_config['Root_nodes'][index]['Cell_type']

        class_robot_template = pd.DataFrame.from_records(class_template)
        class_robot_template.to_csv(output_marker_path, sep="\t", index=False)

