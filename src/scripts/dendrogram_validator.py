import logging
import os
from dendrogram_tools import dend_json_2_nodes_n_edges
from abc import ABC, abstractmethod
from os.path import isfile, join

log = logging.getLogger(__name__)

DENDROGRAM_FOLDER = join(os.path.dirname(os.path.realpath(__file__)), "../dendrograms")


class BaseChecker(ABC):

    @abstractmethod
    def check(self, dend_file, dendrogram):
        pass


class PrefAliasUniquenessChecker(BaseChecker):
    """
    cell_set_preferred_alias should be unique within any one dendrogram - ignoring nodes with no
    cell_set_preferred_alias, no two nodes should have the same one
    """

    def __init__(self):
        self.reports = []

    def check(self, dend_file, dendrogram):
        pref_aliases = list()
        is_valid = True
        for o in dendrogram['nodes']:
            if o['cell_set_preferred_alias']:
                if o['cell_set_preferred_alias'] not in pref_aliases:
                    pref_aliases.append(o['cell_set_preferred_alias'])
                else:
                    is_valid = False
                    log.error("cell_set_preferred_alias '{}' is duplicate in {}"
                              .format(o['cell_set_preferred_alias'], dend_file))
        return is_valid


class ValidationError(Exception):

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


def main():
    log.info("Dendrogram validation started.")
    files = [f for f in os.listdir(DENDROGRAM_FOLDER) if isfile(join(DENDROGRAM_FOLDER, f))]
    is_valid = True
    for file in files:
        filename, file_extension = os.path.splitext(file)
        if file_extension == ".json":
            dend = dend_json_2_nodes_n_edges(join(DENDROGRAM_FOLDER, file))
            is_valid &= PrefAliasUniquenessChecker().check(filename, dend)

    if not is_valid:
        raise ValidationError("Dendrogram validation failed and issues logged.")


if __name__ == '__main__':
    main()
