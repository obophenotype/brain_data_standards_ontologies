## Store R dendrograms and generate robot template TSVs

### File Naming

Store dendrogram JSON files as {accession}.json and associated tsvs as {accession}.tsv, where {accession} = standard
Allen dendrogram accession e.g. CCN202002013

### (re)Generating robot template TSVs

WARNING: Be careful about overwriting TSVs containing curation!

To (re)generate all templates:

    `./run.sh make all`
    
To extend the set of recognised accessions for build, edit the list of JOBS in the makefile
    
To (re)generate templates for a single dendrogram:

   `./run.sh JOBS={accession}` (note no spaces)
   
 To (re)generate a single template
 
   `./run.sh make {template relative path)` e.g. `run.sh make ../CCN201908210_class.tsv`
 

