JOBS = CCN201908210 CCN202002013 CCN201810310 CCN201908211

TEMPLATE_FILES = $(patsubst %, ../templates/%.tsv, $(JOBS))
TEMPLATE_CLASS_FILES = $(patsubst %, ../templates/%_class.tsv, $(JOBS))
MARKER_FILES = $(patsubst %, ../templates/%_markers.tsv, $(JOBS))
EQUIVALENT_CLASS_REIFICATION_FILES = $(patsubst %, ../templates/%_equivalent_reification.tsv, $(JOBS))


all: $(TEMPLATE_FILES) $(TEMPLATE_CLASS_FILES) $(MARKER_FILES) $(EQUIVALENT_CLASS_REIFICATION_FILES)

../templates/%.tsv: %.json
	python ../scripts/template_runner.py $< $@

../templates/%_class.tsv: %.json
	python ../scripts/template_runner.py -c $< $@

../templates/%_markers.tsv: %.json
	python ../scripts/template_runner.py -m $< $@

../templates/%_equivalent_reification.tsv: %.json
	python ../scripts/template_runner.py -er $< $@