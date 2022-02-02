prefix owl: <http://www.w3.org/2002/07/owl#>
prefix oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix RO: <http://purl.obolibrary.org/obo/RO_>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix skos: <http://www.w3.org/2004/02/skos/core#>


DELETE {
  ?s ?p ?o
}
WHERE 
{ 
  {
    VALUES ?p {
      skos:prefLabel
    }
  ?s a owl:Class ;
  ?p ?o
    FILTER (isIRI(?s) && STRSTARTS(str(?s), "http://purl.obolibrary.org/obo/PCL_"))
  }
}
