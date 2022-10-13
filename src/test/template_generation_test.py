import unittest
import os

from template_generation_tools import generate_base_class_template, \
    generate_ind_template, generate_homologous_to_template
from template_generation_utils import read_tsv, migrate_manual_curations
from pcl_id_factory import get_class_id, get_taxonomy_id, get_individual_id

current_dir = os.path.dirname(os.path.realpath(__file__))
ALL_BASE_FILES = [os.path.join(current_dir, "../patterns/data/default/CCN202002013_class_base.tsv"),
                  os.path.join(current_dir, "../patterns/data/default/CCN201912131_class_base.tsv"),
                  os.path.join(current_dir, "../patterns/data/default/CCN201912132_class_base.tsv"),
                  os.path.join(current_dir, "../patterns/data/default/CS1908210_class_base.tsv")]

PATH_MOUSE_NOMENCLATURE = os.path.join(current_dir, "../dendrograms/nomenclature_table_CCN202002013.csv")
# PATH_NOMENCLATURE_TABLE = os.path.join(current_dir, "./test_data/nomenclature_table_CCN201912131.csv")
PATH_NOMENCLATURE_TABLE = os.path.join(current_dir, "../dendrograms/nomenclature_table_CCN201912131.csv")
PATH_MARKER = os.path.join(current_dir, "./test_data/CS202002013_markers.tsv")
PATH_OUTPUT_CLASS_TSV = os.path.join(current_dir, "./test_data/output_class.tsv")
PATH_OUTPUT_NON_TAXON_TSV = os.path.join(current_dir, "./test_data/output_non_taxon.tsv")
PATH_OUTPUT_NOMENCLATURE_TSV = os.path.join(current_dir, "./test_data/nomenclature.tsv")
PATH_GENERIC_OUTPUT_TSV = os.path.join(current_dir, "./test_data/output_generic.tsv")
PATH_CENTRALIZED_DATA = os.path.join(current_dir, "./test_data/centralized_data/MOp_taxonomies_ontology/")

