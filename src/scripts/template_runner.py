from template_generation_tools import generate_base_class_template, generate_curated_class_template, \
    generate_ind_template, merge_class_templates, \
    generate_cross_species_template, generate_taxonomies_template, generate_app_specific_template, \
    generate_obsolete_ind_template, generate_homologous_to_template, generate_datasets_template, \
    generate_marker_gene_set_template, generate_obsolete_taxonomies_template
from marker_tools import generate_denormalised_marker_template
import argparse
import pathlib

parser = argparse.ArgumentParser(description='Cli interface for BDS functions. Provides two interfaces; '
                                             'generator interface to generate templates and '
                                             'modifier interface to update templates. ')
subparsers = parser.add_subparsers(help='Available BDS actions', dest='action')

parser_generator = subparsers.add_parser('generator', description='Process some JSON dendrograms and generates template'
                                                                  ' files. Without optional args, generates an ind '
                                                                  'template.')
parser_generator.add_argument('-i', '--input', help="Path to input JSON file")
parser_generator.add_argument('-i2', '--input2', help="Path to second input file")
parser_generator.add_argument('-o', '--output', help="Path to output TSV file")
parser_generator.add_argument('-b', '--base', help="List of all class base TSV files")
parser_generator.add_argument('-cb', action='store_true', help="Generate a class base template.")
parser_generator.add_argument('-cc', action='store_true', help="Generate a class curation template.")
parser_generator.add_argument('-ch', action='store_true', help="Generate a class homologous to relation template.")
parser_generator.add_argument('-md', action='store_true', help="Generate a denormalized marker template.")
parser_generator.add_argument('-cs', action='store_true', help="Generate a cross species alignment template.")
parser_generator.add_argument('-a', action='store_true', help="Generate a app specific data template.")
parser_generator.add_argument('-ds', action='store_true', help="Generate a datasets template.")
parser_generator.add_argument('-tx', action='store_true', help="Generate a taxonomies template.")
parser_generator.add_argument('-ms', action='store_true', help="Generate a marker gene set template.")
parser_generator.add_argument('-oi', action='store_true', help="Generate a obsolete individuals data template.")
parser_generator.add_argument('-ot', action='store_true', help="Generate a obsolete taxonomies template.")

parser_modifier = subparsers.add_parser('modifier', description='Template modification interface')
parser_modifier.add_argument('-i', '--input', action='store', type=pathlib.Path, help="Path to first input file")
parser_modifier.add_argument('-i2', '--input2', action='store', type=pathlib.Path, help="Path to second input file")
parser_modifier.add_argument('-o', '--output', action='store', type=pathlib.Path, help="Path to output file")
parser_modifier.add_argument('-m', '--merge', action='store_true')

args = parser.parse_args()

if args.action == "modifier":
    if 'merge' in args and args.merge:
        merge_class_templates(args.input, args.input2, args.output)
else:
    if args.cb:
        generate_base_class_template(args.input, args.output)
    elif args.cc:
        generate_curated_class_template(args.input, args.output)
    elif args.ch:
        all_base_files = [x.strip() for x in args.base.split(' ') if x.strip()]
        generate_homologous_to_template(args.input, all_base_files, args.output)
    elif args.md:
        generate_denormalised_marker_template(args.input, args.output)
    elif args.cs:
        generate_cross_species_template(args.input, args.output)
    elif args.a:
        generate_app_specific_template(args.input, args.output)
    elif args.ds:
        generate_datasets_template(args.input, args.output)
    elif args.tx:
        generate_taxonomies_template(args.input, args.output)
    elif args.ms:
        generate_marker_gene_set_template(args.input, args.input2, args.output)
    elif args.oi:
        generate_obsolete_ind_template(args.input, args.input2, args.output)
    elif args.ot:
        generate_obsolete_taxonomies_template(args.input, args.output)
    else:
        generate_ind_template(args.input, args.input2, args.output)
