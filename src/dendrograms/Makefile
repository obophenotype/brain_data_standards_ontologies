JOBS = CCN202002013 CCN201912131 CCN201912132 # CCN202002270 CCN201908210 CCN201810310 CCN201908211

TEMPLATE_FILES = $(patsubst %, ../templates/%.tsv, $(JOBS))
MARKER_DENORMALIZED_FILES = $(patsubst %, ../markers/%_markers_denormalized.tsv, $(JOBS))
TEMPLATE_CLASS_BASE_FILES = $(patsubst %, ../patterns/data/default/%_class_base.tsv, $(JOBS))
TEMPLATE_CLASS_CURATION_FILES = $(patsubst %, ../patterns/data/default/%_class_curation.tsv, $(JOBS))
NOMENCLATURE_TEMPLATE_FILES = $(patsubst %, ../patterns/data/default/%_non_taxonomy_classification.tsv, $(JOBS))
CROSS_SPECIES_TEMPLATE_FILES = $(patsubst %, ../patterns/data/default/%_cross_species.tsv, $(JOBS))
APP_SPECIFIC_TEMPLATE_FILES = $(patsubst %, ../templates/%_app_specific.tsv, $(JOBS))
TAXONOMY_TEMPLATE_FILE = ../templates/Taxonomies.tsv


all: $(TEMPLATE_FILES) $(TEMPLATE_CLASS_BASE_FILES) $(TEMPLATE_CLASS_CURATION_FILES) $(MARKER_DENORMALIZED_FILES) $(NOMENCLATURE_TEMPLATE_FILES) $(TAXONOMY_TEMPLATE_FILE) $(APP_SPECIFIC_TEMPLATE_FILES)

../templates/%.tsv: nomenclature_table_%.csv
	python ../scripts/template_runner.py generator -i $< -o $@

../markers/%_markers_denormalized.tsv: nomenclature_table_%.csv
	python ../scripts/template_runner.py generator -md -i $< -o $@

../patterns/data/default/%_class_base.tsv: nomenclature_table_%.csv
	python ../scripts/template_runner.py generator -cb -i $< -j "$(JOBS)" -o $@

../patterns/data/default/%_class_curation.tsv: nomenclature_table_%.csv
	python ../scripts/template_runner.py generator -cc -i $< -o $@

../patterns/data/default/%_non_taxonomy_classification.tsv: nomenclature_table_%.csv
	python ../scripts/template_runner.py generator -n -i $< -o $@

../templates/%_app_specific.tsv: nomenclature_table_%.csv
	python ../scripts/template_runner.py generator -a -i $< -o $@

../templates/Taxonomies.tsv: Taxonomy_Info_Panel.csv
	python ../scripts/template_runner.py generator -tx -i $< -o $@

#../patterns/data/default/%_cross_species.tsv: nomenclature_table_%.csv
#	python ../scripts/template_runner.py generator -cs -i $< -o $@
