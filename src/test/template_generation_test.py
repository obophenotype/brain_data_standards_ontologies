import unittest
import os
import csv

from template_generation_tools import generate_curated_class_template, generate_equivalent_class_marker_template

PATH_DENDROGRAM_JSON = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/CCN202002013.json")
PATH_MARKER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/CS202002013_markers.tsv")
PATH_OUTPUT_CLASS_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/output_class.tsv")
PATH_OUTPUT_EC_MARKER_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         "./test_data/output_equivalent_marker.tsv")

ALLEN_CLASS = "http://www.semanticweb.org/brain_data_standards/AllenDendClass_"


def delete_file(path_to_file):
    if os.path.exists(path_to_file):
        os.remove(path_to_file)


class TemplateGenerationTest(unittest.TestCase):

    def setUp(self):
        delete_file(PATH_OUTPUT_CLASS_TSV)
        delete_file(PATH_OUTPUT_EC_MARKER_TSV)

    def tearDown(self):
        # delete_file(PATH_OUTPUT_CLASS_TSV)
        delete_file(PATH_OUTPUT_EC_MARKER_TSV)

    def test_curated_class_template_generation(self):
        generate_curated_class_template(PATH_DENDROGRAM_JSON, PATH_OUTPUT_CLASS_TSV)
        output = read_class_file(PATH_OUTPUT_CLASS_TSV)

        # assert only descendants of the root nodes (except root nodes itself) exist
        self.assertFalse(ALLEN_CLASS + "CS202002013_117" in output)  # root

        self.assertFalse(ALLEN_CLASS+"CS202002013_123" in output) # root
        self.assertTrue(ALLEN_CLASS + "CS202002013_150" in output)  # child
        self.assertTrue(ALLEN_CLASS + "CS202002013_124" in output)  # child
        self.assertFalse(ALLEN_CLASS + "CS202002013_158" in output)  # grand child, empty cell_set_preferred_alias
        self.assertTrue(ALLEN_CLASS + "CS202002013_3" in output)  # grand child
        self.assertFalse(ALLEN_CLASS + "CS202002013_122" in output)  # parent
        self.assertFalse(ALLEN_CLASS + "CS202002013_120" in output)  # grand parent

        self.assertTrue(ALLEN_CLASS + "CS202002013_103" in output)  # root & leaf
        self.assertFalse(ALLEN_CLASS + "CS202002013_220" in output)  # parent

        self.assertFalse(ALLEN_CLASS + "CS202002013_179" in output)  # root
        self.assertFalse(ALLEN_CLASS + "CS202002013_180" in output)  # child, empty cell_set_preferred_alias
        self.assertTrue(ALLEN_CLASS + "CS202002013_207" in output)  # child
        self.assertFalse(ALLEN_CLASS + "CS202002013_208" in output)  # grand child, empty cell_set_preferred_alias
        self.assertTrue(ALLEN_CLASS + "CS202002013_83" in output)  # grand child

        self.assertFalse(ALLEN_CLASS + "CS202002013_219" in output)  # parent
        self.assertFalse(ALLEN_CLASS + "CS202002013_220" in output)  # grand parent

    def test_equivalent_class_marker_template_generation(self):
        generate_equivalent_class_marker_template(PATH_DENDROGRAM_JSON, PATH_MARKER, PATH_OUTPUT_EC_MARKER_TSV)
        output = read_class_file(PATH_OUTPUT_EC_MARKER_TSV)

        # assert only descendants of the root nodes (except root nodes itself) exist
        self.assertFalse(ALLEN_CLASS + "CS202002013_117" in output)  # root

        self.assertFalse(ALLEN_CLASS+"CS202002013_123" in output) # root
        self.assertFalse(ALLEN_CLASS + "CS202002013_150" in output)  # child, no marker
        self.assertFalse(ALLEN_CLASS + "CS202002013_124" in output)  # child, no marker
        self.assertTrue(ALLEN_CLASS + "CS202002013_28" in output)  # grand child, with marker
        self.assertFalse(ALLEN_CLASS + "CS202002013_158" in output)  # grand child, no marker
        self.assertTrue(ALLEN_CLASS + "CS202002013_35" in output)  # grand child, with marker
        self.assertTrue(ALLEN_CLASS + "CS202002013_3" in output)  # grand child, with marker
        self.assertFalse(ALLEN_CLASS + "CS202002013_122" in output)  # parent
        self.assertFalse(ALLEN_CLASS + "CS202002013_120" in output)  # grand parent

        self.assertTrue(ALLEN_CLASS + "CS202002013_103" in output)  # root & leaf
        self.assertFalse(ALLEN_CLASS + "CS202002013_220" in output)  # parent

        self.assertFalse(ALLEN_CLASS + "CS202002013_179" in output)  # root
        self.assertFalse(ALLEN_CLASS + "CS202002013_180" in output)  # child, no marker
        self.assertTrue(ALLEN_CLASS + "CS202002013_207" in output)  # child, with marker
        self.assertFalse(ALLEN_CLASS + "CS202002013_208" in output)  # grand child, no marker
        self.assertTrue(ALLEN_CLASS + "CS202002013_83" in output)  # grand child, with marker

        self.assertFalse(ALLEN_CLASS + "CS202002013_219" in output)  # parent
        self.assertFalse(ALLEN_CLASS + "CS202002013_220" in output)  # grand parent

    # def test_migrate(self):
    #     curated_class_migrate()


def read_class_file(class_template):
    records = {}
    with open(class_template) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        for row in rd:
            _id = row[0]
            records[_id] = row

    return records


def curated_class_migrate():
    migrate_columns = [5, 6, 7]
    # curation_table_migrate_manual_edits("./test_data/source_class.tsv", "./test_data/target_class.tsv", migrate_columns)
    curation_table_migrate_manual_edits("../templates/CCN202002013_class_old.tsv",
                                        "../templates/CCN202002013_class.tsv", migrate_columns)


def curation_table_migrate_manual_edits(source_path, target_path, migrate_columns):
    source = read_class_file(source_path)
    target = read_class_file(target_path)

    new_target_path = target_path.replace(".tsv", "_migrate.tsv")

    with open(new_target_path, mode='w') as out:
        writer = csv.writer(out, delimiter="\t", quotechar='"')

        for key, row in target.items():
            if key in source:
                # copy migrate columns
                for migrate_column in migrate_columns:
                    row[migrate_column] = source.get(key)[migrate_column]

            writer.writerow(row)
