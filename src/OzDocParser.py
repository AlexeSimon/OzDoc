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

from src.ParserNode import *
import re
from src import FileHandler, StringTools, ListTools
import os
from src.ParseEval import eval_rule

regex_type = type(re.compile(''))


def fuse_similar_successive_contexts(node, context_type):
    # example : comments contexts on the same line or on consecutive lines should be fused into blocks
    # how to find them? They are at the same level (same parent) and end of one is start of other and
    # they differ by at most a line
    prev = None
    to_remove = []
    for child_node in node.iter_children():
        if child_node.context_type in context_type:
            if prev is not None and prev.context_type == child_node.context_type \
                    and (prev.line_end == child_node.line_start or prev.line_end + 1 == child_node.line_start) \
                    and prev.parent == child_node.parent:
                prev.end = child_node.end  # sync end
                prev.line_end = child_node.line_end  # sync line end
                to_remove.append(child_node)  # we will remove child from parent after iteration
            else:
                prev = child_node
        else:
            prev = None
    for child in to_remove:
        child.parent.children.remove(child)


def remove_nodes_type(node, context_type, del_after=True):
    to_remove = []
    for child in node.iter_children():
        if child.context_type in context_type or child.parent in to_remove:
            to_remove.append(child)
    for child in to_remove:
        child.parent.children.remove(child)

    if del_after:
        for child in to_remove:
            del child


def build_context_repo(node, context, repo=None):
    return build_context_repo_not_in(node, context, [], repo=None)


def build_context_repo_not_in(node, context, repo2, repo=None):
    if repo is None:
        repo = []
    for child_node in node.iter_children():
        if child_node.context_type in context and child_node not in repo and child_node not in repo2:
                repo.append(child_node)
    return repo


def build_line_repo(node):
    line_repo = [[] for i in range(node.line_end)]
    line_offset = node.line_start
    for child_node in node.iter_children():
        if child_node not in line_repo[child_node.line_start-line_offset]:
            line_repo[child_node.line_start-line_offset].append(child_node)
        if child_node not in line_repo[child_node.line_end - line_offset]:
            line_repo[child_node.line_end - line_offset].append(child_node)
    return line_repo


# append to repo [node1, node2], node1 not in repo, node1 is in context1, node2 in context2 and
# node2 is the first node in context2 to appear after node1. Ignores node depth
def build_link_context_with_repo(node, context1, context2, repo=None):
    if repo is None:
        repo = []
    prev = None
    for child_node in node.iter_children():
        if prev is None:
            if child_node.context_type in context1 and child_node not in ListTools.get_list_column(repo, 0):
                prev = child_node
        else:
            if child_node.context_type in context2:
                repo.append([prev, child_node])
                prev = None
    return repo


def link_following_regex_to_repo(node, repo, regex, exception=None):
    if not isinstance(regex, regex_type):
        p = re.compile(regex)
    else:
        p = regex
    is_multi_d = isinstance(repo[0], list) if repo else False
    for i in range(len(repo)):
        if is_multi_d:  # if it is a list, we use the last column
            context = repo[i][-1]
        else:
            context = repo[i]
        ans = None
        for m in p.finditer(node.code[context.start:context.end]):
            if exception is None or context.lowest_context_for_char(m.start()+context.start).context_type not in exception:
                ans = m.group()
                break
        if is_multi_d:  # if it is a list, use the last column
            repo[i].append(ans)
        else:
            repo[i] = [context, ans]


def link_all_regex_to_repo(node, repo, regex, exception=None):
    if not isinstance(regex, regex_type):
        p = re.compile(regex)
    else:
        p = regex
    is_multi_d = isinstance(repo[0], list) if repo else False
    for i in range(len(repo)):
        if is_multi_d:  # if it is a list, we use the last column
            context = repo[i][-1]
        else:
            context = repo[i]
        ans = []
        for m in p.finditer(node.code[context.start:context.end]):
            if exception is None or context.lowest_context_for_char(m.start()+context.start).context_type not in exception:
                ans.append([m.group(), m.start()+context.start])
        if is_multi_d:  # if it is a list, use the last column
            repo[i].append(ans)
        else:
            repo[i] = [context, ans]


def build_regex_dict(node, regex, exception=None, dict_repo=None, ):
    if dict_repo is None:
        dict_repo = {}
    if not isinstance(regex, regex_type):
        p = re.compile(regex)
    else:
        p = regex
    for m in p.finditer(node.code):
        context = node.lowest_context_for_char(m.start())
        if exception is None or context.context_type not in exception:
            if m.group() in dict_repo:
                dict_repo[m.group()].append([m.start(), context])
            else:
                dict_repo[m.group()] = [[m.start(), context]]
    return dict_repo


