PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

DELETE {
    ?s1 ?p1 ?o1 .
}

WHERE {
    ?s1 a owl:Class .
    ?s1 ?p1 ?o1 .
    FILTER(!regex(str(?s1), "http://purl.obolibrary.org/obo/PCL_" ) )
    FILTER(!regex(str(?s1), "http://www.jcvi.org/framework/nsf2_full_mtg#" ) )
}