"""
Responsible with allocating stable PCL IDs for taxonomy nodes. Id ranges for taxonomies are allocated based on
taxonomies order in the 'taxonomy_details.yaml' configuration file. Automatic ID range allocation starts from
#ID_RANGE_BASE and allocates 400 IDs for classes and 600 IDs for individuals

ID range allocation logic is as follows

    - 0010000 to 0010999  custom classes and properties (manually managed)
    - 0011000 taxonomy1 individual # idle: now individuals use accession_id
    - 0011001 to 0011499 taxonomy1 classes (500)
    - 0011500 to 0012450 taxonomy1 individuals (950) # idle: now individuals use accession_id
    - 0012451 to 0012500 taxonomy1 datasets (50)
    - 0012501 to 0012999 taxonomy1 marker gene sets (500)
    - 0013000 to 0014999 taxonomy1 spare id space (2000)
    -
    - 0015000 taxonomy2 individual # idle: now individuals use accession_id
    - 0015001 to 0015499 taxonomy2 classes
    - 0015500 to 0016450 taxonomy2 individuals # idle: now individuals use accession_id
    - 0016451 to 0016500 taxonomy2 datasets
    - 0016501 to 0016999 taxonomy2 marker gene sets
    - 0017000 to 0018999 taxonomy2 spare id space
    - ...

"""

import yaml
import os


TAXONOMY_DETAILS_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     '../dendrograms/taxonomy_details.yaml')

# Allocate IDs starting from PCL_0011000
ID_RANGE_BASE = 11000
TAXONOMY_ID_RANGE = 4000
INDV_ID_DISPLACEMENT = 500
DATASET_ID_DISPLACEMENT = 1451
MARKER_SET_ID_DISPLACEMENT = 1500


def read_taxonomy_details_yaml():
    with open(r'%s' % TAXONOMY_DETAILS_YAML) as file:
        documents = yaml.full_load(file)
    return documents


taxonomies = read_taxonomy_details_yaml()
taxonomy_ids = [taxon["Taxonomy_id"] for taxon in taxonomies]


def get_class_id(accession_id):
    """
    Generates a PCL id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
    in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a PCL id displaced by the
    node_id.
    Args:
        accession_id: cell set accession id

    Returns: seven digit PCL id as string
    """
    node_id, taxonomy_index = parse_accession_id(accession_id)
    pcl_id = ID_RANGE_BASE + (TAXONOMY_ID_RANGE * taxonomy_index) + node_id

    return str(pcl_id).zfill(7)


def get_individual_id(accession_id):
    """
    DEPRECATED: now individuals use accession_id

    Generates a PCL id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
    in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a PCL id displaced by the
    node_id in the individual range (taxonomy range + 500).
    Args:
        accession_id: cell set accession id

    Returns: seven digit PCL id as string
    """
    node_id, taxonomy_index = parse_accession_id(accession_id)
    pcl_id = ID_RANGE_BASE + (TAXONOMY_ID_RANGE * taxonomy_index) + INDV_ID_DISPLACEMENT + node_id

    return str(pcl_id).zfill(7)


def get_taxonomy_id(taxonomy_id):
    """
    DEPRECATED: now individuals use accession_id

    Generates a PCL id for the given taxonomy. it is the first id of the taxonomy allocated id range (such as 0012000)
    Args:
        taxonomy_id: taxonomy id

    Returns: seven digit PCL id as string
    """
    taxonomy_index = get_taxonomy_index(taxonomy_id)
    pcl_id = ID_RANGE_BASE + (TAXONOMY_ID_RANGE * taxonomy_index)

    return str(pcl_id).zfill(7)


def get_dataset_id(taxonomy_id, dataset_index):
    """
    Generates a PCL id for the given dataset. Dataset id range is last 50 ids of the taxonomy id range.
    Args:
        taxonomy_id: taxonomy id
        dataset_index: index of the dataset (0 to 48)

    Returns: seven digit PCL id as string
    """
    taxonomy_index = get_taxonomy_index(taxonomy_id)
    pcl_id = ID_RANGE_BASE + (TAXONOMY_ID_RANGE * taxonomy_index) + DATASET_ID_DISPLACEMENT + dataset_index

    return str(pcl_id).zfill(7)


