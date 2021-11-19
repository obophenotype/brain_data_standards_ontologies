import unittest
from pcl_id_factory import get_class_id, get_individual_id, taxonomy_ids, get_taxonomy_id


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

        self.assertEqual(get_individual_id("CS202002013_1"), "0011401")
        self.assertEqual(get_individual_id("CS202002013_121"), "0011521")

    def test_human_ids(self):
        self.assertEqual(get_class_id("CS201912131_1"), "0012001")
        self.assertEqual(get_class_id("CS201912131_121"), "0012121")

        self.assertEqual(get_individual_id("CS201912131_1"), "0012401")
        self.assertEqual(get_individual_id("CS201912131_121"), "0012521")

    def test_marmoset_ids(self):
        self.assertEqual(get_class_id("CS201912132_1"), "0013001")
        self.assertEqual(get_class_id("CS201912132_121"), "0013121")

        self.assertEqual(get_individual_id("CS201912132_1"), "0013401")
        self.assertEqual(get_individual_id("CS201912132_121"), "0013521")

    def test_human_mtg_ids(self):
        self.assertEqual(get_class_id("CS1908210001"), "0014001")
        self.assertEqual(get_class_id("CS1908210148"), "0014148")

        self.assertEqual(get_individual_id("CS1908210001"), "0014401")
        self.assertEqual(get_individual_id("CS1908210148"), "0014548")

    def test_taxonomy_id(self):
        self.assertEqual(get_taxonomy_id("CS202002013"), "0011000")
        self.assertEqual(get_taxonomy_id("CCN202002013"), "0011000")

        self.assertEqual(get_taxonomy_id("CS201912131"), "0012000")
        self.assertEqual(get_taxonomy_id("CCN201912131"), "0012000")

        self.assertEqual(get_taxonomy_id("CS201912132"), "0013000")
        self.assertEqual(get_taxonomy_id("CCN201912132"), "0013000")

        self.assertEqual(get_taxonomy_id("CS1908210"), "0014000")


if __name__ == '__main__':
    unittest.main()
