## Customize Makefile settings for bdscratch
##
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

IMPORTS += simple_human simple_marmoset

JOBS = CCN202002013 CCN201912131 CCN201912132 #CCN202002270 CCN202002013 CCN201810310 CCN201908211 CCN201908210
GENE_LIST = ensmusg simple_human simple_marmoset
BDS_BASE = http://www.semanticweb.org/brain_data_standards/

TSV_CLASS_FILES = $(patsubst %, ../patterns/data/default/%_class.tsv, $(JOBS))

OWL_FILES = $(patsubst %, components/%.owl, $(JOBS))
OWL_CLASS_FILES = $(patsubst %, components/%_class.owl, $(JOBS))
GENE_FILES = $(patsubst %, mirror/%.owl, $(GENE_LIST))
OWL_NOMENCLATURE_FILES = $(patsubst %, components/%_non_taxonomy_classification.owl, $(JOBS))
OWL_CROSS_SPECIES_FILES = $(patsubst %, components/%_cross_species.owl, $(JOBS))
OWL_APP_SPECIFIC_FILES = $(patsubst %, components/%_app_specific.owl, $(JOBS))
OWL_TAXONOMY_FILE = components/taxonomies.owl
OWL_PROTEIN2GENE_FILE = components/Protein2GeneExpression.owl

#DEND_FILES = $(patsubst %, ../dendrograms/%.json, $(JOBS))
#TEMPLATE_FILES = $(patsubst %, ../templates/%.tsv, $(JOBS))
#TEMPLATE_CLASS_FILES = $(patsubst %, ../templates/_%class.tsv, $(JOBS))


$(PATTERNDIR)/pattern.owl: pattern_schema_checks update_patterns
	if [ $(PAT) = true ]; then $(DOSDPT) prototype --prefixes=template_prefixes.yaml --obo-prefixes true --template=$(PATTERNDIR)/dosdp-patterns --outfile=$@; fi

