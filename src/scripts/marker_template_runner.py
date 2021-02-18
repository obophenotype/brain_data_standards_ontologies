import argparse
from marker_tools import generate_denormalised_marker_template

parser = argparse.ArgumentParser(description='Process some JSON dendrograms. Without optional args, '
                                             'generates an ind template.')
parser.add_argument('json', help="Path to input JSON file")
parser.add_argument('marker', help="Path to input marker file")
parser.add_argument('config', help="Path to input config file")
parser.add_argument('output', help="Path to output TSV file")
args = parser.parse_args()

generate_denormalised_marker_template(args.json, args.marker, args.config, args.output)
