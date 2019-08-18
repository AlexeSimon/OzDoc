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

# Parser context rules. Can use regex
priority_context_rules = [
                ["comment_line", "symbol", '%', "symbol", '\n'],
                ["comment_block", "symbol", "/*", "symbol", "*/"],
                ["string1", "symbol", "\'", "symbol", "\'"],
                ["string2", "symbol", '\"', "symbol", '\"'],
                ["var2", "symbol", "`", "symbol", "`"]]

context_rules = [
                ["{", "symbol", "{", "symbol", "}"],
                ["[]", "symbol", "[]", "empty", ""],
                ["var", "regex", "[A-Z][A-Za-z0-9]*", "empty", ""],
                ["atom", "text", "atom", "regex", "[a-z]*\(", "\)"],
                #[":", "regex", "[a-z0-9]*:[ ]*", "regex", "(?![a-zA-Z0-9 ])"],
                ["functor", "text", "functor", "text", "end"],
                ["fun", "text", "fun", "text", "end"],
                ["local", "text", "local", "text", "end"],
                ["case", "text", "case", "text",  "end"],
                ["try", "text", "try", "text",  "end"],
                ["if", "text", "if", "text",  "end"],
                ["for", "text", "for", "text",  "end"],
                ["raise", "text", "raise", "text",  "end"],
                ["thread", "text", "thread", "text",  "end"],
                ["lock", "text", "lock", "text",  "end"],
                ["proc", "text", "proc", "text",  "end"],
                ["meth", "text", "meth", "text",  "end"],
                ["class", "text", "class", "text", "end"],
                ["in", "text", "in", "empty", ""],
                ["then", "text", "then", "empty", ""],
                ["else", "text", "else", "empty", ""],
                ["elseif", "text", "elseif", "empty", ""],
                ["of", "text", "of", "empty", ""],
                ["catch", "text", "catch", "empty", ""],
                ["finally", "text", "finally", "empty", ""],
                ["define", "text", "define", "empty", ""],
                ["declare", "text", "declare", "empty", ""],
                ["import", "text", "import", "empty", ""],
                ["andthen", "text", "andthen", "empty", ""]]

# Some context keywords

comment_keyword = ["comment_line", 'comment_block']
inline_comment_keyword = ["comment_line"]
fun_keyword = ["fun", "proc", "meth"]
def_keyword = ["{"]
class_keyword = ["class"]

# Regex

ozdoc_tag_regex = "@([a-z])*"
fun_regex = "([A-Z][A-Za-z0-9]*)|(`.*`)|(\$)"
variable_regex = "([A-Z][A-Za-z0-9]*)|(`.*`)"

# Exception
variable_exception = ["/*", "%", "\'", "\""]

if __name__=="__main__":
    print("Error: This script is part of the OzDoc framework and should not be ran alone. Please locate and run OzDoc.py")