def get_marker_gene_set_id(accession_id):
    """
    Generates a PCL id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
    in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a PCL id displaced by the
    node_id in the marker gene set range (taxonomy range + 400).
    Args:
        accession_id: cell set accession id

    Returns: seven digit PCL id as string
    """
    node_id, taxonomy_index = parse_accession_id(accession_id)
    pcl_id = ID_RANGE_BASE + (TAXONOMY_ID_RANGE * taxonomy_index) + MARKER_SET_ID_DISPLACEMENT + node_id

    return str(pcl_id).zfill(7)


def parse_accession_id(accession_id):
    """
    Parses taxonomy id and node id from the accession id and returns taxonomy index and the node id.
    Args:
        accession_id: cell set accession id

    Returns: tuple of node_id and taxonomy's index in the 'taxonomy_details.yaml' config file.
    """
    if "_" in accession_id:
        accession_parts = str(accession_id).split("_")
        node_id = int(accession_parts[1].strip())
        taxonomy_id = accession_parts[0]
        taxonomy_index = get_taxonomy_index(taxonomy_id)
    else:
        # assume last 3 is node id
        node_id = int(accession_id[len(accession_id)-3:])
        taxonomy_id = accession_id[:len(accession_id)-3]
        taxonomy_index = get_taxonomy_index(taxonomy_id)

    return node_id, taxonomy_index


def get_taxonomy_index(taxonomy_id):
    if taxonomy_id in taxonomy_ids:
        taxonomy_index = taxonomy_ids.index(taxonomy_id)
    elif taxonomy_id.replace("CS", "CCN") in taxonomy_ids:
        taxonomy_index = taxonomy_ids.index(taxonomy_id.replace("CS", "CCN"))
    else:
        raise ValueError("Cannot find '{}' in the taxonomy config.".format(taxonomy_id))
    return taxonomy_index


def get_reverse_id(pcl_id_str):
    """
    Converts PCL id to cell cet accession id
    Args:
        pcl_id_str: PCL id
    Returns: cell cet accession id
    """
    if str(pcl_id_str).startswith("http://purl.obolibrary.org/obo/pcl/") or str(pcl_id_str).startswith("PCL_INDV:"):
        pcl_id_str = str(pcl_id_str).replace("http://purl.obolibrary.org/obo/pcl/", "")
        pcl_id_str = str(pcl_id_str).replace("PCL_INDV:", "")
        return pcl_id_str

    pcl_id_str = str(pcl_id_str).replace("http://purl.obolibrary.org/obo/PCL_", "")
    pcl_id_str = str(pcl_id_str).replace("PCL:", "")
    pcl_id_str = str(pcl_id_str).replace("PCL_", "")

    pcl_id = int(pcl_id_str)

    taxonomy_index = int((pcl_id - ID_RANGE_BASE) / TAXONOMY_ID_RANGE)
    taxonomy_id = taxonomy_ids[taxonomy_index].replace("CCN", "CS")

    node_id = (pcl_id - ID_RANGE_BASE) - (TAXONOMY_ID_RANGE * taxonomy_index)
    if node_id > INDV_ID_DISPLACEMENT:
        node_id = node_id - INDV_ID_DISPLACEMENT

    if taxonomy_id == "CS1908210":
        accession_id = taxonomy_id + str(node_id).zfill(3)
    else:
        accession_id = taxonomy_id + "_" + str(node_id)

    return accession_id


def is_pcl_id(id_str):
    """
    Returns 'True' if given id is PCL id.
    Args:
        id_str: ID string to check
    Returns: 'True' if given id is PCL id, 'False' otherwise
    """
    return str(id_str).startswith("http://purl.obolibrary.org/obo/PCL_") \
        or str(id_str).startswith("PCL:") or str(id_str).startswith("PCL_") \
        or str(id_str).startswith("http://purl.obolibrary.org/obo/pcl/") \
        or str(id_str).startswith("PCL_INDV:")
