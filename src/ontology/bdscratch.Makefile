## Customize Makefile settings for bdscratch
##
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile


JOBS = CCN201908210 CCN202002013

OWL_FILES = $(patsubst %, %.owl, $(JOBS))
OWL_CLASS_FILES = $(patsubst %, %_class.owl, $(JOBS))

#DEND_FILES = $(patsubst %, ../dendrograms/%.json, $(JOBS))
#TEMPLATE_FILES = $(patsubst %, ../templates/%.tsv, $(JOBS))
#TEMPLATE_CLASS_FILES = $(patsubst %, ../templates/_%class.tsv, $(JOBS))

components/all_templates.owl: $(OWL_FILES) $(OWL_CLASS_FILES) helper.owl
	$(ROBOT) merge $(patsubst %, -i %, $^) \
	 --collapse-import-closure false \
	 annotate --ontology-iri "http://www.semanticweb.org/brain_data_standards/"$@  \
	 convert -f ofn	 -o $@

../templates/%.tsv: ../dendrograms/%.json
	python ../scripts/template_runner.py $< $@

../templates/%_class.tsv: ../dendrograms/%.json
	python ../scripts/template_runner.py -c $< $@

#(SRC): $(OWL_FILES)
#	$(ROBOT) merge -i pcl-template.owl $(patsubst %, -i %, $^) --collapse-import-closure false -o $@

%.owl: ../templates/%.tsv
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


%_class.owl: ../templates/%_class.tsv
	$(ROBOT) template --input helper.owl --template $< \
    		--add-prefix "BDSHELP: http://www.semanticweb.org/brain_data_standards/helper.owl#" \
    		--add-prefix "AllenDend: http://www.semanticweb.org/brain_data_standards/AllenDend_" \
    		--add-prefix "skos: http://www.w3.org/2004/02/skos/core#" \
    		annotate --ontology-iri "http://www.semanticweb.org/brain_data_standards/"$@ \
    		convert --format ofn --output $@



