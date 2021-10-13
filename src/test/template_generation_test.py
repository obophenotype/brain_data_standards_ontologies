import unittest
import os

from template_generation_tools import generate_base_class_template, generate_cross_species_template, \
    generate_non_taxonomy_classification_template
from template_generation_utils import read_tsv, migrate_manual_curations

PATH_DENDROGRAM_JSON = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/CCN202002013.json")
PATH_NOMENCLATURE_TABLE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                       "./test_data/nomenclature_table_CCN201912131.csv")
PATH_MARKER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/CS202002013_markers.tsv")
PATH_OUTPUT_CLASS_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/output_class.tsv")
PATH_OUTPUT_NON_TAXON_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         "./test_data/output_non_taxon.tsv")
PATH_OUTPUT_NOMENCLATURE_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/nomenclature.tsv")
PATH_GENERIC_OUTPUT_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                       "./test_data/output_generic.tsv")

ALLEN_CLASS = "http://www.semanticweb.org/brain_data_standards/AllenDendClass_"


def delete_file(path_to_file):
    if os.path.exists(path_to_file):
        os.remove(path_to_file)


class TemplateGenerationTest(unittest.TestCase):

    def setUp(self):
        delete_file(PATH_OUTPUT_CLASS_TSV)
        delete_file(PATH_OUTPUT_NON_TAXON_TSV)
        delete_file(PATH_OUTPUT_NOMENCLATURE_TSV)
        delete_file(PATH_GENERIC_OUTPUT_TSV)

    def tearDown(self):
        delete_file(PATH_OUTPUT_CLASS_TSV)
        delete_file(PATH_OUTPUT_NON_TAXON_TSV)
        delete_file(PATH_OUTPUT_NOMENCLATURE_TSV)
        delete_file(PATH_GENERIC_OUTPUT_TSV)

    def test_curated_class_template_generation(self):
        generate_base_class_template(PATH_DENDROGRAM_JSON, PATH_OUTPUT_CLASS_TSV)
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

    def test_curated_class_template_generation_with_nomenclature(self):
        generate_base_class_template(PATH_NOMENCLATURE_TABLE, PATH_OUTPUT_CLASS_TSV)
        output = read_tsv(PATH_OUTPUT_CLASS_TSV)

        # assert only descendants of the root nodes (except root nodes itself) exist
        self.assertFalse(ALLEN_CLASS + "CS201912131_149" in output)  # root

        self.assertTrue(ALLEN_CLASS + "CS201912131_22" in output)  # child
        self.assertTrue(ALLEN_CLASS + "CS201912131_70" in output)  # child

        self.assertTrue(ALLEN_CLASS + "CS201912131_125" in output)  # root & leaf
        self.assertFalse(ALLEN_CLASS + "CS201912131_148" in output)  # parent

    def test_non_taxonomy_classification_template_generation(self):
        generate_non_taxonomy_classification_template(PATH_DENDROGRAM_JSON, PATH_OUTPUT_NON_TAXON_TSV)
        output = read_tsv(PATH_OUTPUT_NON_TAXON_TSV)

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

    def test_cross_species_template_generation_json(self):
        generate_cross_species_template(PATH_DENDROGRAM_JSON, PATH_GENERIC_OUTPUT_TSV)
        output = read_tsv(PATH_GENERIC_OUTPUT_TSV)

        # non matching nodes
        self.assertFalse(ALLEN_CLASS + "CS202002013_94" in output)
        self.assertFalse(ALLEN_CLASS + "CS202002013_212" in output)

        # aligned alias matching
        self.assertTrue(ALLEN_CLASS + "CS202002013_8" in output)
        self.assertEqual(ALLEN_CLASS + "CS202002270_4", output[ALLEN_CLASS + "CS202002013_8"][1])
        self.assertTrue(ALLEN_CLASS + "CS202002013_193" in output)
        self.assertEqual(ALLEN_CLASS + "CS202002270_53", output[ALLEN_CLASS + "CS202002013_193"][1])

        # taxon additional_aliases -> cross species preferred_alias
        self.assertTrue(ALLEN_CLASS + "CS202002013_211" in output)
        self.assertEqual(ALLEN_CLASS + "CS202002270_39", output[ALLEN_CLASS + "CS202002013_211"][1])

    def test_cross_species_template_generation_nomenclature(self):
        generate_cross_species_template(PATH_NOMENCLATURE_TABLE, PATH_GENERIC_OUTPUT_TSV)
        output = read_tsv(PATH_GENERIC_OUTPUT_TSV)

        # aligned alias matching
        self.assertTrue(ALLEN_CLASS + "CS201912131_72" in output)
        self.assertEqual(ALLEN_CLASS + "CS202002270_24", output[ALLEN_CLASS + "CS201912131_72"][1])
        self.assertTrue(ALLEN_CLASS + "CS201912131_127" in output)
        self.assertEqual(ALLEN_CLASS + "CS202002270_45", output[ALLEN_CLASS + "CS201912131_127"][1])

        # taxon additional_aliases -> cross species preferred_alias
        self.assertTrue(ALLEN_CLASS + "CS201912131_11" in output)
        self.assertEqual(ALLEN_CLASS + "CS202002270_6", output[ALLEN_CLASS + "CS201912131_11"][1])
        self.assertTrue(ALLEN_CLASS + "CS201912131_171" in output)
        self.assertEqual(ALLEN_CLASS + "CS202002270_25", output[ALLEN_CLASS + "CS201912131_171"][1])

    # not test
    # def test_curated_class_migrate(self):
    #     migrate_columns = ["Curated_synonyms", "Classification", "Classification_comment", "Classification_pub",
    #                        "Expresses", "Expresses_comment", "Expresses_pub", "Projection_type", "Layers"]
    #     migrate_manual_curations("../patterns/data/default/CCN201912131_class_curation_old.tsv",
    #                              "../patterns/data/default/CCN201912131_class_curation.tsv",
    #                              migrate_columns,
    #                              "../patterns/data/default/CCN201912131_class_curation_migrate.tsv")
    #
    #     migrate_manual_curations("../patterns/data/default/CCN201912132_class_curation_old.tsv",
    #                              "../patterns/data/default/CCN201912132_class_curation.tsv",
    #                              migrate_columns,
    #                              "../patterns/data/default/CCN201912132_class_curation_migrate.tsv")
    #
    #     migrate_manual_curations("../patterns/data/default/CCN202002013_class_curation_old.tsv",
    #                              "../patterns/data/default/CCN202002013_class_curation.tsv",
    #                              migrate_columns,
    #                              "../patterns/data/default/CCN202002013_class_curation_migrate.tsv")
    #
    #     migrate_manual_curations("../patterns/data/default/CCN202002270_class_curation_old.tsv",
    #                              "../patterns/data/default/CCN202002270_class_curation.tsv",
    #                              migrate_columns,
    #                              "../patterns/data/default/CCN202002270_class_curation_migrate.tsv")


