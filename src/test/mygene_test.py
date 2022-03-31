import unittest
from ensembl import mygene_get_synonyms


class MyGeneApiTest(unittest.TestCase):

    def test_list_response(self):
        gene_synonyms = mygene_get_synonyms(["ensembl:ENSMUSG00000033774"])

        synonyms = gene_synonyms["ENSMUSG00000033774"]
        self.assertTrue("Gpr7" in synonyms)
        self.assertTrue("Nbpwr1" in synonyms)
        self.assertTrue("G protein-coupled receptor 7" in synonyms)
        self.assertTrue("neuropeptides B/W receptor type 1" in synonyms)

    def test_single_value_response(self):
        gene_synonyms = mygene_get_synonyms(["entrez:102465909"])

        synonyms = gene_synonyms["102465909"]
        self.assertTrue("hsa-mir-6859-2" in synonyms)
        self.assertTrue("microRNA mir-6859-2" in synonyms)

    def test_no_value_response(self):
        gene_synonyms = mygene_get_synonyms(["entrez:105378580"])

        synonyms = gene_synonyms["105378580"]
        self.assertEqual(0, len(synonyms))

    def test_multiple_genes(self):
        gene_synonyms = mygene_get_synonyms(["ensembl:ENSMUSG00000033774", "entrez:102465909", "entrez:105378580", "entrez:not_exists"])

        self.assertEqual(4, len(gene_synonyms["ENSMUSG00000033774"]))
        self.assertEqual(2, len(gene_synonyms["102465909"]))
        self.assertEqual(0, len(gene_synonyms["105378580"]))
        self.assertEqual(0, len(gene_synonyms["not_exists"]))
