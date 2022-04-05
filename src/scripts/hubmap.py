import os
import csv
import re
from rdflib import Graph
from template_generation_utils import read_csv_to_dict

NEW_COLUMN_INDEX = 25

HUBMAP_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          "../markers/raw/ASCT+B_Tables_Published_v1.0_v1.1 - Brain_v1.1.tsv")
PCL_CCN201912131_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                    "../patterns/data/default/CCN201912131_class_base.tsv")
HUBMAP_OUTPUT = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "../markers/raw/ASCT+B_Tables_Published_v1.0_v1.1 - Brain_v1.1-PCL.tsv")
PCL_ONTOLOGY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../bdso-full.owl")


def map_to_pcl():
    """
    Maps CT/1 value of the Hubmap table with the prefLabel of Human taxonomy (CCN201912131). Adds a PCL ID column after
    the CT/1 column.
    """
    hubmap_headers, hubmap_data = read_csv_to_dict(HUBMAP_TSV, delimiter="\t", generated_ids=True)
    headers, pcl_by_pref_label = read_csv_to_dict(PCL_CCN201912131_TSV, id_column=1, delimiter="\t")
    pcl_labels = get_pcl_labels()

    with open(HUBMAP_OUTPUT, mode='w') as out:
        writer = csv.writer(out, delimiter="\t", quotechar='"')
        new_headers = hubmap_headers.copy()
        new_headers.insert(NEW_COLUMN_INDEX, "PCL/ID")
        new_headers.insert(NEW_COLUMN_INDEX + 1, "PCL/LABEL")
        writer.writerow(new_headers)

        print(headers)
        for row_index in hubmap_data:
            row_data = hubmap_data[row_index]
            pcl_data = {}
            name_without_parentheses = re.sub(r'\([^)]*\)', '', row_data["CT/1"]).strip()
            pvalb_name = row_data["CT/1"].replace("PVALB", "PVALB-like")
            opalin_name = row_data["CT/1"].replace("OPALIN", "OPALIN-like")
            if row_data["CT/1"]:
                if row_data["CT/1"] in pcl_by_pref_label:
                    pcl_data = pcl_by_pref_label[row_data["CT/1"]]
                elif name_without_parentheses in pcl_by_pref_label:
                    pcl_data = pcl_by_pref_label[name_without_parentheses]
                elif pvalb_name in pcl_by_pref_label:
                    pcl_data = pcl_by_pref_label[pvalb_name]
                elif opalin_name in pcl_by_pref_label:
                    pcl_data = pcl_by_pref_label[opalin_name]
                elif row_data["CT/1"]:
                    print("Not Found:" + str(row_data["CT/1"]))
            new_row = []
            for header in hubmap_headers:
                new_row.append(row_data[header])

            if pcl_data:
                pcl_id = pcl_data["defined_class"]
                pcl_label = pcl_labels[pcl_id]
            else:
                pcl_id = ""
                pcl_label = ""
            new_row.insert(NEW_COLUMN_INDEX, pcl_id)
            new_row.insert(NEW_COLUMN_INDEX + 1, pcl_label)

            writer.writerow(new_row)


def get_pcl_labels():
    pcl_graph = Graph()
    pcl_graph.parse(PCL_ONTOLOGY)
    list_bds_entities = """
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    SELECT DISTINCT ?pclClass ?label 
    WHERE {
        ?pclClass a owl:Class .
        ?pclClass rdfs:label ?label .
        FILTER ( strstarts(str(?pclClass), "http://purl.obolibrary.org/obo/PCL_"))
    }"""
    qres = pcl_graph.query(list_bds_entities)
    pcl_labels = dict()
    for row in qres:
        pcl_labels[str(row.pclClass)] = row.label

    pcl_graph.close()
    return pcl_labels


map_to_pcl()
