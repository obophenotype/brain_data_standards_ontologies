JOBS = CCN202002013 #CCN201912131 CCN201912132 CCN201908210 CCN201810310 CCN201908211

TEMPLATE_FILES = $(patsubst %, ../templates/%.tsv, $(JOBS))
TEMPLATE_CLASS_FILES = $(patsubst %, ../patterns/data/bds/%_class.tsv, $(JOBS))
MARKER_DENORMALIZED_FILES = $(patsubst %, ../markers/%_markers_denormalized.tsv, $(JOBS))
EQUIVALENT_CLASS_MARKER_FILES = $(patsubst %, ../templates/%_equivalent_markers.tsv, $(JOBS))
EQUIVALENT_CLASS_REIFICATION_FILES = $(patsubst %, ../patterns/data/bds/%_equivalent_reification.tsv, $(JOBS))
TEMPLATE_MINIMAL_MARKER_FILES = $(patsubst %, ../patterns/data/bds/%_minimal_markers.tsv, $(JOBS))
NOMENCLATURE_TEMPLATE_FILES = $(patsubst %, ../patterns/data/bds/%_non_taxonomy_classification.tsv, $(JOBS))


all: $(TEMPLATE_FILES) $(TEMPLATE_CLASS_FILES) $(MARKER_DENORMALIZED_FILES) $(EQUIVALENT_CLASS_MARKER_FILES) $(EQUIVALENT_CLASS_REIFICATION_FILES) $(TEMPLATE_MINIMAL_MARKER_FILES) $(NOMENCLATURE_TEMPLATE_FILES)

../templates/%.tsv: %.json
	python ../scripts/template_runner.py $< $@

../patterns/data/bds/%_class.tsv: %.json
	python ../scripts/template_runner.py -c $< $@

../markers/%_markers_denormalized.tsv: %.json
	python ../scripts/template_runner.py -md $< $@

../templates/%_equivalent_markers.tsv: %.json
	python ../scripts/template_runner.py -em $< $@

../patterns/data/bds/%_equivalent_reification.tsv: %.json
	python ../scripts/template_runner.py -er $< $@

../patterns/data/bds/%_minimal_markers.tsv: %.json
	python ../scripts/template_runner.py -mm $< $@

../patterns/data/bds/%_non_taxonomy_classification.tsv: %.json
	python ../scripts/template_runner.py -n $< $@

