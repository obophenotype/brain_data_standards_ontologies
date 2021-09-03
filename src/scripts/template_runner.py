from template_generation_tools import generate_curated_class_template, generate_ind_template, \
    generate_equivalent_class_reification_template, generate_equivalent_class_marker_template, \
    generate_minimal_marker_template, generate_non_taxonomy_classification_template
from marker_tools import generate_denormalised_marker_template
import argparse


parser = argparse.ArgumentParser(description='Process some JSON dendrograms. Without optional args, '
                                             'generates an ind template.')
parser.add_argument('input', help="Path to input JSON file")
parser.add_argument('output', help="Path to output TSV file")
parser.add_argument('-c', action='store_true',
                    help="Generate a class template.")

parser.add_argument('-md', action='store_true',
                    help="Generate a denormalized marker template.")
parser.add_argument('-mm', action='store_true',
                    help="Generate a minimal marker template.")

parser.add_argument('-er', action='store_true',
                    help="Generate a equivalent_class template with reification.")
parser.add_argument('-em', action='store_true',
                    help="Generate a equivalent_class template with marker.")
parser.add_argument('-n', action='store_true',
                    help="Generate a nomenclature table template.")

args = parser.parse_args()

if args.c:
    generate_curated_class_template(args.input, args.output)
elif args.md:
    generate_denormalised_marker_template(args.input, args.output)
elif args.mm:
    generate_minimal_marker_template(args.input, args.output)
elif args.er:
    generate_equivalent_class_reification_template(args.input, args.output)
elif args.em:
    generate_equivalent_class_marker_template(args.input, args.output)
elif args.n:
    generate_non_taxonomy_classification_template(args.input, args.output)
else:
    generate_ind_template(args.input, args.output)

