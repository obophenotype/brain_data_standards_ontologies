import yaml
import json
import logging
from jsonschema import validate

log = logging.getLogger(__name__)


def read_taxonomy_details_yaml():
    """
    TODO: after merge of branch update_issue_31, use this function:
    from template_generation_utils import read_taxonomy_details_yaml
    Returns:

    """
    with open(r'../dendrograms/taxonomy_details.yaml') as file:
        documents = yaml.full_load(file)
    return documents


def read_schema(schema_path):
    """
    Reads a json schema file from the given path.
    Args:
        schema_path: path of the schema

    Returns: schema object

    """
    f = open(schema_path, 'r')
    return json.loads(f.read())


if __name__ == '__main__':
    validate(read_taxonomy_details_yaml(), read_schema("./config_schema.json"))



