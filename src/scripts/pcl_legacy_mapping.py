import os
import pandas as pd
from rdflib import Graph

BDSO_ONT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../bdso-full.owl")
PCL_ONT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../resources/pCL_4.1.0.owl")
PCL_MAPPING_OUTPUT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../templates/pCL_mapping.tsv")


def map_pcl_2_bdso():
    bdso_preflabels = get_bdso_pref_labels()

    robot_template_seed = {'ID': 'ID',
                           'Synonym': 'A obo:PCL_0000100',
                           'Pref Name': 'A jcvi:preferred_name',
                           'Obsoleted By': 'AI obo:IAO_0100001',
                           'Obselete': 'AT owl:deprecated^^xsd:boolean',
                           'Comment': "A rdfs:comment",
                           'Label': "A rdfs:label",
                           'Definition': 'A skos:definition'
                           }
    dl = [robot_template_seed]

    g, legacy_entities = query_legacy_entities()
    for row in legacy_entities:
        d = dict()
        d["ID"] = row.pclClass
        if row.synonym:
            d["Synonym"] = row.synonym
        else:
            d["Synonym"] = ""
        d["Pref Name"] = row.preferred_name
        if row.synonym:
            if str(row.synonym).lower() in bdso_preflabels:
                d["Obsoleted By"] = bdso_preflabels[str(row.synonym).lower()]
            else:
                d["Obsoleted By"] = ""
        else:
            if "http://www.jcvi.org/framework/nsf2_full_mtg#CL_" in str(row.pclClass):
                d["Obsoleted By"] = str(row.pclClass).replace("http://www.jcvi.org/framework/nsf2_full_mtg#CL_",
                                                              "http://purl.obolibrary.org/obo/CL_")
            elif "http://www.jcvi.org/framework/nsf2_full_mtg#UBERON_" in str(row.pclClass):
                d["Obsoleted By"] = str(row.pclClass).replace("http://www.jcvi.org/framework/nsf2_full_mtg#UBERON_",
                                                              "http://purl.obolibrary.org/obo/UBERON_")
            else:
                d["Obsoleted By"] = ""

        d['Obselete'] = "true"
        d["Comment"] = "This term has been obsoleted and replaced with updated by an updated term from the " \
                       "Brain Data Standards ontology, please see 'term replaced by' axiom to for new term."
        if row.label:
            d["Label"] = "obsolete " + row.label
        else:
            d["Label"] = "obsolete"
        if row.definition:
            d["Definition"] = "OBSOLETE. " + row.definition
        else:
            d["Definition"] = "OBSOLETE"

        dl.append(d)

    g.close()
    robot_template = pd.DataFrame.from_records(dl)
    robot_template.to_csv(PCL_MAPPING_OUTPUT, sep="\t", index=False)


def query_legacy_entities():
    g = Graph()
    g.parse(PCL_ONT)
    list_entities = """
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX jcvi: <http://www.jcvi.org/framework/nsf2_full_mtg#>
    SELECT DISTINCT ?pclClass ?synonym ?preferred_name ?label ?definition
    WHERE {
        ?pclClass a owl:Class .
        OPTIONAL {?pclClass obo:PCL_0000100 ?synonym} .
        OPTIONAL {?pclClass jcvi:preferred_name ?preferred_name} .
        OPTIONAL {?pclClass rdfs:label ?label} .
        OPTIONAL {?pclClass skos:definition ?definition} .
        FILTER ( strstarts(str(?pclClass), "http://www.jcvi.org/framework/nsf2_full_mtg#")
                ||  strstarts(str(?pclClass), "http://purl.obolibrary.org/obo/PCL_") )
    }"""
    qres = g.query(list_entities)
    return g, qres


def get_bdso_pref_labels():
    bdso_graph = Graph()
    bdso_graph.parse(BDSO_ONT)
    list_bds_entities = """
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    SELECT DISTINCT ?bdsoClass ?prefLabel 
    WHERE {
        ?bdsoClass a owl:Class .
        ?bdsoClass skos:prefLabel ?prefLabel .
        FILTER ( strstarts(str(?bdsoClass), "http://purl.obolibrary.org/obo/PCL_"))
    }"""
    qres = bdso_graph.query(list_bds_entities)
    bdso_preflabels = dict()
    for row in qres:
        if str(row.prefLabel).lower() not in bdso_preflabels:
            bdso_preflabels[str(row.prefLabel).lower()] = row.bdsoClass
        else:
            print("!!!!  " + str(row.prefLabel).lower() + " exists multiple times in the ontology: " +
                  str(row.bdsoClass) + " and " + str(bdso_preflabels[str(row.prefLabel).lower()]))

    bdso_graph.close()
    return bdso_preflabels


if __name__ == '__main__':
    map_pcl_2_bdso()
