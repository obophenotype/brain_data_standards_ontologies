## Customize Makefile settings for bdscratch
##
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

JOBS = CCN202002013 CCN201912131 CCN201912132 CS1908210
GENE_LIST = ensmusg simple_human simple_marmoset
BDS_BASE = http://purl.obolibrary.org/obo/
ONTBASE=                    $(URIBASE)/pcl

TSV_CLASS_FILES = $(patsubst %, $(TMPDIR)/%_class.tsv, $(JOBS))
TSV_CLASS_HOMOLOGOUS_FILES = $(patsubst %, ../patterns/data/default/%_class_homologous.tsv, $(JOBS))
TSV_MARKER_SET_FILES = $(patsubst %, ../patterns/data/default/%_marker_set.tsv, $(JOBS))

OWL_FILES = $(patsubst %, components/%.owl, $(JOBS))
OWL_CLASS_FILES = $(patsubst %, components/%_class.owl, $(JOBS))
OWL_CLASS_HOMOLOGOUS_FILES = $(patsubst %, components/%_class_homologous.owl, $(JOBS))
OWL_MARKER_SET_FILES = $(patsubst %, components/%_marker_set.owl, $(JOBS))
GENE_FILES = $(patsubst %, $(MIRRORDIR)/%.owl, $(GENE_LIST))
OWL_APP_SPECIFIC_FILES = $(patsubst %, components/%_app_specific.owl, $(JOBS))
OWL_DATASET_FILES = $(patsubst %, components/%_dataset.owl, $(JOBS))
OWL_TAXONOMY_FILE = components/taxonomies.owl
OWL_PROTEIN2GENE_FILE = components/Protein2GeneExpression.owl
PCL_LEGACY_FILE = components/pcl-legacy.owl

OWL_OBSOLETE_INDVS = $(patsubst %, components/%_obsolete_indvs.owl, $(JOBS))
OWL_OBSOLETE_TAXONOMY_FILE = components/taxonomies_obsolete.owl

# overriding to add prefixes
$(PATTERNDIR)/pattern.owl: $(ALL_PATTERN_FILES)
	if [ $(PAT) = true ]; then $(DOSDPT) prototype --prefixes=template_prefixes.yaml --obo-prefixes true --template=$(PATTERNDIR)/dosdp-patterns --outfile=$@; fi

$(PATTERNDIR)/data/default/%.txt: $(PATTERNDIR)/dosdp-patterns/%.yaml $(PATTERNDIR)/data/default/%.tsv .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --prefixes=template_prefixes.yaml --infile=$(word 2, $^) --template=$< --obo-prefixes=true --outfile=$@; fi

ALL_TERMS_COMBINED = $(patsubst %, $(IMPORTDIR)/%_terms_combined.txt, $(IMPORTS))
$(IMPORTDIR)/merged_terms_combined.txt: $(ALL_TERMS_COMBINED)
	if [ $(IMP) = true ]; then cat $^ | grep -v ^# | sort | uniq >  $@; fi

ALL_MIRRORS = $(patsubst %, mirror/%.owl, $(IMPORTS))
mirror/merged.owl: $(ALL_MIRRORS)
	if [ $(IMP) = true ] && [ $(MERGE_MIRRORS) = true ]; then $(ROBOT) merge $(patsubst %, -i %, $^) -o $@; fi
.PRECIOUS: mirror/merged.owl

# DISABLE automatic pattern management. Manually managed below
$(PATTERNDIR)/definitions.owl: $(TSV_CLASS_FILES)
	if [ $(PAT) = "skip" ] && [ "${DOSDP_PATTERN_NAMES_DEFAULT}" ]   && [ $(PAT) = true ]; then $(ROBOT) merge $(addprefix -i , $^) \
		annotate --ontology-iri $(ONTBASE)/patterns/definitions.owl  --version-iri $(ONTBASE)/releases/$(TODAY)/patterns/definitions.owl \
      --annotation owl:versionInfo $(VERSION) -o definitions.ofn && mv definitions.ofn $@; fi
$(DOSDP_OWL_FILES_DEFAULT):
	if [ $(PAT) = "skip" ] && [ "${DOSDP_PATTERN_NAMES_DEFAULT}" ]; then $(DOSDPT) generate --catalog=catalog-v001.xml \
    --infile=$(PATTERNDIR)/data/default/ --template=$(PATTERNDIR)/dosdp-patterns --batch-patterns="$(DOSDP_PATTERN_NAMES_DEFAULT)" \
    --ontology=$< --obo-prefixes=true --outfile=$(PATTERNDIR)/data/default; fi
