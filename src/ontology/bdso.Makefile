## Customize Makefile settings for bdscratch
##
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

IMPORTS += simple_human simple_marmoset

JOBS = CCN202002013 CCN201912131 CCN201912132 CS1908210 #CCN202002270 CCN202002013 CCN201810310 CCN201908211 CCN201908210
GENE_LIST = ensmusg simple_human simple_marmoset
BDS_BASE = http://purl.obolibrary.org/obo/
ONTBASE=                    $(URIBASE)/pcl

TSV_CLASS_FILES = $(patsubst %, ../patterns/data/default/%_class.tsv, $(JOBS))
TSV_CLASS_HOMOLOGOUS_FILES = $(patsubst %, ../patterns/data/default/%_class_homologous.tsv, $(JOBS))
TSV_MARKER_SET_FILES = $(patsubst %, ../patterns/data/default/%_marker_set.tsv, $(JOBS))

OWL_FILES = $(patsubst %, components/%.owl, $(JOBS))
OWL_CLASS_FILES = $(patsubst %, components/%_class.owl, $(JOBS))
OWL_CLASS_HOMOLOGOUS_FILES = $(patsubst %, components/%_class_homologous.owl, $(JOBS))
OWL_MARKER_SET_FILES = $(patsubst %, components/%_marker_set.owl, $(JOBS))
GENE_FILES = $(patsubst %, mirror/%.owl, $(GENE_LIST))
OWL_APP_SPECIFIC_FILES = $(patsubst %, components/%_app_specific.owl, $(JOBS))
OWL_DATASET_FILES = $(patsubst %, components/%_dataset.owl, $(JOBS))
OWL_TAXONOMY_FILE = components/taxonomies.owl
OWL_PROTEIN2GENE_FILE = components/Protein2GeneExpression.owl
PCL_LEGACY_FILE = components/pcl-legacy.owl

#DEND_FILES = $(patsubst %, ../dendrograms/%.json, $(JOBS))
#TEMPLATE_FILES = $(patsubst %, ../templates/%.tsv, $(JOBS))
#TEMPLATE_CLASS_FILES = $(patsubst %, ../templates/_%class.tsv, $(JOBS))

# overriding to add prefixes
$(PATTERNDIR)/pattern.owl: update_patterns
	if [ $(PAT) = true ]; then $(DOSDPT) prototype --prefixes=template_prefixes.yaml --obo-prefixes true --template=$(PATTERNDIR)/dosdp-patterns --outfile=$@; fi

