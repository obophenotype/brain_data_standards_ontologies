## Customize Makefile settings for bdscratch
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

all = merged.owl

JOBS = CCN201908210

OWL_FILES = $(patsubst %, ../templates/%.owl, $(JOBS))

../templates/%_ind.tsv: ../dendrograms/%.json
    ../scripts/template_runner.py $< $@

../templates/%_class.tsv: ../dendrograms/%.json
    ../scripts/template_generation_tools.py -c $< $@

../templates/%.owl: ../robot_templates/%.tsv
	$(ROBOT) template -i ../robot_templates/support.owl --template $< -o $@;

#(SRC): $(OWL_FILES)
#	$(ROBOT) merge -i pcl-template.owl $(patsubst %, -i %, $^) --collapse-import-closure false -o $@

../templates/%_ind.owl: ../templates/%_ind.tsv
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


../templates/%_class.owl: ../templates/%_class.tsv
	$(ROBOT) template --input helper.owl --template $< \
    		--add-prefix "BDSHELP: http://www.semanticweb.org/brain_data_standards/helper.owl#" \
    		--add-prefix "AllenDend: http://www.semanticweb.org/brain_data_standards/AllenDend_" \
    		--add-prefix "skos: http://www.w3.org/2004/02/skos/core#" \
    		annotate --ontology-iri "http://www.semanticweb.org/brain_data_standards/"$@ \
    		convert --format ofn --output $@


merged.owl: $(OWL_FILES)
	$(ROBOT) merge -i pcl-template.owl $(patsubst %, -i %, $^) \
	 --collapse-import-closure false -o $@
     annotate --ontology-iri "http://www.semanticweb.org"