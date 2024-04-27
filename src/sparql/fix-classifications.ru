#  Fix https://github.com/obophenotype/provisional_cell_ontology/issues/55
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

DELETE DATA
{
    <http://purl.obolibrary.org/obo/PCL_0015079> rdfs:subClassOf <http://purl.obolibrary.org/obo/CL_0002453> .
    <http://purl.obolibrary.org/obo/PCL_0015119> rdfs:subClassOf <http://purl.obolibrary.org/obo/CL_0002453> .
    <http://purl.obolibrary.org/obo/PCL_0015120> rdfs:subClassOf <http://purl.obolibrary.org/obo/CL_0002453> .
}