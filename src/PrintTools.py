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

def print_repo(repo):
    if len(repo) > 0:
        if isinstance(repo[0], list):
            print_2d_repo(repo)
        else:
            for node in repo:
                print(node)


def print_2d_repo(repo):
    for entry in repo:
        print([str(node) for node in entry])


def print_line_repo(line_repo, line_start=1):
    for i in range(len(line_repo)):
        print(str(i+line_start) + " " + str([str(node) for node in line_repo[i]]))

def print_dict_of_list(my_dict):
    for key, val in my_dict.items():
        print(key, "=>", [[str(elem) for elem in line] for line in val])

if __name__=="__main__":
    print("Error: This script is part of the OzDoc framework and should not be ran alone. "
          "Please locate and run OzDoc.py")
