import unittest
import os
import csv

from dosdp_pattern_generation import generate_pattern_table_denormalised_markers

PATH_DENDROGRAM_JSON = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/CCN202002013.json")
PATH_OUTPUT_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/dosdp_output.tsv")

ALLEN_CLASS = "AllenDendClass:"


def delete_file(path_to_file):
    if os.path.exists(path_to_file):
        os.remove(path_to_file)


class DosdpPatternGenerationTest(unittest.TestCase):

    def setUp(self):
        delete_file(PATH_OUTPUT_TSV)

    def tearDown(self):
        delete_file(PATH_OUTPUT_TSV)

    def test_curated_class_template_generation(self):
        generate_pattern_table_denormalised_markers(PATH_DENDROGRAM_JSON, PATH_OUTPUT_TSV)
        output = read_tsv(PATH_OUTPUT_TSV)

        # assert only descendants of the root nodes (except root nodes itself) exist
        self.assertFalse(ALLEN_CLASS + "CS202002013_117" in output)  # root

        self.assertFalse(ALLEN_CLASS+"CS202002013_123" in output) # root
        self.assertTrue(ALLEN_CLASS + "CS202002013_150" in output)  # child
        self.assertTrue(ALLEN_CLASS + "CS202002013_124" in output)  # child
        self.assertTrue(ALLEN_CLASS + "CS202002013_158" in output)  # grand child
        self.assertTrue(ALLEN_CLASS + "CS202002013_3" in output)  # grand child
        self.assertFalse(ALLEN_CLASS + "CS202002013_122" in output)  # parent
        self.assertFalse(ALLEN_CLASS + "CS202002013_120" in output)  # grand parent

        self.assertFalse(ALLEN_CLASS + "CS202002013_103" in output)  # root
        self.assertFalse(ALLEN_CLASS + "CS202002013_220" in output)  # parent

        self.assertFalse(ALLEN_CLASS + "CS202002013_179" in output)  # root
        self.assertTrue(ALLEN_CLASS + "CS202002013_180" in output)  # child
        self.assertTrue(ALLEN_CLASS + "CS202002013_207" in output)  # child
        self.assertTrue(ALLEN_CLASS + "CS202002013_208" in output)  # grand child
        self.assertTrue(ALLEN_CLASS + "CS202002013_83" in output)  # grand child

        self.assertFalse(ALLEN_CLASS + "CS202002013_219" in output)  # parent
        self.assertFalse(ALLEN_CLASS + "CS202002013_220" in output)  # grand parent


def read_tsv(tsv_path):
    records = {}
    with open(tsv_path) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        for row in rd:
            _id = row[0]
            records[_id] = row

    return records
