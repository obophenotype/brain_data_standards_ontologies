from template_generation_tools import generate_curated_class_template, generate_ind_template, generate_marker_template
import argparse


parser = argparse.ArgumentParser(description='Process some JSON dendrograms. Without optional args, '
                                             'generates an ind template.')
parser.add_argument('input', help="Path to input JSON file")
parser.add_argument('output', help="Path to output TSV file")
parser.add_argument('-c', action='store_true',
                    help="Generate a class template.")

parser.add_argument('-m', action='store_true',
                    help="Generate a marker template.")

args = parser.parse_args()

if args.c:
    generate_curated_class_template(args.input, args.output)
elif args.m:
    generate_marker_template(args.input, args.output)
else:
    generate_ind_template(args.input, args.output)

