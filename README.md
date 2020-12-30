# Brain Data Standards Ontologies [![Build Status](https://travis-ci.org/obophenotype/brain_data_standards_ontologies.svg?branch=master)](https://travis-ci.org/obophenotype/brain_data_standards_ontologies)
A repository for co-ordinating work on ontologies for the Brain Data Standards Project

### Overview:

![image](https://user-images.githubusercontent.com/112839/103354330-2ffa7580-4aa3-11eb-8444-81b73e09adf4.png)


The Build system is built on top of the [Ontology Development Kit]().  You will need docker unstalled.  Running a build will pull the required containers.


To build 

```sh
cd src/ontology
sh ./run.sh make prepare_release
```

This dynamically updates imports as well as building reasoned release files.

To extend the ontologies imported from.  Edit [bdscratch-odk.yaml](https://github.com/obophenotype/brain_data_standards_ontologies/blob/master/src/ontology/bdscratch-odk.yaml) to add the required ontology to import_group.products, then run:

```
sh ./run.sh make update_repo
```

The update the import statements in src/ontology/bdscratch-edit.owl.

### Extensions to the standard ODK MakeFile build

Extensions to the build are specified (as per ODK standard) in [bdscratch.Makefile](https://github.com/obophenotype/brain_data_standards_ontologies/blob/master/src/ontology/bdscratch.Makefile). 


#### Building robot templates from Dendrograms

Dendrograms live in [/src/dendrograms/](https://github.com/obophenotype/brain_data_standards_ontologies/blob/master/src/dendrograms/).  They are named according to their Allen Dendrogram ID, e.g. CCN201908210.json

We expect dendrograms to remain stable for relatively long periods of time and at least some generated Robot templates are intended to be manually edited to map to CL classes / property driven classification.  For these reasons, we store generated templates on the repo and build them as needed using a separate MakeFile - [src/dendrograms/Makefile](https://github.com/obophenotype/brain_data_standards_ontologies/blob/master/src/dendrograms/Makefile).  

To build (be careful you don't wipe out curation!): 

```sh
cd src/dendrograms
# Build all
sh ./run.sh make
# Build specific template
sh ./run.sh make <template_filename>
# Build a specific set of tempaltes
sh ./run.sh make JOBS=<dendrogram_id>
```

tempaltes are build from dendrograms using python scripts in [src/scripts](https://github.com/obophenotype/brain_data_standards_ontologies/tree/master/src/scripts)

Extended information about groupings of taxonomy nodes that are candidates for curation are stored in additional tsv files (accession.tsv)
Support for incorporating this informtion into templates is TBA.


### Robot templates

Robot templates live in  [/src/tempaltes/](https://github.com/obophenotype/brain_data_standards_ontologies/blob/master/src/templates/). 


filename | e.g. | Description
-- | -- | --
{accession}.tsv | CCN201810310.tsv | Template for generating taxonomy as OWL individuals
{accession}\_class.tsv | CCN201810310_class.tsv | Templates for generating classes corresponding to OWL individuals in taxonomy. Includes slots for curating cell type & properties
{accession}\_markers.tsv | CCN201810310_markers.tsv | Templates for adding markers.  Referenced markers must be present in gene reference files.
ensmusg.tsv | {ensembl_gene_file}.tsv | Robot template listing all genes (all possible markers) for analysis/dendrogams of some specific species.

ensembl_gene_file name follows standard ensembl ID prefixes but in lowercase e.g. ensmusg.tsv (ensembl mouse gene) has genes with IDs of the form: ENSMUSG{numeric_accession}

#### Markers

Markers are referenced by enembl ID using an [identifiers.org URL scheme](https://registry.identifiers.org/registry/ensembl)

ensembl gene file templates are used to generate mirror files, which act as source files for import generation, so that only referenced markers end up in the release files.








