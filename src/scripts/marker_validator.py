import os
import re
import logging
import argparse

from dendrogram_tools import dend_json_2_nodes_n_edges
from template_generation_utils import read_tsv
from abc import ABC, abstractmethod
from os.path import isfile, join, abspath

log = logging.getLogger(__name__)

MARKERS_FOLDER = join(os.path.dirname(os.path.realpath(__file__)), "../markers")
DENDROGRAMS_FOLDER = join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms")

PATH_REPORT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../target/report.txt")


def is_denormalized_file(file_name):
    return file_name.endswith("_markers_denormalized.tsv")


def get_taxonomy_files():
    return [f for f in os.listdir(DENDROGRAMS_FOLDER) if re.search("^CCN\\d+\\.json$", f)]


def get_taxonomy_file_name(marker_file_name):
    return marker_file_name.replace("_markers.tsv", ".json") .replace("CS", "CCN")


def get_marker_file_name(taxonomy_file_name):
    return taxonomy_file_name.replace(".json", "_markers.tsv") .replace("CCN", "CS")


def index_dendrogram(dend):
    dend_dict = dict()
    for o in dend['nodes']:
        dend_dict[o['cell_set_accession']] = o
    return dend_dict


def save_report(report):
    f = open(PATH_REPORT, "w")
    for rep in report:
        f.write(rep+"\n")
    f.close()


class BaseChecker(ABC):

    reports = []

    @abstractmethod
    def check(self):
        pass

    @abstractmethod
    def get_header(self):
        return "=== Default Checker :"


class FileNameChecker(BaseChecker):
    """
    - Marker files are submitted under src/markers/.
    - Files must be named CS{taxonomy_id}_markers.tsv.
    - Marker files must have a corresponding dendrogram (CCN{taxonomy_id}.json) under src/dendrograms.
    """

    def check(self):
        expected_names = [get_marker_file_name(f) for f in get_taxonomy_files()]
        files = [f for f in os.listdir(MARKERS_FOLDER) if isfile(join(MARKERS_FOLDER, f))]
        for file in files:
            if not is_denormalized_file(file) and file not in expected_names:
                message = "Invalid marker file name: {}. Name should be one of {}"\
                    .format(file, expected_names)
                self.reports.append(message)
                # log.error(message)
            elif file in expected_names:
                expected_names.remove(file)

    def get_header(self):
        return "=== File Name Checks :"


class TableStructureChecker(BaseChecker):
    """
    - Marker files must have 3 columns.
    - Expected headers are in order : 'Taxonomy_node_ID', 'clusterName', 'Markers'.
    """

    expected_headers = ['Taxonomy_node_ID', 'clusterName', 'Markers']

    def check(self):
        files = [f for f in os.listdir(MARKERS_FOLDER) if isfile(join(MARKERS_FOLDER, f))]
        for file in files:
            if not is_denormalized_file(file):
                records = read_tsv(join(MARKERS_FOLDER, file))
                header_row = records[next(iter(records))]
                if header_row != self.expected_headers:
                    message = "Invalid column names: {} in file {}. Expected columns are: {}" \
                        .format(header_row, file, self.expected_headers)
                    self.reports.append(message)
                    # log.error(message)

    def get_header(self):
        return "=== Table Structure Checks :"


class MarkerContentChecker(BaseChecker):
    """
    - All dendrogram nodes must be present.
    - Taxonomy_node_ID must be valid (exists in the dendrogram).
    - clusterName must(?) match clusterName in dendrogram
    - Markers must match regex ^\\\w+:\\\w+$ with multiple entries delimited by |
    """

    def check(self):
        files = [f for f in os.listdir(MARKERS_FOLDER) if isfile(join(MARKERS_FOLDER, f))]
        for marker_file in files:
            if not is_denormalized_file(marker_file):
                dendrogram_path = join(DENDROGRAMS_FOLDER, get_taxonomy_file_name(marker_file))
                if os.path.exists(dendrogram_path):
                    marker_records = read_tsv(join(MARKERS_FOLDER, marker_file))
                    dend = dend_json_2_nodes_n_edges(join(DENDROGRAMS_FOLDER, dendrogram_path))
                    dend_dict = index_dendrogram(dend)
                    self.check_all_nodes_exist(dend, marker_records, marker_file)
                    self.check_all_node_ids_valid(dend_dict, marker_records, marker_file)
                    self.check_cluster_name(dend_dict, marker_records, marker_file)
                    self.check_marker_names(marker_records, marker_file)

    def check_all_nodes_exist(self, dend, marker_records, marker_file):
        missing_nodes = []
        for o in dend['nodes']:
            if o['cell_set_accession'] not in marker_records:
                missing_nodes.append(o['cell_set_accession'])
                if len(missing_nodes) > 4:
                    break
        if missing_nodes:
            message = "All dendrogram nodes must be present in the marker file {}. Top 5 missing nodes: {}" \
                .format(marker_file, missing_nodes)
            self.reports.append(message)
            # log.error(message)

    def check_all_node_ids_valid(self, dend_dict, marker_records, marker_file):
        marker_ids = list(marker_records.keys())
        marker_ids.pop(0)  # pop header row
        for _id in marker_ids:
            if _id not in dend_dict:
                message = "Invalid Taxonomy_node_ID '{}' in the marker file {}. Id not exist in the dendrogram." \
                    .format(_id, marker_file)
                self.reports.append(message)
                # log.error(message)

    def check_cluster_name(self, dend_dict, marker_records, marker_file):
        marker_ids = list(marker_records.keys())
        marker_ids.pop(0)  # pop header row
        for _id in marker_ids:
            if _id in dend_dict:
                if marker_records[_id][1] != dend_dict[_id]["label"]:
                    message = "clusterName '{}' of {} in {} does not match label ({}) in the dendrogram." \
                        .format(marker_records[_id][1], _id, marker_file, dend_dict[_id]["label"])
                    self.reports.append(message)
                    # log.error(message)

    def check_marker_names(self, marker_records, marker_file):
        marker_ids = list(marker_records.keys())
        marker_ids.pop(0)  # pop header row
        for _id in marker_ids:
            markers = marker_records[_id][2]
            for marker in markers.split("|"):
                if not re.search("^\\w+:\\w+$", marker):
                    message = "Invalid marker '{}' in file '{}' with key '{}'." \
                        .format(marker, marker_file, _id)
                    self.reports.append(message)
                    # log.error(message)

    def get_header(self):
        return "=== Marker Content Checks :"


class MarkerValidator(object):

    rules = [FileNameChecker(), TableStructureChecker(), MarkerContentChecker()]
    reports = []

    def validate(self):
        for checker in self.rules:
            checker.check()
            if checker.reports:
                self.reports.append(checker.get_header())
                self.reports.extend(checker.reports)


class ValidationError(Exception):

    def __init__(self, message, report):
        Exception.__init__(self)
        self.message = message
        self.report = report


def main(silent):
    log.info("Marker validation started.")
    validator = MarkerValidator()
    validator.validate()
    if not validator.reports:
        log.info("Marker validation successful.")
    else:
        for rep in validator.reports:
            print(rep)
        # save_report()
        log.error("Marker validation completed with errors.")
        if not silent:
            raise ValidationError("Marker validation completed with errors.", validator.reports)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--silent', action='store_true')
    args = parser.parse_args()
    main(args.silent)