class OzDocParser:

    def __init__(self, code=None, context_type=None, description=None, id_start=0, priority_context_rules=None, context_rules=None):

        self.id_count = id_start
        self.base_node = ParserNode()
        self.base_node.context_id = id_start
        self.base_node.context_type = context_type
        self.base_node.description = description
        self.base_node.code = code
        self.base_node.children = []

        #  default rules are for Oz
        self.priority_context_rules = priority_context_rules
        self.context_rules = context_rules
        self.build_abstract_syntax_tree(self.base_node)

    def priority_rule_check_open(self, main_node, rules, current_context, offset, line):
        stop_flag = False
        for rule in rules:
            ans = eval_rule(main_node, offset, rule[1], rule[2])
            if ans is not None:
                current_context = current_context.open_new_context(self.next_node_id(), context_type=rule[0],
                                                                   start=offset, line_start=line,
                                                                   description=None if rule[0] == rule[2] else ans)
                offset = offset + len(ans)
                stop_flag = True
                break
        return [current_context, offset, stop_flag]

    def priority_rule_check_close(self, main_node, rules, current_context, offset, line):
        stop_flag = False
        for rule in rules:
            if current_context.context_type == rule[0]:  # if we are in a priority rule
                ans = eval_rule(main_node, offset, rule[3], rule[4])
                if ans is not None:
                    offset = offset + len(ans)
                    current_context = current_context.close_node_context(end=offset, line_end=line)
                    stop_flag = True
                    break

                if not stop_flag:  # even if we did not close it, we must skip all the rest because of exclusivity
                    stop_flag = True
                    offset = offset + 1
                break
        return [current_context, offset, stop_flag]

    def non_priority_rule_check(self, main_node, rules, current_context, offset, line):
        stop_flag = False
        for rule in rules:
            if current_context.context_type == rule[0]:  # if we are in the rule
                ans = eval_rule(main_node, offset, rule[3], rule[4])  # check if we must close it
                if ans is not None:
                    offset = offset + len(ans)
                    current_context = current_context.close_node_context(end=offset, line_end=line)
                    stop_flag = True
                    break
            ans = eval_rule(main_node, offset, rule[1], rule[2])  # check if we must open a new rule
            if ans is not None:
                current_context = current_context.open_new_context(self.next_node_id(), context_type=rule[0],
                                                                   start=offset, line_start=line,
                                                                   description=None if rule[0] == rule[2] else ans)
                offset = offset + len(ans)
                stop_flag = True
                break
        return [current_context, offset, stop_flag]

    def next_node_id(self):
        self.id_count = self.id_count + 1
        return self.id_count

    def build_abstract_syntax_tree_dir(self, main_node):
        last_dir = main_node
        for dirName, subdirList, file_list in os.walk(self.base_node.description):
            if dirName != main_node.description:
                last_dir = last_dir.open_new_context(self.next_node_id(), "dir",
                                                     description=dirName)
            for file_name in file_list:
                child = last_dir.open_new_context(self.next_node_id(), "file", description=os.path.join(dirName, file_name))
                self.build_abstract_syntax_tree(child)

    def build_abstract_syntax_tree(self, main_node):

        if main_node.code is None and main_node.context_type == "file" and main_node.description is not None:
            main_node.code = FileHandler.file_to_string(main_node.description)

        if main_node.context_type == "dir":
            self.build_abstract_syntax_tree_dir(main_node)
            return

        main_node.start = 0
        main_node.end = len(main_node.code)
        main_node.line_start = 1
        main_node.line_end = StringTools.count_lines(main_node.code)

        current_context = main_node
        line = 1
        last_n = None
        offset = main_node.start

        while offset < main_node.end:
            previous_context = current_context
            # increase line counter at end of loop whenever you find '\n'
            line_flag = False
            if offset != last_n and main_node.code[offset] == '\n':
                last_n = offset  # if \n is not eaten, we must be sure we do not compute the line skip more than once
                line_flag = True

            # close priority contexts: ignore all but the closure, used for strings and comments
            [current_context, offset, stop_flag] = \
                self.priority_rule_check_close(main_node=main_node, rules=self.priority_context_rules,
                                               current_context=current_context, offset=offset, line=line)

            # here, we are sure we are not in a priority rule
            if not stop_flag:
                [current_context, offset, stop_flag] = \
                    self.priority_rule_check_open(main_node=main_node, rules=self.priority_context_rules,
                                                  current_context=current_context, offset = offset, line=line)

            # Non priority contexts:
            if not stop_flag:
                [current_context, offset, stop_flag] = \
                    self.non_priority_rule_check(main_node=main_node, rules=self.context_rules,
                                                 current_context=current_context, offset=offset, line=line)

            # if we did not find anything, remember to skip to next character
            if not stop_flag:
                offset = offset + 1

            # increase line counter at end of loop whenever you find '\n'
            if line_flag:
                line = line + 1

    # Print Functions

    def print_tree(self):
        print(self)

    def __str__(self):
        return self.base_node.repr_tree()


if __name__ == "__main__":
    print("Error: This script is part of the OzDoc framework and should not be ran alone. "
          "Please locate and run OzDoc.py")
