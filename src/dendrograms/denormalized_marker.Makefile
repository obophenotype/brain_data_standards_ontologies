JOBS = 202002013

MARKER_FILES = $(patsubst %, ../templates/CCN%_markers.tsv, $(JOBS))
MARKER_DENORMALIZED_FILES = $(patsubst %, ../templates/CS%_markers_denormalized.tsv, $(JOBS))

all: $(MARKER_DENORMALIZED_FILES)

../templates/CS%_markers_denormalized.tsv: CCN%.json ../markers/CS%_markers.tsv taxonomy_details.yaml
	python ../scripts/marker_template_runner.py $^ $@