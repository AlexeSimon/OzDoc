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

import re
regex_type = type(re.compile(''))

evalfun = {}


def eval_rule_empty(node, offset, rule_string):
    if rule_string == "":
        return ""


def eval_rule_symbol(node, offset, rule_string):
    if node.code[offset:offset + len(rule_string)] == rule_string:
        return rule_string


def eval_rule_text(node, offset, rule_string):
    if rule_string == "" or (node.code[offset:offset + len(rule_string)] == rule_string
                          and (offset == 0 or not node.code[offset - 1].isalnum())
                          and (offset + len(rule_string) >= node.end or not node.code[offset + len(rule_string)].isalnum())):
        return rule_string


def eval_rule_regex(node, offset, regex):
    if not isinstance(regex, regex_type):
        ans = re.match(regex, node.code[offset:])
    else:
        ans = regex.match(node.code[offset:])
    if ans is not None:
        return ans.group(0)
    else:
        return None


def eval_regex_text(node, offset, regex):
    if not isinstance(regex, regex_type):
        ans = re.match(regex, node.code[offset:])
    else:
        ans = regex.match(node.code[offset:])
    if ans is not None:
        found_string = ans.group(0)
        if not (node.code[offset - 1].isalnum()) and not (node.code[offset + len(found_string)].isalnum()):
            return found_string
        else:
            return None
    else:
        return None


def eval_rule(node, offset, eval_name, rule_string) :
    if eval_name in evalfun:
        return evalfun[eval_name](node, offset, rule_string)


evalfun["empty"] = eval_rule_empty
evalfun["symbol"] = eval_rule_symbol
evalfun["text"] = eval_rule_text
evalfun["regex"] = eval_rule_regex
evalfun["varregex"] = eval_regex_text

if __name__=="__main__":
    print("Error: This script is part of the OzDoc framework and should not be ran alone. Please locate and run OzDoc.py")
