import unittest
import os
import csv

from template_generation_tools import generate_curated_class_template, generate_equivalent_class_marker_template\
    , generate_non_taxonomy_classification_template
from template_generation_utils import read_tsv

PATH_DENDROGRAM_JSON = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/CCN202002013.json")
PATH_MARKER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/CS202002013_markers.tsv")
PATH_OUTPUT_CLASS_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/output_class.tsv")
PATH_OUTPUT_EC_MARKER_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         "./test_data/output_equivalent_marker.tsv")
PATH_OUTPUT_NOMENCLATURE_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/nomenclature.tsv")

ALLEN_CLASS = "http://www.semanticweb.org/brain_data_standards/AllenDendClass_"


def delete_file(path_to_file):
    if os.path.exists(path_to_file):
        os.remove(path_to_file)


class TemplateGenerationTest(unittest.TestCase):

    def setUp(self):
        delete_file(PATH_OUTPUT_CLASS_TSV)
        delete_file(PATH_OUTPUT_EC_MARKER_TSV)
        delete_file(PATH_OUTPUT_NOMENCLATURE_TSV)

    def tearDown(self):
        delete_file(PATH_OUTPUT_CLASS_TSV)
        delete_file(PATH_OUTPUT_EC_MARKER_TSV)
        delete_file(PATH_OUTPUT_NOMENCLATURE_TSV)

    def test_curated_class_template_generation(self):
        generate_curated_class_template(PATH_DENDROGRAM_JSON, PATH_OUTPUT_CLASS_TSV)
        output = read_tsv(PATH_OUTPUT_CLASS_TSV)

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

    # def test_equivalent_class_marker_template_generation(self):
    #     generate_equivalent_class_marker_template(PATH_DENDROGRAM_JSON, PATH_MARKER, PATH_OUTPUT_EC_MARKER_TSV)
    #     output = read_tsv(PATH_OUTPUT_EC_MARKER_TSV)
    #
    #     # assert only descendants of the root nodes (except root nodes itself) exist
    #     self.assertFalse(ALLEN_CLASS + "CS202002013_117" in output)  # root
    #
    #     self.assertFalse(ALLEN_CLASS+"CS202002013_123" in output) # root
    #     self.assertFalse(ALLEN_CLASS + "CS202002013_150" in output)  # child, no marker
    #     self.assertFalse(ALLEN_CLASS + "CS202002013_124" in output)  # child, no marker
    #     self.assertTrue(ALLEN_CLASS + "CS202002013_28" in output)  # grand child, with marker
    #     self.assertFalse(ALLEN_CLASS + "CS202002013_158" in output)  # grand child, no marker
    #     self.assertTrue(ALLEN_CLASS + "CS202002013_35" in output)  # grand child, with marker
    #     self.assertTrue(ALLEN_CLASS + "CS202002013_3" in output)  # grand child, with marker
    #     self.assertFalse(ALLEN_CLASS + "CS202002013_122" in output)  # parent
    #     self.assertFalse(ALLEN_CLASS + "CS202002013_120" in output)  # grand parent
    #
    #     self.assertTrue(ALLEN_CLASS + "CS202002013_103" in output)  # root & leaf
    #     self.assertFalse(ALLEN_CLASS + "CS202002013_220" in output)  # parent
    #
    #     self.assertFalse(ALLEN_CLASS + "CS202002013_179" in output)  # root
    #     self.assertFalse(ALLEN_CLASS + "CS202002013_180" in output)  # child, no marker
    #     self.assertTrue(ALLEN_CLASS + "CS202002013_207" in output)  # child, with marker
    #     self.assertFalse(ALLEN_CLASS + "CS202002013_208" in output)  # grand child, no marker
    #     self.assertTrue(ALLEN_CLASS + "CS202002013_83" in output)  # grand child, with marker
    #
    #     self.assertFalse(ALLEN_CLASS + "CS202002013_219" in output)  # parent
    #     self.assertFalse(ALLEN_CLASS + "CS202002013_220" in output)  # grand parent

    def test_non_taxonomy_classification_template_generation(self):
        generate_non_taxonomy_classification_template(PATH_DENDROGRAM_JSON, PATH_OUTPUT_EC_MARKER_TSV)
        output = read_tsv(PATH_OUTPUT_EC_MARKER_TSV)

        # assert only descendants of the root nodes (except root nodes itself) exist
        self.assertFalse(ALLEN_CLASS + "CS202002013_258" in output)  # root
        self.assertFalse(ALLEN_CLASS + "CS202002013_237" in output)  # root
        self.assertFalse(ALLEN_CLASS + "CS202002013_232" in output)  # root
        self.assertFalse(ALLEN_CLASS + "CS202002013_261" in output)  # root

        self.assertTrue(ALLEN_CLASS + "CS202002013_114" in output)  # child of CS202002013_237
        self.assertEqual("CL:0000881", output[ALLEN_CLASS + "CS202002013_114"][1])
        self.assertTrue(ALLEN_CLASS + "CS202002013_115" in output)  # child of CS202002013_237
        self.assertEqual("CL:0000881", output[ALLEN_CLASS + "CS202002013_115"][1])
        self.assertTrue(ALLEN_CLASS + "CS202002013_116" in output)  # child of CS202002013_237
        self.assertEqual("CL:0000881", output[ALLEN_CLASS + "CS202002013_116"][1])

    # def test_migrate(self):
    #     curated_class_migrate()

    # def test_migrate_dosdp(self):
    #     curated_dosdp_migrate()


