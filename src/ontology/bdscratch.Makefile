## Customize Makefile settings for bdscratch
##
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile


JOBS = CCN202002013 # CCN201810310 CCN201908211 CCN201908210
GENE_FILES = ensmusg
BDS_BASE = http://www.semanticweb.org/brain_data_standards/

# Equivalent class pattern approach: reification or denormalised_markers
EC_PATTERN = reification # denormalised_markers

OWL_FILES = $(patsubst %, components/%.owl, $(JOBS))
OWL_CLASS_FILES = $(patsubst %, components/%_class.owl, $(JOBS))
OWL_EQUIVALENT_CLASS_FILES = $(patsubst %, components/%_equivalent_class.owl, $(JOBS))
GENE_FILES = $(patsubst %, mirror/%.owl, $(JOBS))
OWL_MIN_MARKER_FILES = $(patsubst %, components/%_minimal_markers.owl, $(JOBS))

DEND_FILES = $(patsubst %, ../dendrograms/%.json, $(JOBS))
#TEMPLATE_FILES = $(patsubst %, ../templates/%.tsv, $(JOBS))
#TEMPLATE_CLASS_FILES = $(patsubst %, ../templates/_%class.tsv, $(JOBS))

.PHONY: generate_pattern_tsvs
generate_pattern_tsvs: $(DEND_FILES)
	if [ $(EC_PATTERN) = reification ]; then python ../scripts/dosdp_pattern_generation.py -re $< ; fi
	if [ $(EC_PATTERN) = denormalised_markers ]; then python ../scripts/dosdp_pattern_generation.py -dm $< ; fi

.PHONY: update_pattern_vars
update_pattern_vars:
	$(eval pattern_tables := $(notdir $(shell find $(PATTERNDIR)/data/default/ -name '*.tsv'))  )
	$(eval individual_patterns_default := $(patsubst %.tsv, $(PATTERNDIR)/data/default/%.ofn, $(pattern_tables)) )
	$(eval pattern_term_lists_default := $(patsubst %.tsv, $(PATTERNDIR)/data/default/%.txt, $(pattern_tables)) )
	$(eval individual_patterns_names_default := $(strip $(strip $(patsubst %.tsv,%, $(pattern_tables))) ))

.PHONY: prepare_patterns
prepare_patterns: generate_pattern_tsvs update_pattern_vars
	if [ $(PAT) = true ]; then touch $(PATTERNDIR)/data $(pattern_term_lists_default)  ; fi
	if [ $(PAT) = true ]; then touch $(PATTERNDIR)/data $(individual_patterns_default)  ; fi
	@for f in $(individual_patterns_names_default); do \
	    if [ $(PAT) = true ]; then $(DOSDPT) terms --prefixes=template_prefixes.yaml --infile=$(PATTERNDIR)/data/default/$${f}.tsv --template=$(PATTERNDIR)/dosdp-patterns/$${f}.yaml --obo-prefixes=true --outfile=$(PATTERNDIR)/data/default/$${f}.txt; fi \
	done

$(PATTERNDIR)/pattern.owl: pattern_schema_checks update_patterns
	if [ $(PAT) = true ]; then $(DOSDPT) prototype --prefixes=template_prefixes.yaml --obo-prefixes true --template=$(PATTERNDIR)/dosdp-patterns --outfile=$@; fi

individual_patterns_names_default := $(strip $(patsubst %.tsv,%, $(notdir $(wildcard $(PATTERNDIR)/data/default/*.tsv))))
dosdp_patterns_default: $(SRC) all_imports .FORCE
	if [ $(PAT) = true ] && [ "${individual_patterns_names_default}" ]; then $(DOSDPT) generate --prefixes=template_prefixes.yaml --catalog=catalog-v001.xml --infile=$(PATTERNDIR)/data/default/ --template=$(PATTERNDIR)/dosdp-patterns --batch-patterns="$(individual_patterns_names_default)" --ontology=$< --obo-prefixes=true --outfile=$(PATTERNDIR)/data/default; fi

$(PATTERNDIR)/data/default/%.txt: $(PATTERNDIR)/dosdp-patterns/%.yaml $(PATTERNDIR)/data/default/%.tsv .FORCE
    # deprecated, please see prepare_patterns
	if [ $(PAT) = true ]; then $(DOSDPT) terms --prefixes=template_prefixes.yaml --infile=$(word 2, $^) --template=$< --obo-prefixes=true --outfile=$@; fi

# Generating the seed file from all the TSVs. If Pattern generation is deactivated, we still extract a seed from definitions.owl
$(PATTERNDIR)/all_pattern_terms.txt: $(pattern_term_lists_default)   $(PATTERNDIR)/pattern_owl_seed.txt
	if [ $(PAT) = true ]; then cat $(pattern_term_lists_default) $^ | sort | uniq > $@; else $(ROBOT) query --use-graphs true -f csv -i ../patterns/definitions.owl --query ../sparql/terms.sparql $@; fi

# hard wiring for now.  Work on patsubst later
mirror/ensmusg.owl: ../templates/ensmusg.tsv
	if [ $(MIR) = true ] && [ $(IMP) = true ]; then $(ROBOT) template --input bdscratch-edit.owl --template $< \
      --add-prefixes template_prefixes.json \
      annotate --ontology-iri ${BDS_BASE}$@ \
      convert --format ofn --output $@; fi

components/all_templates.owl: $(OWL_FILES) $(OWL_CLASS_FILES) $(OWL_EQUIVALENT_CLASS_FILES) $(OWL_MIN_MARKER_FILES)
	$(ROBOT) merge $(patsubst %, -i %, $^) \
	 --collapse-import-closure false \
	 annotate --ontology-iri ${BDS_BASE}$@  \
	 convert -f ofn	 -o $@

#(SRC): $(OWL_FILES)
#	$(ROBOT) merge -i pcl-template.owl $(patsubst %, -i %, $^) --collapse-import-closure false -o $@

components/%.owl: ../templates/%.tsv bdscratch-edit.owl
	$(ROBOT) template --input bdscratch-edit.owl --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@

components/%_class.owl: ../templates/%_class.tsv bdscratch-edit.owl
	$(ROBOT) template --input bdscratch-edit.owl --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@

components/%_equivalent_class.owl: ../templates/%_equivalent_reification.tsv bdscratch-edit.owl
	$(ROBOT) template --input bdscratch-edit.owl --template $< \
	        --add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@

components/%_minimal_markers.owl: ../templates/%_minimal_markers.tsv bdscratch-edit.owl
	$(ROBOT) template --input bdscratch-edit.owl --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@

