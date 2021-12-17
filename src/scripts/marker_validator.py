import os
import re
import logging
import argparse
import csv

from dendrogram_tools import dend_json_2_nodes_n_edges
from template_generation_utils import read_tsv, index_dendrogram, read_csv_to_dict
from nomenclature_tools import nomenclature_2_nodes_n_edges
from abc import ABC, abstractmethod, ABCMeta
from os.path import isfile, join

log = logging.getLogger(__name__)

MARKERS_FOLDER = join(os.path.dirname(os.path.realpath(__file__)), "../markers")
DENDROGRAMS_FOLDER = join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms")

PATH_REPORT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../target/report.txt")

TAXONOMY_MAPPING = {"CCN202002013": "nomenclature_table_CCN202002013.csv",
                    "CCN201912131": "nomenclature_table_CCN201912131.csv",
                    "CCN201912132": "nomenclature_table_CCN201912132.csv",
                    "CS1908210": "CS1908210.json"}


def is_whitelist_file(file_name):
    """White list documents that are exempt from validation."""
    return file_name.endswith("_markers_denormalized.tsv") or file_name.endswith("_Allen_markers.tsv")


def get_taxonomy_files():
    return [f for f in os.listdir(DENDROGRAMS_FOLDER) if re.search("^CCN\\d+\\.json$", f)]


def get_taxonomy_file_name(marker_file_name):
    path_parts = marker_file_name.split(os.path.sep)
    taxon = path_parts[len(path_parts) - 1].split(".")[0].replace("_markers", "") .replace("CS", "CCN")

    if taxon in TAXONOMY_MAPPING:
        return TAXONOMY_MAPPING[taxon]
    else:
        return "nomenclature_table_" + taxon + ".csv"


def get_marker_file_name(taxonomy_file_name):
    return taxonomy_file_name.replace(".json", "_markers.tsv") .replace("CCN", "CS")


def save_report(report):
    f = open(PATH_REPORT, "w")
    for rep in report:
        f.write(rep+"\n")
    f.close()


class BaseChecker(ABC):

    @abstractmethod
    def check(self):
        pass

    @abstractmethod
    def get_header(self):
        return "=== Default Checker :"


class StrictChecker(BaseChecker, metaclass=ABCMeta):
    """Failures of strict checks cause exceptions."""
    pass


class SoftChecker(BaseChecker, metaclass=ABCMeta):
    """Failures of soft checks cause warnings."""
    pass


class FileNameChecker(StrictChecker):
    """
    - Marker files are submitted under src/markers/.
    - Files must be named CS{taxonomy_id}_markers.tsv.
    - Marker files must have a corresponding dendrogram (CCN{taxonomy_id}.json) under src/dendrograms.
    """

    def __init__(self):
        self.reports = []

    def check(self):
        expected_names = [get_marker_file_name(f) for f in get_taxonomy_files()]
        files = [f for f in os.listdir(MARKERS_FOLDER) if isfile(join(MARKERS_FOLDER, f))]
        for file in files:
            if not is_whitelist_file(file) and file not in expected_names:
                message = "Invalid marker file name: {}. Name should be one of {}"\
                    .format(file, expected_names)
                self.reports.append(message)
                # log.error(message)
            elif file in expected_names:
                expected_names.remove(file)

    def get_header(self):
        return "=== File Name Checks :"


class TableStructureChecker(StrictChecker):
    """
    - Marker files must have 3 columns.
    - Expected headers are in order : 'Taxonomy_node_ID', 'clusterName', 'Markers'.
    """

    def __init__(self):
        self.reports = []
        self.expected_headers = ['Taxonomy_node_ID', 'clusterName', 'Markers']

    def check(self):
        files = [f for f in os.listdir(MARKERS_FOLDER) if isfile(join(MARKERS_FOLDER, f))]
        for file in files:
            if not is_whitelist_file(file):
                header_row, records = read_csv_to_dict(join(MARKERS_FOLDER, file), delimiter="\t")
                if header_row != self.expected_headers:
                    message = "Invalid column names: {} in file {}. Expected columns are: {}" \
                        .format(header_row, file, self.expected_headers)
                    self.reports.append(message)
                    # log.error(message)

    def get_header(self):
        return "=== Table Structure Checks :"


