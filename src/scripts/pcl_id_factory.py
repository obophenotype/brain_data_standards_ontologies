"""
Responsible with allocating stable PCL IDs for taxonomy nodes. Id ranges for taxonomies are allocated based on
taxonomies order in the 'taxonomy_details.yaml' configuration file. Automatic ID range allocation starts from
#ID_RANGE_BASE and allocates 400 IDs for classes and 600 IDs for individuals

ID range allocation logic is as follows

    - 0010000 to 0010999  custom classes and properties (manually managed)
    - 0011000 to 0011399 taxonomy1 classes
    - 0011400 to 0011999 taxonomy1 individuals
    - 0012000 to 0012399 taxonomy2 classes
    - 0012400 to 0012999 taxonomy2 individuals
    - ...

"""

from template_generation_utils import read_taxonomy_details_yaml

# Allocate IDs starting from PCL_0010000
ID_RANGE_BASE = 11000

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

    pcl_id = ID_RANGE_BASE + (1000 * taxonomy_index) + node_id
    return str(pcl_id).zfill(7)


def get_individual_id(accession_id):
    """
    Generates a PCL id for the given accession id. Parses taxonomy id from accession id and based on taxonomy's order
    in the 'taxonomy_details.yaml' finds the allocated id range for the taxonomy. Generates a PCL id displaced by the
    node_id in the individual range (taxonomy range + 400).
    Args:
        accession_id: cell set accession id

    Returns: seven digit PCL id as string
    """
    node_id, taxonomy_index = parse_accession_id(accession_id)

    pcl_id = ID_RANGE_BASE + (1000 * taxonomy_index) + 400 + node_id
    return str(pcl_id).zfill(7)


def get_taxonomy_id(taxonomy_id):
    """
    Generates a PCL id for the given taxonomy. it is the first id of the taxonomy allocated id range (such as 0012000)
    Args:
        taxonomy_id: taxonomy id

    Returns: seven digit PCL id as string
    """
    taxonomy_index = get_taxonomy_index(taxonomy_id)

    pcl_id = ID_RANGE_BASE + (1000 * taxonomy_index)
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