individual_patterns_names_default := $(strip $(patsubst %.tsv,%, $(notdir $(wildcard $(PATTERNDIR)/data/default/*.tsv))))
dosdp_patterns_default: $(SRC) all_imports .FORCE
	if [ $(PAT) = true ] && [ "${individual_patterns_names_default}" ]; then $(DOSDPT) generate --prefixes=template_prefixes.yaml --catalog=catalog-v001.xml --infile=$(PATTERNDIR)/data/default/ --template=$(PATTERNDIR)/dosdp-patterns --batch-patterns="$(individual_patterns_names_default)" --ontology=$< --obo-prefixes=true --outfile=$(PATTERNDIR)/data/default; fi

$(PATTERNDIR)/data/default/%.txt: $(PATTERNDIR)/dosdp-patterns/%.yaml $(PATTERNDIR)/data/default/%.tsv .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --prefixes=template_prefixes.yaml --infile=$(word 2, $^) --template=$< --obo-prefixes=true --outfile=$@; fi

# adding more imports (simple_human simple_marmoset) to process
#IMPORT_ROOTS = $(patsubst %, imports/%_import, $(IMPORTS))
#IMPORT_OWL_FILES = $(foreach n,$(IMPORT_ROOTS), $(n).owl)
#IMPORT_FILES = $(IMPORT_OWL_FILES)

#ALL_TERMS_COMBINED = $(patsubst %, imports/%_terms_combined.txt, $(IMPORTS))
#imports/merged_terms_combined.txt: $(ALL_TERMS_COMBINED)
#	if [ $(IMP) = true ]; then cat $^ | grep -v ^# | sort | uniq >  $@; fi

ALL_MIRRORS = $(patsubst %, mirror/%.owl, $(IMPORTS))
mirror/merged.owl: $(ALL_MIRRORS)
	if [ $(IMP) = true ] && [ $(MERGE_MIRRORS) = true ]; then $(ROBOT) merge $(patsubst %, -i %, $^) -o $@; fi
.PRECIOUS: mirror/merged.owl


# adding an extra query step to inject version info to imported entities and remove exclude_iri_patterns
imports/%_import.owl: mirror/merged.owl imports/%_terms_combined.txt
	if [ $(IMP) = true ]; then $(ROBOT) query  -i $< --update ../sparql/inject-version-info.ru --update ../sparql/preprocess-module.ru \
		extract -T imports/$*_terms_combined.txt --force true --copy-ontology-annotations true --individuals exclude --method BOT \
		remove  --select "<http://www.informatics.jax.org/marker/MGI:*>" remove  --select "<http://purl.obolibrary.org/obo/OBA_*>" remove  --select "<http://purl.obolibrary.org/obo/ENVO_*>" remove  --select "<http://purl.obolibrary.org/obo/OBI_*>" remove  --select "<http://purl.obolibrary.org/obo/GOCHE_*>" remove  --select "<http://purl.obolibrary.org/obo/CARO_*>" remove  --select "<http://purl.obolibrary.org/obo/NCBITaxon_Union_*>" remove  --select "<http://www.genenames.org/cgi-bin/gene_symbol_report*>"  \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/postprocess-module.ru \
		annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) --output $@.tmp.owl && mv $@.tmp.owl $@; fi

.PRECIOUS: imports/%_import.owl

# remove exclude_iri_patterns
imports/pr_import.owl: mirror/merged.owl imports/pr_terms_combined.txt
	if [ $(IMP) = true ] && [ $(IMP_LARGE) = true ]; then $(ROBOT) extract -i $< -T imports/pr_terms_combined.txt --force true --individuals exclude --method BOT \
		remove  --select "<http://www.informatics.jax.org/marker/MGI:*>" remove  --select "<http://purl.obolibrary.org/obo/OBA_*>" remove  --select "<http://purl.obolibrary.org/obo/ENVO_*>" remove  --select "<http://purl.obolibrary.org/obo/OBI_*>" remove  --select "<http://purl.obolibrary.org/obo/GOCHE_*>" remove  --select "<http://purl.obolibrary.org/obo/CARO_*>" remove  --select "<http://purl.obolibrary.org/obo/NCBITaxon_Union_*>" remove  --select "<http://www.genenames.org/cgi-bin/gene_symbol_report*>"  \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/postprocess-module.ru \
		annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) --output $@.tmp.owl && mv $@.tmp.owl $@; fi

.PRECIOUS: imports/pr_import.owl

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

$(PATTERNDIR)/data/default/%_class_homologous.txt: $(PATTERNDIR)/data/default/%_class_homologous.tsv $(TSV_CLASS_FILES) .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class_homologous.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi

$(PATTERNDIR)/data/default/%_marker_set.txt: $(PATTERNDIR)/data/default/%_marker_set.tsv $(TSV_MARKER_SET_FILES) .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi

$(PATTERNDIR)/data/default/Protein2GeneExpression.txt: $(PATTERNDIR)/data/default/Protein2GeneExpression.tsv .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/Protein2GeneExpression.yaml --obo-prefixes=true --prefixes=template_prefixes.yaml --outfile=$@; fi


# merge class template data
$(PATTERNDIR)/data/default/%_class.tsv: $(PATTERNDIR)/data/default/%_class_base.tsv $(PATTERNDIR)/data/default/%_class_curation.tsv
	python ../scripts/template_runner.py modifier --merge -i=$< -i2=$(word 2, $^) -o=$@

all_imports: $(IMPORT_FILES) imports/merged_import.owl

# hard wiring for now.  Work on patsubst later
mirror/ensmusg.owl: ../templates/ensmusg.tsv .FORCE
	if [ $(MIR) = true ]; then $(ROBOT) template --input $(SRC) --template $< \
      --add-prefixes template_prefixes.json \
      annotate --ontology-iri ${BDS_BASE}$@ \
      convert --format ofn --output $@; fi
	if [ $(MIR) = true ]; then $(ROBOT) template --input $(SRC) --template ../templates/simple_human.tsv \
      --add-prefixes template_prefixes.json \
      annotate --ontology-iri ${BDS_BASE}mirror/simple_human.owl \
      convert --format ofn --output mirror/simple_human.owl; fi
	if [ $(MIR) = true ]; then $(ROBOT) template --input $(SRC) --template ../templates/simple_marmoset.tsv \
      --add-prefixes template_prefixes.json \
      annotate --ontology-iri ${BDS_BASE}mirror/simple_marmoset.owl \
      convert --format ofn --output mirror/simple_marmoset.owl; fi

.PRECIOUS: mirror/simple_human.owl
.PRECIOUS: imports/simple_human_import.owl
.PRECIOUS: mirror/simple_marmoset.owl
.PRECIOUS: imports/simple_marmoset_import.owl

# merge all templates except application specific ones
components/all_templates.owl: $(OWL_FILES) $(OWL_CLASS_FILES) $(OWL_MIN_MARKER_FILES) $(OWL_TAXONOMY_FILE) $(OWL_PROTEIN2GENE_FILE) $(OWL_APP_SPECIFIC_FILES) $(PCL_LEGACY_FILE) $(OWL_CLASS_HOMOLOGOUS_FILES) $(OWL_DATASET_FILES) $(OWL_MARKER_SET_FILES)
	$(ROBOT) merge $(patsubst %, -i %, $(filter-out $(OWL_APP_SPECIFIC_FILES), $^)) \
	 --collapse-import-closure false \
	 annotate --ontology-iri ${BDS_BASE}$@  \
	 convert -f ofn	 -o $@

#(SRC): $(OWL_FILES)
#	$(ROBOT) merge -i pcl-template.owl $(patsubst %, -i %, $^) --collapse-import-closure false -o $@

components/%.owl: ../templates/%.tsv $(SRC)
	$(ROBOT) template --input $(SRC) --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@ \

components/%_class.owl: $(PATTERNDIR)/data/default/%_class.tsv $(SRC) $(PATTERNDIR)/dosdp-patterns/taxonomy_class.yaml $(SRC) all_imports .FORCE
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

components/%_class_homologous.owl: $(PATTERNDIR)/data/default/%_class_homologous.tsv $(SRC) $(PATTERNDIR)/dosdp-patterns/taxonomy_class_homologous.yaml $(SRC) all_imports .FORCE
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class_homologous.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

components/%_marker_set.owl: $(PATTERNDIR)/data/default/%_marker_set.tsv $(SRC) $(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml $(SRC) all_imports .FORCE
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_marker_set.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

components/taxonomies.owl: ../templates/Taxonomies.tsv $(SRC)
	$(ROBOT) template --input $(SRC) --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@

components/Protein2GeneExpression.owl: $(PATTERNDIR)/data/default/Protein2GeneExpression.tsv $(PATTERNDIR)/dosdp-patterns/Protein2GeneExpression.yaml $(SRC) all_imports .FORCE
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/Protein2GeneExpression.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@

# release a legacy ontology to support older versions of the PCL
components/pcl-legacy.owl: ../resources/pCL_4.1.0.owl components/pCL_mapping.owl
	$(ROBOT) query --input ../resources/pCL_4.1.0.owl --update ../sparql/delete-legacy-properties.ru \
			query --update ../sparql/delete-non-pcl-terms.ru \
			query --update ../sparql/postprocess-module.ru \
			remove --select ontology \
			merge --input components/pCL_mapping.owl \
			annotate --ontology-iri $(ONTBASE)/pcl.owl  \
			--link-annotation dc:license http://creativecommons.org/licenses/by/4.0/ \
			--annotation owl:versionInfo $(VERSION) \
			--annotation dc:title "Provisional Cell Ontology" \
			--output $@

components/pCL_mapping.owl: ../templates/pCL_mapping.tsv ../resources/pCL_4.1.0.owl
	$(ROBOT) template --input ../resources/pCL_4.1.0.owl --template $< \
    		--add-prefixes template_prefixes.json \
    		convert --format ofn --output $@

components/%_app_specific.owl: ../templates/%_app_specific.tsv allen_helper.owl
	$(ROBOT) template --input allen_helper.owl --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@ \

components/%_dataset.owl: ../templates/%_dataset.tsv $(SRC)
	$(ROBOT) template --input $(SRC) --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@ \


# Release additional artifacts
$(ONT).owl: $(ONT)-full.owl $(ONT)-allen.owl $(ONT)-pcl-comp.owl $(ONT)-pcl-comp.obo $(ONT)-pcl-comp.json
	$(ROBOT) annotate --input $< --ontology-iri $(URIBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		convert -o $@.tmp.owl && mv $@.tmp.owl $@

# Allen app specific ontology (with color information etc.) (Used for Solr dump)
$(ONT)-allen.owl: $(ONT)-full.owl allen_helper.owl
	$(ROBOT) merge -i $< -i allen_helper.owl $(patsubst %, -i %, $(OWL_APP_SPECIFIC_FILES)) \
			 annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		 	 --output $(RELEASEDIR)/$@

# Artifact that extends base with gene ontologies (used by PCL)
$(ONT)-pcl-comp.owl:  $(ONT)-base.owl $(GENE_FILES)
	$(ROBOT) merge -i $< $(patsubst %, -i %, $(GENE_FILES)) \
	query --update ../sparql/remove_preflabels.ru \
			 annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		 	 --output $(RELEASEDIR)/$@ 
$(ONT)-pcl-comp.obo: $(RELEASEDIR)/$(ONT)-pcl-comp.owl
	$(ROBOT) convert --input $< --check false -f obo $(OBO_FORMAT_OPTIONS) -o $@.tmp.obo && grep -v ^owl-axioms $@.tmp.obo > $(RELEASEDIR)/$@ && rm $@.tmp.obo
$(ONT)-pcl-comp.json: $(RELEASEDIR)/$(ONT)-pcl-comp.owl
	$(ROBOT) annotate --input $< --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		convert --check false -f json -o $@.tmp.json &&\
	jq -S 'walk(if type == "array" then sort else . end)' $@.tmp.json > $(RELEASEDIR)/$@ && rm $@.tmp.json

# New ODK should remove the need for this 
## skip schema checks for now, because odk using the wrong validator
##.PHONY: pattern_schema_checks
##pattern_schema_checks: update_patterns
##	if [ $(PAT) = "skip" ]; then $(PATTERN_TESTER) $(PATTERNDIR)/dosdp-patterns/  ; fi

#tmp fix
.PHONY: update_patterns
update_patterns: download_patterns
	cp -f -r $(TMPDIR)/dosdp/*.yaml $(PATTERNDIR)/dosdp-patterns