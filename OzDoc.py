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

import os
import errno
from src.OzDocParser import OzDocParser
from src.ArgumentsHandler import parse_args
from src import FileHandler


if __name__ == '__main__':

    # Recover program arguments (file, dir, text, out, settings, template, docgen)
    args = parse_args()
    try:
        os.makedirs(args.out)
    except FileExistsError:
        if not os.access(args.out, os.W_OK):
            raise IOError(errno.EIO, "Error writing out folder", args.out)

    # Check program mode
    settings = FileHandler.import_module("settings", args.settings)
    if args.file[0] is not None:  # file mode
        parser = OzDocParser(context_type="file", description=args.file[0],
                             priority_context_rules=settings.priority_context_rules,
                             context_rules=settings.context_rules)

    elif args.dir is not None:  # directory mode
        parser = OzDocParser(context_type="dir", description=args.dir,
                             priority_context_rules=settings.priority_context_rules,
                             context_rules=settings.context_rules)

    else:  # text mode
        parser = OzDocParser(args.text, context_type="text",
                             priority_context_rules=settings.priority_context_rules,
                             context_rules=settings.context_rules)

    FileHandler.copy_directory(args.template, args.out)
    docgen = FileHandler.import_module("docgen", args.docgen)
    docgen.run(parser, settings, args.out)
    # Exit successfully
