ROBOT= /Users/davidos/bin/robot -vvv

all: MTG.owl

# Currently relying on Jupyter notebook to generate input TSVs, but this could be folded into the makefile.
# Longer term aim - turn this into a pipeline in which any dendrogram json can be placed and registered =>
# OWL individual file following some standard naming convention
# Hand curated TSVs will add additional properties
# Automated import managements (could just switch this whole thing to ODK)
# Minimal output OWL files that are directly useful to users

MTG_ind.owl: CCN201908210.tsv
	$(ROBOT) template --input helper.owl --template $< \
    		--add-prefix "BDSHELP: http://www.semanticweb.org/brain_data_standards/helper.owl#" \
    		--add-prefix "AllenDend: http://www.semanticweb.org/brain_data_standards/AllenDend_" \
    		--add-prefix "skos: http://www.w3.org/2004/02/skos/core#" \
    		annotate --ontology-iri "http://www.semanticweb.org/brain_data_standards/"$@ \
    		convert --format ofn --output $@

#MTG_ec.owl: CCN201908210_EC.tsv MTG_ind.owl
#	$(ROBOT) template --input helper.owl --template $< \
#    		--add-prefix "BDSHELP: http://www.semanticweb.org/brain_data_standards/helper.owl#" \
#    		--add-prefix "AllenDend: http://www.semanticweb.org/brain_data_standards/AllenDend_" \
#    		--add-prefix "skos: http://www.w3.org/2004/02/skos/core#" \
#    		annotate --ontology-iri "http://www.semanticweb.org/brain_data_standards/"$@ \
#    		convert --format ofn --output $@


MTG_class.owl: CCN201908210_class_curated.tsv
	$(ROBOT) template --input helper.owl --template $< \
    		--add-prefix "BDSHELP: http://www.semanticweb.org/brain_data_standards/helper.owl#" \
    		--add-prefix "AllenDend: http://www.semanticweb.org/brain_data_standards/AllenDend_" \
    		--add-prefix "skos: http://www.w3.org/2004/02/skos/core#" \
    		annotate --ontology-iri "http://www.semanticweb.org/brain_data_standards/"$@ \
    		convert --format ofn --output $@


MTG.owl: helper.owl MTG_ind.owl MTG_class.owl
	$(ROBOT) merge --input helper.owl --input MTG_class.owl --input MTG_ind.owl \
  		    annotate --ontology-iri "http://www.semanticweb.org/brain_data_standards/"$@ \
    		convert --format ofn --output $@




