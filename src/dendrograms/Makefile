JOBS = CCN202002013

TEMPLATE_FILES = $(patsubst %, ../templates/%.tsv, $(JOBS))
TEMPLATE_CLASS_FILES = $(patsubst %, ../templates/%_class.tsv, $(JOBS))
MARKER_FILES = $(patsubst %, ../templates/%_markers.tsv, $(JOBS))
MARKER_DENORMALIZED_FILES = $(patsubst %, ../templates/%_markers_denormalized.tsv, $(JOBS))
EQUIVALENT_CLASS_MARKER_FILES = $(patsubst %, ../templates/%_equivalent_markers.tsv, $(JOBS))


all: $(TEMPLATE_FILES) $(TEMPLATE_CLASS_FILES) $(MARKER_FILES) $(EQUIVALENT_CLASS_MARKER_FILES)

../templates/%.tsv: %.json
	python ../scripts/template_runner.py $< $@

../templates/%_class.tsv: %.json
	python ../scripts/template_runner.py -c $< $@

../templates/%_markers.tsv: %.json
	python ../scripts/template_runner.py -m $< $@

../templates/%_markers_denormalized.tsv: %.json
	python ../scripts/template_runner.py -md $< $@

../templates/%_equivalent_markers.tsv: %.json
	python ../scripts/template_runner.py -em $< $@
