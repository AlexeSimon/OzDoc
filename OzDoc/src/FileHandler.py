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
import shutil
import importlib
import importlib.util


def file_to_string(file_name):
    with open(file_name, 'r') as file:
        file_content = file.read()
    if not file_content:
        print("Error : file "+file_name+" is empty")
        return ""
    else:
        return file_content


def string_to_file(string, file_name):
    with open(file_name, 'w') as file:
        file.write(string)


def append_string_to_file(string, file_name):
    with open(file_name, 'a') as file:
        file.write(string)


def replace_in_file(old_string, new_string, file_name, replace_all=False):
    with open(file_name, 'r+') as file:
        file_content = file.read()
        # Short .html file, so we can use string and replace function
        if replace_all:
            new_content = file_content.replace(old_string, new_string)
        else:
            new_content = file_content.replace(old_string, new_string, 1)  # Only replace the first occurrence
        file.seek(0)
        file.write(new_content)
        file.truncate()


def copy_file(src, dest):
    shutil.copy(src, dest)

# Curtesy of mgrant at https://stackoverflow.com/a/15824216
def copy_directory(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                copy_directory(os.path.join(src, f), os.path.join(dest, f), ignore)
    else:
        shutil.copyfile(src, dest)


def import_module(given_name, path):
    spec = importlib.util.spec_from_file_location(given_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_directory_tree(src):
    pass

if __name__=="__main__":
    print("Error: This script is part of the OzDoc framework and should not be ran alone. Please locate and run OzDoc.py")