class DendrogramCrossChecker(SoftChecker):
    """
    - All dendrogram nodes must be present in the marker file.
    """

    def __init__(self):
        self.reports = []

    def check(self):
        files = [f for f in os.listdir(MARKERS_FOLDER) if isfile(join(MARKERS_FOLDER, f))]
        for marker_file in files:
            if not is_whitelist_file(marker_file):
                dendrogram_path = join(DENDROGRAMS_FOLDER, get_taxonomy_file_name(marker_file))
                if os.path.exists(dendrogram_path):
                    marker_records = read_tsv(join(MARKERS_FOLDER, marker_file))
                    if str(dendrogram_path).endswith(".json"):
                        dend = dend_json_2_nodes_n_edges(dendrogram_path)
                    else:
                        dend = nomenclature_2_nodes_n_edges(dendrogram_path)
                    self.check_all_nodes_exist(dend, marker_records, marker_file)

    def check_all_nodes_exist(self, dend, marker_records, marker_file):
        missing_nodes = []
        for o in dend['nodes']:
            if o['cell_set_accession'] not in marker_records:
                missing_nodes.append(o['cell_set_accession'])
        if missing_nodes:
            message = "All dendrogram nodes must be present in the marker file {}. Total {} missing nodes. " \
                      "\nTop 5 missing nodes are: {}" \
                .format(marker_file, len(missing_nodes), missing_nodes[0:5])
            self.reports.append(message)

    def get_header(self):
        return "=== Dendrogram Node Checks :"


class TaxonomyNodeIdChecker(StrictChecker):
    """
    - Taxonomy_node_ID must be valid (exists in the dendrogram).
    - Taxonomy_node_ID's must be unique
    """

    def __init__(self):
        self.reports = []

    def check(self):
        files = [f for f in os.listdir(MARKERS_FOLDER) if isfile(join(MARKERS_FOLDER, f))]
        for marker_file in files:
            if not is_whitelist_file(marker_file):
                dendrogram_path = join(DENDROGRAMS_FOLDER, get_taxonomy_file_name(marker_file))
                if os.path.exists(dendrogram_path):
                    headers, marker_records = read_csv_to_dict(join(MARKERS_FOLDER, marker_file), delimiter="\t")
                    if str(dendrogram_path).endswith(".json"):
                        dend = dend_json_2_nodes_n_edges(dendrogram_path)
                    else:
                        dend = nomenclature_2_nodes_n_edges(dendrogram_path)
                    dend_dict = index_dendrogram(dend)
                    self.check_all_node_ids_valid(dend_dict, marker_records, marker_file)
                    self.check_all_node_ids_unique(marker_file)

    def check_all_node_ids_valid(self, dend_dict, marker_records, marker_file):
        marker_ids = list(marker_records.keys())
        for _id in marker_ids:
            if _id not in dend_dict:
                message = "Invalid Taxonomy_node_ID '{}' in the marker file ({}). Id not exist in the dendrogram." \
                    .format(_id, marker_file)
                self.reports.append(message)
                # log.error(message)

    def check_all_node_ids_unique(self, marker_file):
        taxonomy_node_ids = list()
        with open(join(MARKERS_FOLDER, marker_file)) as fd:
            rd = csv.reader(fd, delimiter="\t", quotechar='"')
            for row in rd:
                _id = row[0]
                if _id in taxonomy_node_ids:
                    self.reports.append("Redundant Taxonomy_node_ID '{}' in the marker file ({})."
                                        .format(_id, marker_file))
                else:
                    taxonomy_node_ids.append(_id)

    def get_header(self):
        return "=== Marker Nodes' Dendrogram Existence Checks :"


