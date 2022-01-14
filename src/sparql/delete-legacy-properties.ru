PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

DELETE {
    ?s1 owl:equivalentClass ?eq .
    ?s1 rdfs:subClassOf ?parent .
    ?s1 rdfs:label ?label .
    ?s1 skos:definition ?definition
}

WHERE {
    ?s1 a owl:Class .
    OPTIONAL { ?s1 owl:equivalentClass ?eq . }
    OPTIONAL { ?s1 rdfs:subClassOf ?parent . }
    OPTIONAL { ?s1 rdfs:label ?label . }
    OPTIONAL { ?s1 skos:definition ?definition }
}