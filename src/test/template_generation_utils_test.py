import unittest
import os
import csv
from dendrogram_tools import dend_json_2_nodes_n_edges
from nomenclature_tools import nomenclature_2_nodes_n_edges
from template_generation_utils import get_synonyms_from_taxonomy, get_synonym_pairs, \
    PAIR_SEPARATOR, OR_SEPARATOR, read_taxonomy_config, get_subtrees, read_dendrogram_tree

PATH_DENDROGRAM_JSON = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/CCN202002013.json")
PATH_NOMENCLATURE_CSV = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     "./test_data/nomenclature_table_CCN201912131.csv")


class TemplateUtilsTest(unittest.TestCase):

    def test_get_synonyms_from_taxonomy(self):
        tree = dend_json_2_nodes_n_edges(PATH_DENDROGRAM_JSON)
        nodes = tree['nodes']

        node3_synonyms = get_synonyms_from_taxonomy(nodes[3]).split(OR_SEPARATOR)
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

    def test_nomenclature_nodes_edges(self):
        tree = nomenclature_2_nodes_n_edges(PATH_NOMENCLATURE_CSV)
        nodes = tree['nodes']

        self.assertEqual(177, len(nodes))
        self.assertEqual("CS201912131_4", nodes[3]["cell_set_accession"])
        self.assertEqual("CS201912131_21", nodes[20]["cell_set_accession"])
        self.assertEqual("CS201912131_51", nodes[50]["cell_set_accession"])
        self.assertEqual("CS201912131_181", nodes[176]["cell_set_accession"])

        edges = tree['edges']
        self.assertTrue(("CS201912131_41", "CS201912131_163") in edges)
        self.assertTrue(("CS201912131_40", "CS201912131_144") in edges)
        self.assertTrue(("CS201912131_39", "CS201912131_160") in edges)
        self.assertTrue(("CS201912131_38", "CS201912131_162") in edges)

    # not test
    def report_missing_alias(self):
        dend_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms/CCN202002013.json")
        dend = dend_json_2_nodes_n_edges(dend_path)
        dend_tree = read_dendrogram_tree(dend_path)

        subtrees = get_subtrees(dend_tree, read_taxonomy_config("CCN202002013"))

        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/alias_report.tsv")

        with open(path, mode='w') as out:
            writer = csv.writer(out, delimiter="\t", quotechar='"')
            writer.writerow(["ID", "cell_set_additional_alias", "cell_set_aligned_alias"])
            for o in dend['nodes']:
                if o['cell_set_accession'] in set.union(*subtrees) and not o['cell_set_preferred_alias']:
                    if o['cell_set_additional_aliases'] or o['cell_set_aligned_alias']:
                        additional_alias = o['cell_set_additional_aliases'] if 'cell_set_additional_aliases' in o.keys() else ''
                        aligned_alias = o['cell_set_aligned_alias'] if 'cell_set_aligned_alias' in o.keys() else ''
                        writer.writerow([o['cell_set_accession'], additional_alias, aligned_alias])


if __name__ == '__main__':
    unittest.main()
