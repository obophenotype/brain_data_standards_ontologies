from template_generation_tools import generate_curated_class_template
from template_generation_tools import generate_ind_template
import argparse


parser = argparse.ArgumentParser(description='Process some JSON dendrograms.')
parser.add_argument('input', help="Path to input JSON file")
parser.add_argument('output', help="Path to output TSV file")
parser.add_argument('--class-template', '-c', optional=True, action='store_true',
                    help="Generate a class template, if not present and individual"
                         " template is generated")
args = parser.parse_args()

if not args.class_tempalte:
    generate_ind_template(args.input, args.output)
else:
    generate_curated_class_template(args.input, args.output)
