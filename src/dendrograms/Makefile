JOBS = CCN201912131 CCN201912132 #CCN202002013  CCN201908210 CCN201810310 CCN201908211

TEMPLATE_FILES = $(patsubst %, ../templates/%.tsv, $(JOBS))
MARKER_DENORMALIZED_FILES = $(patsubst %, ../markers/%_markers_denormalized.tsv, $(JOBS))
TEMPLATE_CLASS_BASE_FILES = $(patsubst %, ../patterns/data/default/%_class_base.tsv, $(JOBS))
TEMPLATE_CLASS_CURATION_FILES = $(patsubst %, ../patterns/data/default/%_class_curation.tsv, $(JOBS))
NOMENCLATURE_TEMPLATE_FILES = $(patsubst %, ../patterns/data/default/%_non_taxonomy_classification.tsv, $(JOBS))


all: $(TEMPLATE_FILES) $(TEMPLATE_CLASS_BASE_FILES) $(TEMPLATE_CLASS_CURATION_FILES) $(MARKER_DENORMALIZED_FILES) $(NOMENCLATURE_TEMPLATE_FILES)

../templates/%.tsv: %.json nomenclature_table_%.csv
	if [ $< = CCN201912131.json ]; then python ../scripts/template_runner.py generator -i $(word 2, $^) -o $@ ;\
	elif [ $< = CCN201912132.json ]; then python ../scripts/template_runner.py generator -i $(word 2, $^) -o $@ ;\
	else python ../scripts/template_runner.py generator -i $< -o $@; fi

../markers/%_markers_denormalized.tsv: %.json
	python ../scripts/template_runner.py generator -md -i $< -o $@

../patterns/data/default/%_class_base.tsv: %.json nomenclature_table_%.csv
	if [ $< = CCN201912131.json ]; then python ../scripts/template_runner.py generator -cb -i $(word 2, $^) -o $@ ;\
	elif [ $< = CCN201912132.json ]; then python ../scripts/template_runner.py generator -cb -i $(word 2, $^) -o $@ ;\
	else python ../scripts/template_runner.py generator -cb -i $< -o $@; fi

../patterns/data/default/%_class_curation.tsv: %.json nomenclature_table_%.csv
	if [ $< = CCN201912131.json ]; then python ../scripts/template_runner.py generator -cc -i $(word 2, $^) -o $@ ;\
	elif [ $< = CCN201912132.json ]; then python ../scripts/template_runner.py generator -cc -i $(word 2, $^) -o $@ ;\
	else python ../scripts/template_runner.py generator -cc -i $< -o $@; fi

../patterns/data/default/%_non_taxonomy_classification.tsv: %.json nomenclature_table_%.csv
	if [ $< = CCN201912131.json ]; then python ../scripts/template_runner.py generator -n -i $(word 2, $^) -o $@ ;\
	elif [ $< = CCN201912132.json ]; then python ../scripts/template_runner.py generator -n -i $(word 2, $^) -o $@ ;\
	else python ../scripts/template_runner.py generator -n -i $< -o $@; fi

