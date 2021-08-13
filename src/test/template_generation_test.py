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

    def test_equivalent_class_marker_template_generation(self):
        generate_equivalent_class_marker_template(PATH_DENDROGRAM_JSON, PATH_MARKER, PATH_OUTPUT_EC_MARKER_TSV)
        output = read_tsv(PATH_OUTPUT_EC_MARKER_TSV)

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

    def test_non_taxonomy_classification_template_generation(self):
        generate_non_taxonomy_classification_template(PATH_DENDROGRAM_JSON, PATH_OUTPUT_EC_MARKER_TSV)
        output = read_tsv(PATH_OUTPUT_EC_MARKER_TSV)

        # assert only descendants of the root nodes (except root nodes itself) exist
        self.assertFalse(ALLEN_CLASS + "CS202002013_258" in output)  # root
        self.assertFalse(ALLEN_CLASS + "CS202002013_237" in output)  # root
        self.assertFalse(ALLEN_CLASS + "CS202002013_232" in output)  # root
        self.assertFalse(ALLEN_CLASS + "CS202002013_261" in output)  # root

        self.assertTrue(ALLEN_CLASS + "CS202002013_29" in output)  # child of CS202002013_232
        self.assertEqual("CL:4023017", output[ALLEN_CLASS + "CS202002013_29"][1])
        self.assertTrue(ALLEN_CLASS + "CS202002013_32" in output)  # child of CS202002013_232
        self.assertEqual("CL:4023017", output[ALLEN_CLASS + "CS202002013_32"][1])
        self.assertTrue(ALLEN_CLASS + "CS202002013_40" in output)  # child of CS202002013_232
        self.assertEqual("CL:4023017", output[ALLEN_CLASS + "CS202002013_40"][1])
        self.assertTrue(ALLEN_CLASS + "CS202002013_47" in output)  # child of CS202002013_232
        self.assertEqual("CL:4023017", output[ALLEN_CLASS + "CS202002013_47"][1])

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
    migrate_columns = [5, 6, 7, 8, 9, 10]
    curation_table_migrate_manual_edits("../patterns/data/bds/CCN202002013_class_old.tsv",
                                        "../patterns/data/bds/CCN202002013_class.tsv", migrate_columns)


def curated_dosdp_migrate():
    migrate_columns = [8, 9]
    curation_table_migrate_manual_edits("../patterns/data/default/brainCellRegionMinimalMarkers_backup.tsv",
                                        "../patterns/data/default/brainCellRegionMinimalMarkers.tsv", migrate_columns)

def curation_table_migrate_manual_edits(source_path, target_path, migrate_columns):
    source = read_tsv(source_path)
    target = read_tsv(target_path)

    new_target_path = target_path.replace(".tsv", "_migrate.tsv")

    with open(new_target_path, mode='w') as out:
        writer = csv.writer(out, delimiter="\t", quotechar='"')

        for key, row in target.items():
            if key in source:
                # copy migrate columns
                for migrate_column in migrate_columns:
                    if len(source.get(key)) > migrate_column:
                        row[migrate_column] = source.get(key)[migrate_column]
                    else:
                        row[migrate_column] = ""

            writer.writerow(row)
