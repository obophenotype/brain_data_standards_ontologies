import pandas as pd
import uuid
from dendrogram_tools import dend_json_2_nodes_n_edges

def generate_ind_template(dend_json_path, output_filepath):
    dend = dend_json_2_nodes_n_edges(dend_json_path)
    robot_template_seed = {'ID': 'ID',
                           'Label': 'LABEL',
                           'PrefLabel': 'A skos:prefLabel',
                           'Entity Type': 'TI %',
                           'TYPE': 'TYPE',
                           'Property Assertions': "I BDSHELP:subcluster_of SPLIT='|'",
                           'Synonyms': 'A oboInOwl:has_exact_synonym',
                           'Function': 'TI capable_of some %'
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
        d['Synonyms'] = '|'.join([o[prop] for prop in synonym_properties if
                                  prop in o.keys() and o[prop]])
        d['Property Assertions'] = '|'.join(
            ['AllenDend:' + e[1] for e in dend['edges'] if e[0] == o['cell_set_accession']])
        # There should only be one!
        dl.append(d)
    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(output_filepath, sep="\t", index=False)


def generate_curated_class_template(dend_json_path, output_filepath):
    dend = dend_json_2_nodes_n_edges(dend_json_path)
    robot_class_curation_seed = {'ID': 'ID',
                                 'Label': 'LABEL',
                                 'PrefLabel': 'A skos:prefLabel',
                                 'Synonyms': 'A oboInOwl:has_exact_synonym',
                                 'Exemplar': "EC CL:0000003 and 'has_exemplar' value %",
                                 'Classification': 'SC %',
                                 'Comment': 'A rdfs:comment',
                                 'part of': "SC 'part of' some %",
                                 'part evidence comment': '>A rdfs:comment',
                                 'part evidence pub': ">A dc:reference SPLIT='|'",  # Bundle this with dbxrefs?
                                 'part evidence dbxref': ">A oio:hasDbXref SPLIT='|'",
                                 'location': "SC 'located in' some %",
                                 'location evidence comment': '>A rdfs:comment',
                                 'location evidence pub': ">A dc:reference SPLIT='|'",  # Bundle this with dbxrefs?
                                 'location evidence dbxref': ">A oio:hasDbXref SPLIT='|'",
                                 'has soma location': "SC 'has soma location' some %",
                                 'soma location evidence comment': '>A rdfs:comment',
                                 'soma location evidence pub': ">A dc:reference SPLIT='|'",  # Bundle this with dbxrefs?
                                 'soma location evidence dbxref': ">A oio:dbxref SPLIT='|'",
                                 'cell morphology phenotype': "SC 'bearer of' some %",
                                 'cell morphology evidence comment': '>A rdfs:comment',
                                 'cell morphology evidence pub': ">A dc:reference SPLIT='|'",  # Bundle this with dbxrefs?
                                 'cell morphology evidence dbxref': ">A oio:hasDbXref SPLIT='|'"
                                 }
    class_template = [robot_class_curation_seed]

    # not bothering with stable IDs for now:

    for o in dend['nodes']:
        ID = 'http://brain_data_standards/scratch_' + str(uuid.uuid1())
        d = dict()
        d['ID'] = ID
        d['Class_type'] = 'subclass'
        d['Exemplar'] = 'AllenDend:' + o['cell_set_accession']
        if o['cell_set_label']:
            d['Label'] = o['cell_set_label']
        if o['cell_set_preferred_alias']:
            d['PrefLabel'] = o['cell_set_preferred_alias']
        for k in robot_class_curation_seed.keys():
            if not (k in d.keys()):
                d[k] = ''
        class_template.append(d)

    class_robot_template = pd.DataFrame.from_records(class_template)
    class_robot_template.to_csv(output_filepath, sep="\t", index=False)







