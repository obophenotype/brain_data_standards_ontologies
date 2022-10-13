import unittest
from pcl_id_factory import get_class_id, get_individual_id, taxonomy_ids, get_taxonomy_id, get_reverse_id
from template_generation_utils import migrate_manual_curations


class PCLIdFactoryTestCase(unittest.TestCase):

    def test_taxonomy_ids_parsing(self):
        self.assertTrue(len(taxonomy_ids) >= 4)
        self.assertEqual("CCN202002013", taxonomy_ids[0])
        self.assertEqual("CCN201912131", taxonomy_ids[1])
        self.assertEqual("CCN201912132", taxonomy_ids[2])
        self.assertEqual("CS1908210", taxonomy_ids[3])

    def test_mouse_ids(self):
        self.assertEqual(get_class_id("CS202002013_1"), "0011001")
        self.assertEqual(get_class_id("CS202002013_121"), "0011121")

        self.assertEqual(get_individual_id("CS202002013_1"), "0011501")
        self.assertEqual(get_individual_id("CS202002013_121"), "0011621")

    def test_human_ids(self):
        self.assertEqual(get_class_id("CS201912131_1"), "0015001")
        self.assertEqual(get_class_id("CS201912131_121"), "0015121")

        self.assertEqual(get_individual_id("CS201912131_1"), "0015501")
        self.assertEqual(get_individual_id("CS201912131_121"), "0015621")

    def test_marmoset_ids(self):
        self.assertEqual(get_class_id("CS201912132_1"), "0019001")
        self.assertEqual(get_class_id("CS201912132_121"), "0019121")

        self.assertEqual(get_individual_id("CS201912132_1"), "0019501")
        self.assertEqual(get_individual_id("CS201912132_121"), "0019621")

    def test_human_mtg_ids(self):
        self.assertEqual(get_class_id("CS1908210001"), "0023001")
        self.assertEqual(get_class_id("CS1908210148"), "0023148")

        self.assertEqual(get_individual_id("CS1908210001"), "0023501")
        self.assertEqual(get_individual_id("CS1908210148"), "0023648")

    def test_taxonomy_id(self):
        self.assertEqual(get_taxonomy_id("CS202002013"), "0011000")
        self.assertEqual(get_taxonomy_id("CCN202002013"), "0011000")

        self.assertEqual(get_taxonomy_id("CS201912131"), "0015000")
        self.assertEqual(get_taxonomy_id("CCN201912131"), "0015000")

        self.assertEqual(get_taxonomy_id("CS201912132"), "0019000")
        self.assertEqual(get_taxonomy_id("CCN201912132"), "0019000")

        self.assertEqual(get_taxonomy_id("CS1908210"), "0023000")

    def test_reverse_id(self):
        self.assertEqual(get_reverse_id("0011001"), "CS202002013_1")
        self.assertEqual(get_reverse_id("PCL_0011001"), "CS202002013_1")
        self.assertEqual(get_reverse_id("PCL:0011001"), "CS202002013_1")
        self.assertEqual(get_reverse_id("http://purl.obolibrary.org/obo/PCL_0011001"), "CS202002013_1")

        self.assertEqual(get_reverse_id("0011621"), "CS202002013_121")
        self.assertEqual(get_reverse_id("0015121"), "CS201912131_121")
        self.assertEqual(get_reverse_id("0019501"), "CS201912132_1")
        self.assertEqual(get_reverse_id("0023648"), "CS1908210148")
        self.assertEqual(get_reverse_id("0023001"), "CS1908210001")

    # not test
    # def test_allen_markers_migrate(self):
    #     migrate_columns = ["Obsoleted By"]
    #     migrate_manual_curations("../templates/pCL_mapping_old.tsv",
    #                              "../templates/pCL_mapping.tsv",
    #                              migrate_columns,
    #                              "../templates/pCL_mapping_merged.tsv")


if __name__ == '__main__':
    unittest.main()
