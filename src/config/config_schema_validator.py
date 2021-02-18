import yaml
import json
import logging
import os
from jsonschema import validate, ValidationError

log = logging.getLogger(__name__)


def read_taxonomy_details_yaml(config_path):
    absolute_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_path)
    with open(absolute_path, 'r') as file:
        documents = yaml.full_load(file)
    return documents


def read_schema(schema_path):
    """
    Reads a json schema file from the given path.
    Args:
        schema_path: path of the schema

    Returns: schema object

    """
    absolute_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), schema_path)
    f = open(absolute_path, 'r')
    return json.loads(f.read())


if __name__ == '__main__':
    try:
        log.info("Config schema validation started.")
        validate(read_taxonomy_details_yaml('../dendrograms/taxonomy_details.yaml'),
                 read_schema("./config_schema.json"))
        log.info("Config schema validation successful.")
    except ValidationError as e:
        log.error("Config schema validation failed: " + e.message)
        raise ValueError("Configuration schema validation failed: " + e.message)




