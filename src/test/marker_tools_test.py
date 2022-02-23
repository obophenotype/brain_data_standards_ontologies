import unittest
import os
from marker_tools import get_nsforest_confidences
from dendrogram_tools import dend_json_2_nodes_n_edges
from nomenclature_tools import nomenclature_2_nodes_n_edges

current_dir = os.path.dirname(os.path.realpath(__file__))
PATH_MOUSE_NOMENCLATURE = os.path.join(current_dir, "../dendrograms/nomenclature_table_CCN202002013.csv")
PATH_HUMAN_M1_NOMENCLATURE = os.path.join(current_dir, "../dendrograms/nomenclature_table_CCN201912131.csv")
PATH_MARMOSET_M1_NOMENCLATURE = os.path.join(current_dir, "../dendrograms/nomenclature_table_CCN201912132.csv")
PATH_HUMAN_MTG_NOMENCLATURE = os.path.join(current_dir, "../dendrograms/CS1908210.json")
PATH_CENTRALIZED_DATA = os.path.join(current_dir, "./test_data/centralized_data/MOp_taxonomies_ontology/")

class MarkerToolsTest(unittest.TestCase):

    def test_get_nsforest_confidences_mouse(self):
        dend = nomenclature_2_nodes_n_edges(PATH_MOUSE_NOMENCLATURE)
        marker_path = os.path.join(PATH_CENTRALIZED_DATA, "NSForestMarkers/Mouse_MOp_NSForest_Markers.csv")
        confidences = get_nsforest_confidences("CCN202002013", dend, marker_path)

        self.assertEqual("0.988920549", confidences["CS202002013_179"])
        self.assertEqual("0.607476636", confidences["CS202002013_3"])

    def test_get_nsforest_confidences_human_m1(self):
        dend = nomenclature_2_nodes_n_edges(PATH_HUMAN_M1_NOMENCLATURE)
        marker_path = os.path.join(PATH_CENTRALIZED_DATA, "NSForestMarkers/Human_M1_NSForest_Markers.csv")
        confidences = get_nsforest_confidences("CS201912131", dend, marker_path)

        self.assertEqual("0.989133387", confidences["CS201912131_150"])  # Glutamatergic
        self.assertEqual("0.689189189", confidences["CS201912131_69"])  # Inh L5-6 PVALB GAPDHP60
        self.assertEqual("0.825020189", confidences["CS201912131_134"])  # (Mouse L5 IT)-like
        self.assertFalse("CS201912131_145" in confidences)  # (Mouse IT projecting)-like
        self.assertFalse("CS201912131_162" in confidences)  # (Mouse Vip)-like_C4

    def test_get_nsforest_confidences_marmoset_m1(self):
        dend = nomenclature_2_nodes_n_edges(PATH_MARMOSET_M1_NOMENCLATURE)
        marker_path = os.path.join(PATH_CENTRALIZED_DATA, "NSForestMarkers/Marmoset_M1_NSForest_Markers.csv")
        confidences = get_nsforest_confidences("CS201912132", dend, marker_path)

        self.assertEqual("0.428954424", confidences["CS201912132_79"])  # Astro FGFR3 EPHB1
        self.assertEqual("0.759294697", confidences["CS201912132_104"])  # (Mouse L6 CT)-like
        self.assertEqual("0.7227388", confidences["CS201912132_108"])  # Peri
        self.assertEqual("0.790527018", confidences["CS201912132_109"])  # VLMC
        self.assertEqual("0.889261745", confidences["CS201912132_93"])  # VLMC SLC1A3-like SLC47A1
        self.assertFalse("CS201912132_113" in confidences)  # (Mouse Non-IT projecting)-like
        self.assertFalse("CS201912132_135" in confidences)  # All Cells

    def test_get_nsforest_confidences_human_mtg(self):
        dend = dend_json_2_nodes_n_edges(PATH_HUMAN_MTG_NOMENCLATURE)
        marker_path = os.path.join(PATH_CENTRALIZED_DATA, "NSForestMarkers/Human_MTG_NSForest_Markers.csv")
        confidences = get_nsforest_confidences("CS1908210", dend, marker_path)

        self.assertEqual("0.55", confidences["CS1908210011"])  # Inh L1-2 VIP TSPAN12
        self.assertEqual("0.58", confidences["CS1908210059"])  # Exc L4-6 RORB C1R
        self.assertEqual("0.91", confidences["CS1908210075"])  # Micro L1-6 TYROBP
