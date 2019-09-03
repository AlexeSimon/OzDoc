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

DEFAULT_OUT = "generated_doc"
DEFAULT_SETTINGS = "settings/oz_default.py"
DEFAULT_TEMPLATE = "templates/oz_default"
DEFAULT_DOCGEN = "docgens/oz_default.py"
DEFAULT_EXTENSION = "oz"

arg_parser = argparse.ArgumentParser(description='Generates documentation (for Oz code by default).')
group = arg_parser.add_mutually_exclusive_group(required=True)
group.add_argument("file", nargs="?", action="append", help="specify input file")
group.add_argument("-f", "--file", dest='file', action="append", help="specify input file")
group.add_argument("-d", "--dir", action="store", help="specify input directory")
group.add_argument("-t", "--text", action="store", help="specify input text ")
arg_parser.add_argument("-o", "--out", action="store", default=DEFAULT_OUT,
                        help="specify output destination (default: "+DEFAULT_OUT+")")
arg_parser.add_argument("-s", "--settings", action="store", default=sys.argv[0].rstrip("OzDoc.py")+DEFAULT_SETTINGS,
                        help="specify setting file (default: "+DEFAULT_SETTINGS+")")
arg_parser.add_argument("--template", action="store", default=sys.argv[0].rstrip("OzDoc.py")+DEFAULT_TEMPLATE,
                        help="specify documentation template directory (default: "+DEFAULT_TEMPLATE+")")
arg_parser.add_argument("--docgen", action="store", default=sys.argv[0].rstrip("OzDoc.py")+DEFAULT_DOCGEN,
                        help="specify documentation generating code (default: "+DEFAULT_DOCGEN+")")
arg_parser.add_argument("-e", "--extension", action="store", default=DEFAULT_EXTENSION,
                        help="specify files extension in dir mode, without dot (default: "+DEFAULT_EXTENSION+")")


def parse_args(args=None):
    if args is None:
        return arg_parser.parse_args()
    elif isinstance(args, str):
        return arg_parser.parse_args(args.split())
    else:
        return arg_parser.parse_args(args)


if __name__=="__main__":
    print("Error: This script is part of the OzDoc framework and should not be ran alone. "
          "Please locate and run OzDoc.py")
