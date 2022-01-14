import warnings
import json


def dend_json_2_nodes_n_edges(path_to_json):
    f = open(path_to_json, 'r')
    j = json.loads(f.read())
    out = {}
    tree_recurse(j, out)
    f.close()
    return out


def tree_recurse(tree, out, parent_node_id=''):
    """Convert Allen Taxonomy JSON to a list of nodes and edges, where nodes are
    Copies of nodes in Allen JSON & edges are duples - (subject(child), object(parent))
    identified by 'cell_set_accession'.

    Args:
        - Tree: Allen taxonomy in JSON, or some subtree of it
        - Output structure to populate (starting point must be an empty dict)
        - parent_node_id: 'cell_set_accession' of parent.  Default (no parent) = root.

    """
    if not out:
        out['nodes'] = []
        out['edges'] = set()
    if 'node_attributes' in tree.keys():
        if len(tree['node_attributes']) > 1:
            warnings.warn("Don't know how to deal with multiple nodes per recurse")
        ID = tree['node_attributes'][0]['cell_set_accession']

        out['nodes'].append(tree['node_attributes'][0])
        if parent_node_id:
            out['edges'].add((ID, parent_node_id))
        if 'children' in tree.keys():
            for c in tree['children']:
                tree_recurse(c, out, parent_node_id=ID)
        else:
            warnings.warn("non leaf node %s has no children" % ID)
    elif 'leaf_attributes' in tree.keys():
        if len(tree['leaf_attributes']) > 1:
            warnings.warn("Don't know how to deal with multiple nodes per recurse")
        ID = tree['leaf_attributes'][0]['cell_set_accession']
        # Tag leaves
        tree['leaf_attributes'][0]['is_leaf'] = True
        out['nodes'].append(tree['leaf_attributes'][0])
        out['edges'].add((ID, parent_node_id))
        if 'children' in tree.keys():
            warnings.warn('leaf node %s has children!' % ID)
    else:
        warnings.warn("No recognized nodes")
