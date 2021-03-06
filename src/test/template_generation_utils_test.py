import unittest
import os
from dendrogram_tools import dend_json_2_nodes_n_edges
from template_generation_utils import get_synonyms_from_taxonomy, get_synonym_pairs, \
    PAIR_SEPARATOR, OR_SEPARATOR

PATH_DENDROGRAM_JSON = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/CCN202002013.json")


class TemplateUtilsTest(unittest.TestCase):

    def test_get_synonyms_from_taxonomy(self):
        print(PATH_DENDROGRAM_JSON)
        tree = dend_json_2_nodes_n_edges(PATH_DENDROGRAM_JSON)
        nodes = tree['nodes']

        node3_synonyms = get_synonyms_from_taxonomy(nodes[3]).split(OR_SEPARATOR)
        print(nodes[3])
        self.assertEqual("CS202002013_120", nodes[3]["cell_set_accession"])
        self.assertEqual(2, len(node3_synonyms))
        self.assertTrue("n4" in node3_synonyms)
        self.assertTrue("RNAseq 001-091" in node3_synonyms)

        node20_synonyms = get_synonyms_from_taxonomy(nodes[20]).split(OR_SEPARATOR)
        self.assertEqual("CS202002013_6", nodes[20]["cell_set_accession"])
        self.assertEqual(2, len(node20_synonyms))
        self.assertTrue("RNAseq 006" in node20_synonyms)
        self.assertTrue("Lamp5 Pdlim5_2" in node20_synonyms)

        node50_synonyms = get_synonyms_from_taxonomy(nodes[50]).split(OR_SEPARATOR)
        self.assertEqual("CS202002013_146", nodes[50]["cell_set_accession"])
        self.assertEqual(2, len(node50_synonyms))
        self.assertTrue("n30" in node50_synonyms)
        self.assertTrue("RNAseq 022-025" in node50_synonyms)

    def test_get_synonym_pairs(self):
        tree = dend_json_2_nodes_n_edges(PATH_DENDROGRAM_JSON)
        nodes = tree['nodes']

        node3_pairs = get_synonym_pairs(nodes[3]).split(PAIR_SEPARATOR)
        self.assertEqual("CS202002013_120", nodes[3]["cell_set_accession"])
        self.assertEqual(5, len(node3_pairs))
        self.assertTrue("cell_set_preferred_alias:''" in node3_pairs)
        self.assertTrue("original_label:n4" in node3_pairs)
        self.assertTrue("cell_set_label:RNAseq 001-091" in node3_pairs)
        self.assertTrue("cell_set_aligned_alias:''" in node3_pairs)
        self.assertTrue("cell_set_additional_aliases:''" in node3_pairs)

        node20_pairs = get_synonym_pairs(nodes[20]).split(PAIR_SEPARATOR)
        self.assertEqual("CS202002013_6", nodes[20]["cell_set_accession"])
        self.assertEqual(5, len(node20_pairs))
        self.assertTrue("cell_set_preferred_alias:Lamp5 Pdlim5_2" in node20_pairs)
        self.assertTrue("original_label:Lamp5 Pdlim5_2" in node20_pairs)
        self.assertTrue("cell_set_label:RNAseq 006" in node20_pairs)
        self.assertTrue("cell_set_aligned_alias:''" in node20_pairs)
        self.assertTrue("cell_set_additional_aliases:''" in node20_pairs)

        node50_pairs = get_synonym_pairs(nodes[50]).split(PAIR_SEPARATOR)
        self.assertEqual("CS202002013_146", nodes[50]["cell_set_accession"])
        self.assertEqual(5, len(node50_pairs))
        self.assertTrue("cell_set_preferred_alias:''" in node50_pairs)
        self.assertTrue("original_label:n30" in node50_pairs)
        self.assertTrue("cell_set_label:RNAseq 022-025" in node50_pairs)
        self.assertTrue("cell_set_aligned_alias:''" in node50_pairs)
        self.assertTrue("cell_set_additional_aliases:''" in node50_pairs)


if __name__ == '__main__':
    unittest.main()
