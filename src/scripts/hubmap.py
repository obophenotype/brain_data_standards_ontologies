import os
import csv
import re
from template_generation_utils import read_csv_to_dict

HUBMAP_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          "../markers/raw/ASCT+B_Tables_Published_v1.0_v1.1 - Brain_v1.1.tsv")
PCL_CCN201912131_TSV = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                    "../patterns/data/default/CCN201912131_class_base.tsv")
HUBMAP_OUTPUT = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "../markers/raw/ASCT+B_Tables_Published_v1.0_v1.1 - Brain_v1.1-PCL.tsv")


def map_to_pcl():
    """
    Maps CT/1 value of the Hubmap table with the prefLabel of Human taxonomy (CCN201912131). Adds a PCL ID column after
    the CT/1 column.
    """
    hubmap_headers, hubmap_data = read_csv_to_dict(HUBMAP_TSV, delimiter="\t", generated_ids=True)
    headers, pcl_by_pref_label = read_csv_to_dict(PCL_CCN201912131_TSV, id_column=1, delimiter="\t")

    with open(HUBMAP_OUTPUT, mode='w') as out:
        writer = csv.writer(out, delimiter="\t", quotechar='"')
        new_headers = hubmap_headers.copy()
        new_headers.insert(22, "PCL_ID")
        writer.writerow(new_headers)

        print(headers)
        for row_index in hubmap_data:
            row_data = hubmap_data[row_index]
            pcl_id = ""
            name_without_parentheses = re.sub(r'\([^)]*\)', '', row_data["CT/1"]).strip()
            pvalb_name = row_data["CT/1"].replace("PVALB", "PVALB-like")
            opalin_name = row_data["CT/1"].replace("OPALIN", "OPALIN-like")
            if row_data["CT/1"]:
                if row_data["CT/1"] in pcl_by_pref_label:
                    pcl_id = pcl_by_pref_label[row_data["CT/1"]]["defined_class"]
                elif name_without_parentheses in pcl_by_pref_label:
                    pcl_id = pcl_by_pref_label[name_without_parentheses]["defined_class"]
                elif pvalb_name in pcl_by_pref_label:
                    pcl_id = pcl_by_pref_label[pvalb_name]["defined_class"]
                elif opalin_name in pcl_by_pref_label:
                    pcl_id = pcl_by_pref_label[opalin_name]["defined_class"]
                elif row_data["CT/1"]:
                    print("Not Found:" + str(row_data["CT/1"]))
            new_row = []
            for header in hubmap_headers:
                new_row.append(row_data[header])
            new_row.insert(22, pcl_id)

            writer.writerow(new_row)


map_to_pcl()