class ClusterNameChecker(SoftChecker):
    """
    - clusterName must(?) match clusterName in dendrogram
    """

    def __init__(self):
        self.reports = []

    def check(self):
        files = [f for f in os.listdir(MARKERS_FOLDER) if isfile(join(MARKERS_FOLDER, f))]
        for marker_file in files:
            if not is_whitelist_file(marker_file):
                dendrogram_path = join(DENDROGRAMS_FOLDER, get_taxonomy_file_name(marker_file))
                print("DEND:" + dendrogram_path)
                if os.path.exists(dendrogram_path):
                    headers, marker_records = read_csv_to_dict(join(MARKERS_FOLDER, marker_file), delimiter="\t")
                    if str(dendrogram_path).endswith(".json"):
                        dend = dend_json_2_nodes_n_edges(dendrogram_path)
                    else:
                        dend = nomenclature_2_nodes_n_edges(dendrogram_path)
                    dend_dict = index_dendrogram(dend)
                    self.check_cluster_name(dend_dict, marker_records, marker_file)
                else:
                    message = "Could not find taxonomy file '{}' for marker '{}'." \
                        .format(dendrogram_path, marker_file)
                    self.reports.append(message)

    def check_cluster_name(self, dend_dict, marker_records, marker_file):
        marker_ids = list(marker_records.keys())
        for _id in marker_ids:
            if _id in dend_dict:
                if "original_label" in dend_dict[_id]:
                    dend_label = dend_dict[_id]["original_label"]
                else:
                    dend_label = dend_dict[_id]["label"]
                if marker_records[_id]["clusterName"] != dend_label and \
                        marker_records[_id]["clusterName"] != dend_label.replace("/", "-"):
                    message = "clusterName '{}' of {} in {} does not match label '{}' in the dendrogram." \
                        .format(marker_records[_id]["clusterName"], _id, marker_file, dend_label)
                    self.reports.append(message)

    def get_header(self):
        return "=== Cluster Name Checks :"


class MarkerNameChecker(StrictChecker):
    """
    - Markers must match regex ^\\\w+:\\\w+$ with multiple entries delimited by |
    """

    def __init__(self):
        self.reports = []

    def check(self):
        files = [f for f in os.listdir(MARKERS_FOLDER) if isfile(join(MARKERS_FOLDER, f))]
        for marker_file in files:
            if not is_whitelist_file(marker_file):
                dendrogram_path = join(DENDROGRAMS_FOLDER, get_taxonomy_file_name(marker_file))
                if os.path.exists(dendrogram_path):
                    headers, marker_records = read_csv_to_dict(join(MARKERS_FOLDER, marker_file), delimiter="\t")
                    self.check_marker_names(marker_records, marker_file)

    def check_marker_names(self, marker_records, marker_file):
        marker_ids = list(marker_records.keys())
        for _id in marker_ids:
            markers = marker_records[_id]["Markers"]
            for marker in markers.split("|"):
                if not re.search("^\\w+:\\w+$", marker):
                    message = "Invalid marker '{}' in file '{}' with key '{}'." \
                        .format(marker, marker_file, _id)
                    self.reports.append(message)
                    # log.error(message)

    def get_header(self):
        return "=== Marker Name Checks :"


class MarkerValidator(object):

    rules = [FileNameChecker(), TableStructureChecker(), DendrogramCrossChecker(), TaxonomyNodeIdChecker(),
             # ClusterNameChecker(),  # cluster names do not match after manual curations
             MarkerNameChecker()]
    errors = []
    warnings = []

    def validate(self):
        for checker in self.rules:
            checker.check()
            if checker.reports:
                if isinstance(checker, StrictChecker):
                    self.errors.append("\n"+checker.get_header())
                    self.errors.extend(checker.reports)
                else:
                    self.warnings.append("\n"+checker.get_header())
                    self.warnings.extend(checker.reports)


class ValidationError(Exception):

    def __init__(self, message, report):
        Exception.__init__(self)
        self.message = message
        self.report = report


def main(silent):
    log.info("Marker validation started.")
    validator = MarkerValidator()
    validator.validate()
    if not validator.errors and not validator.warnings:
        print("\nMarker validation successful.")
    elif not validator.errors:
        print("Warnings:")
        for rep in validator.warnings:
            print(rep)
        print("\nMarker validation completed with warnings.")
    else:
        print("\nErrors:")
        for rep in validator.errors:
            print(rep)
        if validator.warnings:
            print("\nWarnings:")
            for rep in validator.warnings:
                print(rep)
        print("\nMarker validation completed with errors.")
        if not silent:
            raise ValidationError("Marker validation completed with errors.", validator.errors)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--silent', action='store_true')
    args = parser.parse_args()
    main(args.silent)
