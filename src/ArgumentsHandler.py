"""
This script is part of The OzDoc Framework, written for the thesis :
"OzDoc , Development and implementation of a highly automated documentation generator for the Oz programming language"

Authors : ALEXE Simon and FRENYO Péter
Supervisor : VAN ROY Peter
School : Université Catholique de Louvain
Year : 2018-2019
Git : https://github.com/AlexeSimon/OzDoc
Version : 1.0
License: GNU GPL

"""

import argparse
import sys

arg_parser = argparse.ArgumentParser(description='Generates documentation (for Oz code by default).')
group = arg_parser.add_mutually_exclusive_group(required=True)
group.add_argument("file", nargs="?", action="append", help="specify input file")
group.add_argument("-f", "--file", dest='file', action="append", help="specify input file")
group.add_argument("-d", "--dir", action="store", help="specify input directory")
group.add_argument("-t", "--text", action="store", help="specify input text ")
arg_parser.add_argument("-o", "--out", action="store", default="generated_doc",
                        help="specify output destination (default: generated_doc")
arg_parser.add_argument("-s", "--settings", action="store", default=sys.argv[0].rstrip("OzDoc.py")+"settings/oz_default.py",
                        help="specify setting file (default: settings/oz_default.py)")
arg_parser.add_argument("--template", action="store", default=sys.argv[0].rstrip("OzDoc.py")+"templates/oz_default",
                        help="specify documentation template directory (default: templates/oz_default")
arg_parser.add_argument("--docgen", action="store", default=sys.argv[0].rstrip("OzDoc.py")+"docgens/oz_default.py",
                        help="specify documentation generating code (default: docgens/oz_default.py")


def parse_args(args=None):
    if args is None:
        return arg_parser.parse_args()
    elif isinstance(args, str):
        return arg_parser.parse_args(args.split())
    else:
        return arg_parser.parse_args(args)

if __name__=="__main__":
    print("Error: This script is part of the OzDoc framework and should not be ran alone. Please locate and run OzDoc.py")
