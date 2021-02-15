import unittest
import networkx as nx
import os
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from scripts.marker_tools import generate_nested_marker, read_dendrogram_tree, read_marker_file, extend_expressions


PATH_DEND_JSON = "./test_data/CCN202002013.json"

PATH_MARKERS = "./test_data/CS202002013_markers.tsv"

PATH_OUTPUT_MARKER = "./test_data/CS202002013_markers_nested.tsv"

EXPRESSIONS = "expressions"


def delete_file(path_to_file):
    if os.path.exists(path_to_file):
        os.remove(path_to_file)


def visualise_tree():
    tree = read_dendrogram_tree(PATH_DEND_JSON)

    labels = {}
    for node in tree.nodes():
        labels[node] = str(node).replace("CS202002013", "")

    plt.title('CCN202002013')
    pos = graphviz_layout(tree, prog='dot')
    nx.draw(tree, pos, with_labels=False, arrows=False)
    nx.draw_networkx_labels(tree, pos, labels, font_size=7)

    plt.show()


class NestedMarkerTest(unittest.TestCase):

    def test_tree_descendants(self):
        tree = read_dendrogram_tree(PATH_DEND_JSON)
        descendants = nx.descendants(tree, "CS202002013_183")

        print(descendants)
        self.assertEqual(4, len(descendants))
        # direct leaf
        self.assertTrue("CS202002013_60" in descendants)
        # direct child
        self.assertTrue("CS202002013_184" in descendants)
        # child of 184
        self.assertTrue("CS202002013_58" in descendants)
        self.assertTrue("CS202002013_59" in descendants)

    def test_marker_enrichment(self):
        tree = read_dendrogram_tree(PATH_DEND_JSON)
        marker_expressions = read_marker_file(PATH_MARKERS)
        marker_extended_expressions = extend_expressions(tree, marker_expressions)

        # assert same IDs
        self.assertEqual(marker_expressions.keys(), marker_extended_expressions.keys())

        self.assertTrue("CS202002013_183" in marker_extended_expressions.keys())
        expressions = marker_extended_expressions["CS202002013_183"][EXPRESSIONS]

        # self expressions
        self.assertTrue("ensembl:ENSMUSG00000028222" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000021708" in expressions)
        # enriched from _60
        self.assertTrue("ensembl:ENSMUSG00000042589" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000056427" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000031216" in expressions)
        # none from _184
        # enriched from _58
        self.assertTrue("ensembl:ENSMUSG00000098097" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000036545" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000009376" in expressions)
        # enriched from _59
        self.assertTrue("ensembl:ENSMUSG00000026676" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000029705" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000027210" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000062372" in expressions)

        self.assertEqual(12, len(expressions))

    def test_subtree_restrictions(self):
        tree = read_dendrogram_tree(PATH_DEND_JSON)
        marker_expressions = read_marker_file(PATH_MARKERS)
        marker_extended_expressions = extend_expressions(tree, marker_expressions, ["CS202002013_184"])

        # assert same IDs
        self.assertEqual(marker_expressions.keys(), marker_extended_expressions.keys())

        self.assertTrue("CS202002013_183" in marker_extended_expressions.keys())
        expressions = marker_extended_expressions["CS202002013_183"][EXPRESSIONS]

        # self expressions
        self.assertTrue("ensembl:ENSMUSG00000028222" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000021708" in expressions)

        self.assertEqual(2, len(expressions))

    def test_subtree_restrictions2(self):
        tree = read_dendrogram_tree(PATH_DEND_JSON)
        marker_expressions = read_marker_file(PATH_MARKERS)
        marker_extended_expressions = extend_expressions(tree, marker_expressions, ["CS202002013_183"])

        # assert same IDs
        self.assertEqual(marker_expressions.keys(), marker_extended_expressions.keys())

        self.assertTrue("CS202002013_183" in marker_extended_expressions.keys())
        expressions = marker_extended_expressions["CS202002013_183"][EXPRESSIONS]

        # self expressions
        self.assertTrue("ensembl:ENSMUSG00000028222" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000021708" in expressions)
        # enriched from _60
        self.assertTrue("ensembl:ENSMUSG00000042589" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000056427" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000031216" in expressions)
        # none from _184
        # enriched from _58
        self.assertTrue("ensembl:ENSMUSG00000098097" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000036545" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000009376" in expressions)
        # enriched from _59
        self.assertTrue("ensembl:ENSMUSG00000026676" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000029705" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000027210" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000062372" in expressions)

        self.assertEqual(12, len(expressions))

    def test_subtree_restrictions3(self):
        tree = read_dendrogram_tree(PATH_DEND_JSON)
        marker_expressions = read_marker_file(PATH_MARKERS)
        marker_extended_expressions = extend_expressions(tree, marker_expressions,
                                                         ["CS202002013_182", "CS202002013_184"])

        # assert same IDs
        self.assertEqual(marker_expressions.keys(), marker_extended_expressions.keys())

        # 183 is child of 182
        self.assertTrue("CS202002013_183" in marker_extended_expressions.keys())
        expressions = marker_extended_expressions["CS202002013_183"][EXPRESSIONS]

        # self expressions
        self.assertTrue("ensembl:ENSMUSG00000028222" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000021708" in expressions)
        # enriched from _60
        self.assertTrue("ensembl:ENSMUSG00000042589" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000056427" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000031216" in expressions)
        # none from _184
        # enriched from _58
        self.assertTrue("ensembl:ENSMUSG00000098097" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000036545" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000009376" in expressions)
        # enriched from _59
        self.assertTrue("ensembl:ENSMUSG00000026676" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000029705" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000027210" in expressions)
        self.assertTrue("ensembl:ENSMUSG00000062372" in expressions)

        self.assertEqual(12, len(expressions))

    def test_subtree_restrictions_sequential(self):
        tree = read_dendrogram_tree(PATH_DEND_JSON)
        marker_expressions = read_marker_file(PATH_MARKERS)

        marker_extended_expressions = extend_expressions(tree, marker_expressions, ["CS202002013_184"])
        expressions = marker_extended_expressions["CS202002013_183"][EXPRESSIONS]
        self.assertEqual(2, len(expressions))

        marker_extended_expressions = extend_expressions(tree, marker_expressions)
        expressions = marker_extended_expressions["CS202002013_183"][EXPRESSIONS]
        self.assertEqual(12, len(expressions))

    def test_marker_generation(self):
        delete_file(PATH_OUTPUT_MARKER)

        generate_nested_marker(PATH_DEND_JSON, PATH_MARKERS, PATH_OUTPUT_MARKER)
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
