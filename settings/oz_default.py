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

oz_block_keywords = ["case", "choice", "class", "for", "functor", "fun", "if", "local", "lock", "meth",
                     "proc", "raise", "thread", "try"]
oz_simple_keywords = ["andthen", "attr", "at", "break", "catch", "declare", "define", "else", "elseif",
                      "finally", "from", "import", "in", "of", "then"]
#oz_html = [" > ", " < ", "&"]


def oz_block_keyword(keyword):
    return [keyword, "text", keyword, "text", "end"]


def oz_simple_keyword(keyword):
    return [keyword, "text", keyword, "empty", ""]


def oz_generate_context_rules(keywords, f):
    return [f(keyword) for keyword in keywords]

# Parser context rules. Can use regex
priority_context_rules = [
                ["comment_line", "symbol", '%', "symbol", '\n'],
                ["comment_block", "symbol", "/*", "symbol", "*/"],
                ["string1", "symbol", "\'", "symbol", "\'"],
                ["string2", "symbol", '\"', "symbol", '\"'],
                ["var2", "symbol", "`", "symbol", "`"]]

context_rules = [
                ["&", "regex", re.compile("&."), "empty", ""],
                ["{", "symbol", "{", "symbol", "}"],
                ["[]", "symbol", "[]", "empty", ""],
                ["var", "varregex", re.compile(r"[A-Z][A-Za-z0-9_]*"), "empty", ""]
                ] \
                + oz_generate_context_rules(oz_block_keywords, oz_block_keyword)\
                + oz_generate_context_rules(oz_simple_keywords, oz_simple_keyword)\
                + [["atom", "regex", re.compile(r"[a-z][A-Za-z0-9_]*"), "empty", ""]]
                #+ oz_generate_context_rules(oz_html, oz_simple_keyword)\

                #["atom", "text", "atom", "regex", "[a-z]*\(", "\)"],
                #[":", "regex", "[a-z0-9]*:[ ]*", "regex", "(?![a-zA-Z0-9 ])"],

# Some context keywords

comment_keyword = ["comment_line", 'comment_block']
string_keyword = ["string1", "string2"]
inline_comment_keyword = ["comment_line"]
fun_keyword = ["fun", "proc"]
meth_keyword = ["meth"]
def_keyword = ["{"]#, "[a-z][A-Za-z0-9]*"]
class_keyword = ["class"]

# Regex

atom_regex = "([a-z][A-Za-z0-9_]*)|('.*')"   # "Except no keywords" can be resolved with lookaheads like in meth_regex, but is treated via prorities in the case of the main rules
variable_regex = "([A-Z][A-Za-z0-9_]*)|(`.*`)"
ozdoc_tag_regex = "@([a-z])*"
declarations_name_regex = variable_regex + "|(\$)"
meth_regex = "(?<=\W)(?!" + \
             "|".join(list(map(lambda x: "(?<=\s)"+x+"(?=\s)", oz_block_keywords+oz_simple_keywords))) + \
             ")([a-z][A-Za-z0-9_]*)|('.*')|(!?[A-Z][A-Za-z0-9_]*)|(!?`.*`)"

# Exception
variable_exception = ["/*", "%", "\'", "\""]

if __name__ == "__main__":
    print("Error: This script is part of the OzDoc framework and should not be ran alone. "
          "Please locate and run OzDoc.py")