PCL_BASE = "http://purl.obolibrary.org/obo/PCL_"


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

    def test_generate_ind_template(self):
        generate_ind_template(PATH_MOUSE_NOMENCLATURE, PATH_CENTRALIZED_DATA, PATH_GENERIC_OUTPUT_TSV)
        output = read_tsv(PATH_GENERIC_OUTPUT_TSV)

        _label = 2
        _description = 18
        _aliases = 19
        _rank = 20

        self.assertTrue("PCL_INDV:"+"CS202002013_123" in output)  # child
        test_node = output["PCL_INDV:"+"CS202002013_123"]
        self.assertEqual("GABAergic", str(test_node[2]))
        self.assertTrue(str(test_node[_description]).startswith("GABAergic is: Neurons that use GABA as a neurotransmitter"))
        self.assertEqual("Neuronal: GABAergic|Inhibitory neurons", test_node[_aliases])
        self.assertEqual("Class", test_node[_rank])

        self.assertTrue("PCL_INDV:CS202002013_219" in output)  # child
        test_node = output["PCL_INDV:CS202002013_219"]
        self.assertEqual("Non-neural", str(test_node[2]))
        self.assertTrue(
            str(test_node[_description]).startswith("Non-Neural is: Cells of mesoderm"))
        self.assertEqual("", test_node[_aliases])
        self.assertEqual("Class", test_node[_rank])

        self.assertEqual("Cell Type|Subclass", output["PCL_INDV:CS202002013_112"][_rank])

    def test_base_class_template_generation(self):
        generate_base_class_template(PATH_MOUSE_NOMENCLATURE, PATH_OUTPUT_CLASS_TSV)
        output = read_tsv(PATH_OUTPUT_CLASS_TSV)

        self.assertTrue(PCL_BASE + get_class_id("CS202002013_150") in output)  # child

        # assert only descendants of the root nodes (except root nodes itself) exist
        self.assertFalse(PCL_BASE + get_class_id("CS202002013_117") in output)  # root

        self.assertFalse(PCL_BASE + get_class_id("CS202002013_123") in output) # root
        self.assertTrue(PCL_BASE + get_class_id("CS202002013_150") in output)  # child
        self.assertTrue(PCL_BASE + get_class_id("CS202002013_124") in output)  # child
        self.assertFalse(PCL_BASE + get_class_id("CS202002013_158") in output)  # grand child, empty cell_set_preferred_alias
        self.assertTrue(PCL_BASE + get_class_id("CS202002013_3") in output)  # grand child
        self.assertFalse(PCL_BASE + get_class_id("CS202002013_122") in output)  # parent
        self.assertFalse(PCL_BASE + get_class_id("CS202002013_120") in output)  # grand parent

        self.assertTrue(PCL_BASE + get_class_id("CS202002013_103") in output)  # root & leaf
        self.assertFalse(PCL_BASE + get_class_id("CS202002013_220") in output)  # parent

        self.assertFalse(PCL_BASE + get_class_id("CS202002013_179") in output)  # root
        self.assertFalse(PCL_BASE + get_class_id("CS202002013_180") in output)  # child, empty cell_set_preferred_alias
        self.assertTrue(PCL_BASE + get_class_id("CS202002013_207") in output)  # child
        self.assertFalse(PCL_BASE + get_class_id("CS202002013_208") in output)  # grand child, empty cell_set_preferred_alias
        self.assertTrue(PCL_BASE + get_class_id("CS202002013_83") in output)  # grand child

        self.assertFalse(PCL_BASE + get_class_id("CS202002013_219") in output)  # parent
        self.assertFalse(PCL_BASE + get_class_id("CS202002013_220") in output)  # grand parent

    def test_base_class_template_generation_with_nomenclature(self):
        generate_base_class_template(PATH_NOMENCLATURE_TABLE, PATH_OUTPUT_CLASS_TSV)
        output = read_tsv(PATH_OUTPUT_CLASS_TSV)

        # assert only descendants of the root nodes (except root nodes itself) exist
        self.assertFalse(PCL_BASE + get_class_id("CS201912131_149") in output)  # root

        self.assertTrue(PCL_BASE + get_class_id("CS201912131_22") in output)  # child
        self.assertTrue(PCL_BASE + get_class_id("CS201912131_70") in output)  # child

        self.assertTrue(PCL_BASE + get_class_id("CS201912131_125") in output)  # root & leaf
        self.assertFalse(PCL_BASE + get_class_id("CS201912131_148") in output)  # parent

    def test_homologous_to_template_generation(self):
        generate_homologous_to_template(PATH_NOMENCLATURE_TABLE, ALL_BASE_FILES, PATH_OUTPUT_CLASS_TSV)
        output = read_tsv(PATH_OUTPUT_CLASS_TSV)

        self.assertTrue(PCL_BASE + get_class_id("CS201912131_164") in output)
        test_node = output[PCL_BASE + get_class_id("CS201912131_164")]
        homologous_to = test_node[1].split("|")
        self.assertEqual(2, len(homologous_to))
        self.assertTrue(PCL_BASE + get_class_id("CS201912132_039") in homologous_to)
        self.assertTrue(PCL_BASE + get_class_id("CS202002013_244") in homologous_to)

        self.assertTrue(PCL_BASE + get_class_id("CS201912131_176") in output)
        test_node = output[PCL_BASE + get_class_id("CS201912131_176")]
        homologous_to = test_node[1].split("|")
        self.assertEqual(2, len(homologous_to))
        self.assertTrue(PCL_BASE + get_class_id("CS201912132_060") in homologous_to)
        self.assertTrue(PCL_BASE + get_class_id("CS202002013_067") in homologous_to)

        self.assertTrue(PCL_BASE + get_class_id("CS201912131_157") in output)
        test_node = output[PCL_BASE + get_class_id("CS201912131_157")]
        homologous_to = test_node[1].split("|")
        self.assertEqual(1, len(homologous_to))
        self.assertTrue(PCL_BASE + get_class_id("CS201912132_002") in homologous_to)

        self.assertTrue(PCL_BASE + get_class_id("CS201912131_142") in output)  # human Astrocyte
        test_node = output[PCL_BASE + get_class_id("CS201912131_142")]
        homologous_to = test_node[1]
        self.assertFalse(homologous_to)  # mouse and marmoset astro not exists

    # not test
    # def test_curated_class_migrate(self):
    #     migrate_columns = ["Curated_synonyms", "Classification", "Classification_comment", "Classification_pub",
    #                        "Expresses", "Expresses_comment", "Expresses_pub", "Projection_type", "Layers",
    #                        "Cross_species_text", "Comment"]
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
    #     migrate_manual_curations("../patterns/data/default/CS1908210_class_curation_old.tsv",
    #                              "../patterns/data/default/CS1908210_class_curation.tsv",
    #                              migrate_columns,
    #                              "../patterns/data/default/CS1908210_class_curation_migrate.tsv")

    # def test_allen_markers_migrate(self):
    #     # in the curation table change Expresses column name to Markers
    #     migrate_columns = ["Markers"]
    #     migrate_manual_curations("../patterns/data/default/CS1908210_class_curation_old.tsv",
    #                              "../markers/CS1908210_Allen_markers_old.tsv",
    #                              migrate_columns,
    #                              "../markers/CS1908210_Allen_markers.tsv", use_accession_ids=True)
    #     # migrate_manual_curations("../patterns/data/default/CCN201912131_class_curation_old.tsv",
    #     #                          "../markers/CS201912131_Allen_markers_old.tsv",
    #     #                          migrate_columns,
    #     #                          "../markers/CS201912131_Allen_markers.tsv", use_accession_ids=True)
