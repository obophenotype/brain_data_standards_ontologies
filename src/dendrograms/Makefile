JOBS = CCN202002013 CCN201912131 CCN201912132 CS1908210 # CCN202002270 CCN201908210 CCN201810310 CCN201908211

# GIT related configurations
GIT_REPO=					https://github.com/AllenInstitute/MOp_taxonomies_ontology.git
REPO_NAME=					MOp_taxonomies_ontology
CENTRALIZED_DIR=			centralized_data

TEMPLATE_FILES = $(patsubst %, ../templates/%.tsv, $(JOBS))
MARKER_DENORMALIZED_FILES = $(patsubst %, ../markers/%_markers_denormalized.tsv, $(JOBS))
TEMPLATE_CLASS_BASE_FILES = $(patsubst %, ../patterns/data/default/%_class_base.tsv, $(JOBS))
TEMPLATE_CLASS_CURATION_FILES = $(patsubst %, ../patterns/data/default/%_class_curation.tsv, $(JOBS))
TEMPLATE_CLASS_HOMOLOGOUS_FILES = $(patsubst %, ../patterns/data/default/%_class_homologous.tsv, $(JOBS))
APP_SPECIFIC_TEMPLATE_FILES = $(patsubst %, ../templates/%_app_specific.tsv, $(JOBS))
DATASET_TEMPLATE_FILES = $(patsubst %, ../templates/%_dataset.tsv, $(JOBS))
MARKER_SET_TEMPLATE_FILES = $(patsubst %, ../patterns/data/default/%_marker_set.tsv, $(JOBS))
TAXONOMY_TEMPLATE_FILE = ../templates/Taxonomies.tsv
OBSOLETE_INDV_TEMPLATE_FILES = $(patsubst %, ../templates/%_obsolete_indvs.tsv, $(JOBS))
OBSOLETE_TAXONOMY_TEMPLATE_FILE = ../templates/Taxonomies_obsolete.tsv

all: update_centralized_repo $(TEMPLATE_FILES) $(TEMPLATE_CLASS_BASE_FILES) $(TEMPLATE_CLASS_CURATION_FILES) $(MARKER_DENORMALIZED_FILES) $(TAXONOMY_TEMPLATE_FILE) $(APP_SPECIFIC_TEMPLATE_FILES) $(TEMPLATE_CLASS_HOMOLOGOUS_FILES) $(DATASET_TEMPLATE_FILES) $(MARKER_SET_TEMPLATE_FILES) $(OBSOLETE_INDV_TEMPLATE_FILES) $(OBSOLETE_TAXONOMY_TEMPLATE_FILE)

../templates/%.tsv: %.json nomenclature_table_%.csv
	if [ $< = CS1908210.json ]; then python ../scripts/template_runner.py generator -i $< -i2 $(CENTRALIZED_DIR)/$(REPO_NAME) -o $@ ;\
	else python ../scripts/template_runner.py generator -i $(word 2, $^) -i2 $(CENTRALIZED_DIR)/$(REPO_NAME) -o $@ ; fi

../markers/%_markers_denormalized.tsv: %.json nomenclature_table_%.csv
	if [ $< = CS1908210.json ]; then python ../scripts/template_runner.py generator -md -i $< -o $@ ;\
	else python ../scripts/template_runner.py generator -md -i $(word 2, $^) -o $@ ; fi

../patterns/data/default/%_class_base.tsv: %.json nomenclature_table_%.csv
	if [ $< = CS1908210.json ]; then python ../scripts/template_runner.py generator -cb -i $< -o $@ ;\
	else python ../scripts/template_runner.py generator -cb -i $(word 2, $^) -o $@ ; fi

../patterns/data/default/%_class_curation.tsv: %.json nomenclature_table_%.csv
	if [ $< = CS1908210.json ]; then python ../scripts/template_runner.py generator -cc -i $< -o $@ ;\
	else python ../scripts/template_runner.py generator -cc -i $(word 2, $^) -o $@ ; fi

../patterns/data/default/%_class_homologous.tsv: %.json nomenclature_table_%.csv $(TEMPLATE_CLASS_BASE_FILES)
	if [ $< = CS1908210.json ]; then python ../scripts/template_runner.py generator -ch -i $< -b "$(TEMPLATE_CLASS_BASE_FILES)" -o $@ ;\
	else python ../scripts/template_runner.py generator -ch -i $(word 2, $^) -b "$(TEMPLATE_CLASS_BASE_FILES)" -o $@ ; fi

../templates/%_app_specific.tsv: %.json nomenclature_table_%.csv
	if [ $< = CS1908210.json ]; then python ../scripts/template_runner.py generator -a -i $< -o $@ ;\
	else python ../scripts/template_runner.py generator -a -i $(word 2, $^) -o $@ ; fi

../patterns/data/default/%_marker_set.tsv: %.json nomenclature_table_%.csv
	if [ $< = CS1908210.json ]; then python ../scripts/template_runner.py generator -ms -i $< -i2 $(CENTRALIZED_DIR)/$(REPO_NAME) -o $@ ;\
	else python ../scripts/template_runner.py generator -ms -i $(word 2, $^) -i2 $(CENTRALIZED_DIR)/$(REPO_NAME) -o $@ ; fi

../templates/%_dataset.tsv: $(CENTRALIZED_DIR)/$(REPO_NAME)
	python ../scripts/template_runner.py generator -ds -i $< -o $@

../templates/Taxonomies.tsv: $(CENTRALIZED_DIR)/$(REPO_NAME)
	python ../scripts/template_runner.py generator -tx -i $< -o $@

../templates/%_obsolete_indvs.tsv: %.json nomenclature_table_%.csv
	if [ $< = CS1908210.json ]; then python ../scripts/template_runner.py generator -oi -i $< -i2 $(CENTRALIZED_DIR)/$(REPO_NAME) -o $@ ;\
	else python ../scripts/template_runner.py generator -oi -i $(word 2, $^) -i2 $(CENTRALIZED_DIR)/$(REPO_NAME) -o $@ ; fi

../templates/Taxonomies_obsolete.tsv: $(CENTRALIZED_DIR)/$(REPO_NAME)
	python ../scripts/template_runner.py generator -ot -i $< -o $@

update_centralized_repo: clean_centralized_data_folder
	cd $(CENTRALIZED_DIR) && git clone --quiet ${GIT_REPO} && rm -rf $(REPO_NAME)/.git  && \
	cd .. && \
	rm nomenclature_table_CCN201912131.csv && cp $(CENTRALIZED_DIR)/$(REPO_NAME)/humanM1_CCN201912131/nomenclature_table_CCN201912131.csv ./  && \
	rm nomenclature_table_CCN202002013.csv && cp $(CENTRALIZED_DIR)/$(REPO_NAME)/mouseMOp_CCN202002013/nomenclature_table_CCN202002013.csv ./  && \
	rm nomenclature_table_CCN201912132.csv && cp $(CENTRALIZED_DIR)/$(REPO_NAME)/marmosetM1_CCN201912132/nomenclature_table_CCN201912132.csv ./

clean_centralized_data_folder:
	rm -rf $(CENTRALIZED_DIR)/$(REPO_NAME)