individual_patterns_names_default := $(strip $(patsubst %.tsv,%, $(notdir $(wildcard $(PATTERNDIR)/data/default/*.tsv))))
dosdp_patterns_default: $(SRC) all_imports .FORCE
	if [ $(PAT) = true ] && [ "${individual_patterns_names_default}" ]; then $(DOSDPT) generate --prefixes=template_prefixes.yaml --catalog=catalog-v001.xml --infile=$(PATTERNDIR)/data/default/ --template=$(PATTERNDIR)/dosdp-patterns --batch-patterns="$(individual_patterns_names_default)" --ontology=$< --obo-prefixes=true --outfile=$(PATTERNDIR)/data/default; fi

$(PATTERNDIR)/data/default/%.txt: $(PATTERNDIR)/dosdp-patterns/%.yaml $(PATTERNDIR)/data/default/%.tsv .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --prefixes=template_prefixes.yaml --infile=$(word 2, $^) --template=$< --obo-prefixes=true --outfile=$@; fi

# adding an extra query step to inject version info to imported entities
imports/%_import.owl: mirror/%.owl imports/%_terms_combined.txt
	if [ $(IMP) = true ]; then $(ROBOT) query  -i $< --update ../sparql/inject-version-info.ru --update ../sparql/preprocess-module.ru \
		extract -T imports/$*_terms_combined.txt --force true --copy-ontology-annotations true --individuals exclude --method BOT \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/postprocess-module.ru \
		annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) --output $@.tmp.owl && mv $@.tmp.owl $@; fi

# disable automatic pattern management. Manually managed below
dosdp_patterns_default: $(SRC) all_imports .FORCE
	if [ $(PAT) = "skip" ] && [ "${individual_patterns_names_default}" ]; then $(DOSDPT) generate --catalog=catalog-v001.xml --infile=$(PATTERNDIR)/data/default/ --template=$(PATTERNDIR)/dosdp-patterns --batch-patterns="$(individual_patterns_names_default)" --ontology=$< --obo-prefixes=true --outfile=$(PATTERNDIR)/data/default; fi

# disable automatic term management and manually manage below
$(PATTERNDIR)/data/default/%.txt: $(PATTERNDIR)/dosdp-patterns/%.yaml $(PATTERNDIR)/data/default/%.tsv .FORCE
	if [ $(PAT) = 'skip' ]; then $(DOSDPT) terms --infile=$(word 2, $^) --template=$< --obo-prefixes=true --outfile=$@; fi

$(PATTERNDIR)/data/default/%_class_base.txt: $(PATTERNDIR)/data/default/%_class_base.tsv $(TSV_CLASS_FILES) .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi

$(PATTERNDIR)/data/default/%_class_curation.txt: $(PATTERNDIR)/data/default/%_class_curation.tsv $(TSV_CLASS_FILES) .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi

$(PATTERNDIR)/data/default/%_non_taxonomy_classification.txt: $(PATTERNDIR)/data/default/%_non_taxonomy_classification.tsv .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_non_taxonomy_classification.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi

$(PATTERNDIR)/data/default/%_cross_species.txt: $(PATTERNDIR)/data/default/%_cross_species.tsv .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_cross_species.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi

$(PATTERNDIR)/data/default/Protein2GeneExpression.txt: $(PATTERNDIR)/data/default/Protein2GeneExpression.tsv .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/Protein2GeneExpression.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi


# merge class template data
$(PATTERNDIR)/data/default/%_class.tsv: $(PATTERNDIR)/data/default/%_class_base.tsv $(PATTERNDIR)/data/default/%_class_curation.tsv
	python ../scripts/template_runner.py modifier --merge -i=$< -i2=$(word 2, $^) -o=$@

all_imports: $(IMPORT_FILES)

# hard wiring for now.  Work on patsubst later
mirror/ensmusg.owl: ../templates/ensmusg.tsv .FORCE
	if [ $(MIR) = true ] && [ $(IMP) = true ]; then $(ROBOT) template --input bdscratch-edit.owl --template $< \
      --add-prefixes template_prefixes.json \
      annotate --ontology-iri ${BDS_BASE}$@ \
      convert --format ofn --output $@; fi
	if [ $(MIR) = true ] && [ $(IMP) = true ]; then $(ROBOT) template --input bdscratch-edit.owl --template ../templates/simple_human.tsv \
      --add-prefixes template_prefixes.json \
      annotate --ontology-iri ${BDS_BASE}mirror/simple_human.owl \
      convert --format ofn --output mirror/simple_human.owl; fi
	if [ $(MIR) = true ] && [ $(IMP) = true ]; then $(ROBOT) template --input bdscratch-edit.owl --template ../templates/simple_marmoset.tsv \
      --add-prefixes template_prefixes.json \
      annotate --ontology-iri ${BDS_BASE}mirror/simple_marmoset.owl \
      convert --format ofn --output mirror/simple_marmoset.owl; fi

.PRECIOUS: mirror/simple_human.owl
.PRECIOUS: imports/simple_human_import.owl
.PRECIOUS: mirror/simple_marmoset.owl
.PRECIOUS: imports/simple_marmoset_import.owl

# merge all templates except application specific ones
components/all_templates.owl: $(OWL_FILES) $(OWL_CLASS_FILES) $(OWL_MIN_MARKER_FILES) $(OWL_NOMENCLATURE_FILES) $(OWL_CROSS_SPECIES_FILES) $(OWL_TAXONOMY_FILE) $(OWL_PROTEIN2GENE_FILE) $(OWL_APP_SPECIFIC_FILES)
	$(ROBOT) merge $(patsubst %, -i %, $(filter-out $(OWL_APP_SPECIFIC_FILES), $^)) \
	 --collapse-import-closure false \
	 annotate --ontology-iri ${BDS_BASE}$@  \
	 convert -f ofn	 -o $@

#(SRC): $(OWL_FILES)
#	$(ROBOT) merge -i pcl-template.owl $(patsubst %, -i %, $^) --collapse-import-closure false -o $@

components/%.owl: ../templates/%.tsv bdscratch-edit.owl
	$(ROBOT) template --input bdscratch-edit.owl --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@ \

components/%_class.owl: $(PATTERNDIR)/data/default/%_class.tsv bdscratch-edit.owl $(PATTERNDIR)/dosdp-patterns/taxonomy_class.yaml $(SRC) all_imports .FORCE
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

components/%_non_taxonomy_classification.owl: $(PATTERNDIR)/data/default/%_non_taxonomy_classification.tsv $(PATTERNDIR)/dosdp-patterns/taxonomy_non_taxonomy_classification.yaml $(SRC) all_imports .FORCE
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_non_taxonomy_classification.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

components/%_cross_species.owl: $(PATTERNDIR)/data/default/%_cross_species.tsv $(PATTERNDIR)/dosdp-patterns/taxonomy_cross_species.yaml $(SRC) all_imports .FORCE
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_cross_species.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

components/taxonomies.owl: ../templates/Taxonomies.tsv bdscratch-edit.owl
	$(ROBOT) template --input bdscratch-edit.owl --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@

components/Protein2GeneExpression.owl: $(PATTERNDIR)/data/default/Protein2GeneExpression.tsv $(PATTERNDIR)/dosdp-patterns/Protein2GeneExpression.yaml $(SRC) all_imports .FORCE
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/Protein2GeneExpression.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

components/%_app_specific.owl: ../templates/%_app_specific.tsv allen_helper.owl
	$(ROBOT) template --input allen_helper.owl --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@ \


# Also release Allen application specific ontology
$(ONT).owl: $(ONT)-full.owl $(ONT)-allen.owl
	$(ROBOT) annotate --input $< --ontology-iri $(URIBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		convert -o $@.tmp.owl && mv $@.tmp.owl $@

$(ONT)-allen.owl: $(ONT)-full.owl allen_helper.owl
	$(ROBOT) merge -i $< -i allen_helper.owl $(patsubst %, -i %, $(OWL_APP_SPECIFIC_FILES)) \
			 annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		 	 --output $(RELEASEDIR)/$@