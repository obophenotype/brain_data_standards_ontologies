PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>

INSERT {
    ?class owl:versionInfo ?versionStr .
    ?individual owl:versionInfo ?versionStr .
}
WHERE {
    ?ontology rdf:type owl:Ontology ;
        owl:versionIRI ?versionIRI .
    BIND (str(?versionIRI) AS ?versionStr)
#     # regex matches date and the previous text in the iri. When replaced, string after the date remains
#     BIND (REPLACE(str(?versionIRI), "^.*\\d{4}[\\-]\\d{2}[\\-]\\d{2}", "") AS ?dateTrailingStr)
#     # regex matches date and the trailing text in the iri. When replaced, string before the date remains
#     BIND (REPLACE(str(?versionIRI), "\\d{4}[\\-]\\d{2}[\\-]\\d{2}.*$", "") AS ?dateHeadingStr)
#     # replace heading and trailing text in the versionIRI to remain only the date
# #     BIND (REPLACE(str(?versionIRI), ?dateTrailingStr, "") AS ?versionSubStr)
# #     BIND (REPLACE(str(?versionSubStr), ?dateHeadingStr, "") AS ?versionStr)

    ?class rdf:type owl:Class .
    OPTIONAL { ?individual rdf:type owl:NamedIndividual . FILTER NOT EXISTS {?individual owl:versionInfo ?o1} }
    FILTER (!isBlank(?class))
    FILTER NOT EXISTS {?class owl:versionInfo ?o2}

    BIND (str(?class) AS ?classIRI)

    # regex matches any character before the last '/'.
    BIND (REPLACE(str(?classIRI), "^(.*[/])", "") AS ?class_simple_name)
    # regex matches any character after the '_'
    BIND (CONCAT(lcase(REPLACE(?class_simple_name, "_.*$", "")), ".owl") AS ?ont_name)
    # versionIRI contains ont_name (only own concepts, exclude imported ones)
    FILTER( REGEX(?versionStr, ?ont_name ))

}