def curated_class_migrate():
    migrate_columns = ["Curated_synonyms", "Classification", "Classification_comment", "Classification_pub",
                       "Expresses", "Expresses_comment", "Expresses_pub", "Projection_type", "Layers"]
    curation_table_migrate_manual_edits("../patterns/data/bds/CCN202002013_class_old.tsv",
                                        "../patterns/data/bds/CCN202002013_class.tsv", migrate_columns)


# def curated_dosdp_migrate():
#     migrate_columns = ["Projection_type", "Layers"]
#     curation_table_migrate_manual_edits("../patterns/data/default/brainCellRegionMinimalMarkers.tsv",
#                                         "../patterns/data/bds/CCN202002013_class.tsv", migrate_columns)


def curation_table_migrate_manual_edits(source_path, target_path, migrate_columns):
    source_headers, source = read_tsv_to_dict(source_path)
    target_headers, target = read_tsv_to_dict(target_path)

    new_target_path = target_path.replace(".tsv", "_migrate.tsv")

    with open(new_target_path, mode='w') as out:
        writer = csv.writer(out, delimiter="\t", quotechar='"')
        writer.writerow(target_headers)

        for key, row_data in target.items():
            if key in source:
                # copy migrate columns
                for migrate_column in migrate_columns:
                    if migrate_column in source[key]:
                        row_data[migrate_column] = source[key][migrate_column]

            row = list()
            for column in target_headers:
                row.append(row_data[column])

            writer.writerow(row)


def read_tsv_to_dict(tsv_path, id_column=0):
    return read_csv_to_dict(tsv_path, id_column=id_column, delimiter="\t")


def read_csv_to_dict(csv_path, id_column=0, delimiter=",", id_to_lower=False):
    records = dict()

    headers = []
    with open(csv_path) as fd:
        rd = csv.reader(fd, delimiter=delimiter, quotechar='"')
        row_count = 0
        for row in rd:
            _id = row[id_column]
            if id_to_lower:
                _id = str(_id).lower()

            if row_count == 0:
                headers = row
            else:
                row_object = dict()
                for column_num, column_value in enumerate(row):
                    row_object[headers[column_num]] = column_value
                records[_id] = row_object

            row_count += 1

    return headers, records
