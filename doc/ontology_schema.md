## Brain Data Standards Ontology schema

Status: Draft

Last updates: 2nd January 2021

### Taxonomy in OWL 

**iri schema:**

IRIs are derived from Allen Dendrogram node names

Current (temporary) solution: 

CS201810310_140
->
http://www.semanticweb.org/brain_data_standards/AllenDend_CS201810310_140

Warning - this scheme will change once the Allen releases it's own IRI scheme.

**Logic:**

Dendrograms nodes are represented as OWL individuals, classified as cell clusters, and stand in **subcluster_of** relationships (OPA) to each other.

**Annotations:**

rdfs:label = 

skos:preflabel = 

OboInOwl:ExactSynonym = 

e.g. 

![image](https://user-images.githubusercontent.com/112839/103462929-a061fa80-4d20-11eb-928c-6f2b7d2ece7f.png)


The **subcluster_of** objectProperty is currently a custom object property for this project.  This should be generalised.

### Data Driven Classes

**iri schema:**

We are currently using (unstable!) UUIDs.  This is a temporary expedient.  Proposed change: switch to dendrogram node ID derived scheme.  Once the ontology is sufficiently mature, these will be deprecated and replaced by CL IDs/IRIs with standard mapping.

**logic:**

Each class is EquivalentTo: cell and (has_exemplar value {dendogram node Individual})

When combined with the property chain axiom: subcluster_of o has_exemplar -> has_exemplar 

Reasoning => classification following the dendogram

### Property driven classification

All terms get a taxon restriction (in_taxon some {NCBI_taxon}) and a has_soma_location relationship to the relevant brain region.

Additional subclassing axioms name CL parent classes or use simple anonymous class expressions to name classes.

### Markers

Genes are modelled as classes

Marker genes are related to Individuals via expresses, eg. 

![image](https://user-images.githubusercontent.com/112839/103463220-c1c3e600-4d22-11eb-9641-d3c1f1f1a8a2.png)

TBD: Add axioms to bridge these markers from Individuals to Classes, or change build/schema to attach them directly to classes?