update_patterns:
	if [ $(PAT) = "skip" ]; then cp -r $(TMPDIR)/dosdp/*.yaml $(PATTERNDIR)/dosdp-patterns; fi

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
$(TMPDIR)/%_class.tsv: $(PATTERNDIR)/data/default/%_class_base.tsv $(PATTERNDIR)/data/default/%_class_curation.tsv
	python ../scripts/template_runner.py modifier --merge -i=$< -i2=$(word 2, $^) -o=$@

all_imports: $(IMPORT_FILES) imports/merged_import.owl

# hard wiring for now.  Work on patsubst later
$(MIRRORDIR)/ensmusg.owl: ../templates/ensmusg.tsv .FORCE
	if [ $(MIR) = true ]; then $(ROBOT) template --input $(SRC) --template $< \
      --add-prefixes template_prefixes.json \
      annotate --ontology-iri ${BDS_BASE}$@ \
      convert --format ofn --output $@; fi
$(MIRRORDIR)/simple_human.owl: ../templates/simple_human.tsv .FORCE
	if [ $(MIR) = true ]; then $(ROBOT) template --input $(SRC) --template ../templates/simple_human.tsv \
      --add-prefixes template_prefixes.json \
      annotate --ontology-iri ${BDS_BASE}mirror/simple_human.owl \
      convert --format ofn --output $(MIRRORDIR)/simple_human.owl; fi
$(MIRRORDIR)/simple_marmoset.owl: ../templates/simple_marmoset.tsv .FORCE
	if [ $(MIR) = true ]; then $(ROBOT) template --input $(SRC) --template ../templates/simple_marmoset.tsv \
      --add-prefixes template_prefixes.json \
      annotate --ontology-iri ${BDS_BASE}mirror/simple_marmoset.owl \
      convert --format ofn --output $(MIRRORDIR)/simple_marmoset.owl; fi

.PRECIOUS: $(MIRRORDIR)/simple_human.owl
.PRECIOUS: $(MIRRORDIR)/simple_marmoset.owl

# merge all templates except application specific ones
components/all_templates.owl: $(OWL_FILES) $(OWL_CLASS_FILES) $(OWL_MIN_MARKER_FILES) $(OWL_TAXONOMY_FILE) $(OWL_PROTEIN2GENE_FILE) $(OWL_APP_SPECIFIC_FILES) $(PCL_LEGACY_FILE) $(OWL_CLASS_HOMOLOGOUS_FILES) $(OWL_DATASET_FILES) $(OWL_MARKER_SET_FILES) $(OWL_OBSOLETE_TAXONOMY_FILE) $(OWL_OBSOLETE_INDVS)
	$(ROBOT) merge $(patsubst %, -i %, $(filter-out $(OWL_APP_SPECIFIC_FILES), $^)) \
	 --collapse-import-closure false \
	 annotate --ontology-iri ${BDS_BASE}$@  \
	 convert -f ofn	 -o $@

.PRECIOUS: $(COMPONENTSDIR)/all_templates.owl

#(SRC): $(OWL_FILES)
#	$(ROBOT) merge -i pcl-template.owl $(patsubst %, -i %, $^) --collapse-import-closure false -o $@

components/%.owl: ../templates/%.tsv $(SRC)
	$(ROBOT) template --input $(SRC) --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@ \

components/%_class.owl: $(TMPDIR)/%_class.tsv $(SRC) $(PATTERNDIR)/dosdp-patterns/taxonomy_class.yaml $(SRC) all_imports .FORCE
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=$(PATTERNDIR)/dosdp-patterns/taxonomy_class.yaml \
        --ontology=$(SRC) --obo-prefixes=true --outfile=$@   &&\
    $(ROBOT) query --input $@ --update ../sparql/fix-classifications.ru --output $@

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

components/taxonomies_obsolete.owl: ../templates/Taxonomies_obsolete.tsv $(SRC)
	$(ROBOT) template --input $(SRC) --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@

components/%_obsolete_indvs.owl: ../templates/%_obsolete_indvs.tsv $(SRC)
	$(ROBOT) template --input $(SRC) --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@ \

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

