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

class ParserNode:

    def __init__(self, node_id=None, context_type=None, parent=None, children=None, start=None, end=None, line_start=None, line_end=None, description=None, code=None, line_repo=None):
        self.node_id = node_id
        self.context_type = context_type
        self.parent = parent
        self.children = children
        self.start = start
        self.end = end
        self.line_start = line_start
        self.line_end = line_end
        self.description = description
        self.code = code

    def add_child(self, child):
        if self.children is not None:
            self.children.append(child)
        else:
            self.children = [child]

    def open_new_context(self, node_id, context_type, start=None, line_start=None, description=None):
        temp_context = ParserNode(node_id=node_id, context_type=context_type,
                                  parent=self, children=[],
                                  start=start, line_start=line_start,
                                  description=description)
        self.add_child(temp_context)
        return temp_context

    def close_node_context(self, end, line_end):
        self.end = end
        self.line_end = line_end
        return self.parent

    def lowest_context_for_char(self, position):  # find the lowest context for that char position,
        # starting the exploration from the node and only going down
        current = self
        if not (self.start <= position < self.end):
            return None

        for child in current.children:
            if child.start <= position < child.end:
                return child.lowest_context_for_char(position)

        return current

    def lowest_context_for_line(self, position, Acc=None):  # find the first lowest context for that line position,
        # starting the exploration from the node and only going down
        current = self
        if not (self.line_start <= position < self.line_end):
            return None

        for child in current.children:
            if child.start <= position < child.end:
                return child.lowest_context_for_line(position)

        return current

    def __str__(self):
        ans = str(self.context_type)

        if self.description is not None:
            ans += " (" + str(self.description) + ")"

        if self.line_start is not None and self.line_end is not None:
            ans += " @L[" + str(self.line_start) + ":" + str(self.line_end) + "]"\

        if self.start is not None and self.end is not None:
            ans += " @C[" + str(self.start) + ":" + str(self.end) + "]"

        return ans

    def repr_tree(self):
        def rec_print(node, level, last, lines):
            ans = ""
            for j in range(level):
                if lines[j]:
                    ans += "│"
                else:
                    ans += " "
                ans += " " * 9

            if last:
                ans += "└"
            else:
                ans += "├"

            ans += str(node) + "\n"

            for i in range(len(node.children)):
                if i == len(node.children)-1:
                    lines.append(False)
                    ans += rec_print(node.children[i], level + 1, True, lines)
                else:
                    lines.append(True)
                    ans += rec_print(node.children[i], level + 1, False, lines)
            del lines[-1]

            if last:
                for j in range(level):
                    if lines[j]:
                        ans += "│"
                    else:
                        ans += " "
                    ans += " " * 9
                ans += "\n"

            return ans
        return rec_print(self, 0, True, [False])

    def get_code(self):
        if self.code is not None:
            return self.code
        else:
            temp = self.parent
            while temp is not None:
                if temp.code is None:
                    temp = temp.parent
                else:
                    return temp.code[self.start:self.end]

    def iter_children(self):
        yield self
        for child in self.children:
            for kid in child.iter_children():
                yield kid

    def find_previous_sister(self):
        """Finds and returns the previous sister node of self

        :return: node. The previous sister node of self. None if self has no previous sister, no parent,
                       or if self.parent.children isn't iterable due to serious programmer mistakes.
        """
        siblings = self.parent
        siblings = siblings.children if siblings is not None else siblings
        if siblings:
            prev = None
            for sibling in siblings:
                if sibling == self:
                    return prev
                else:
                    prev = sibling

    def find_next_sister(self):
        """Finds and returns the next sister node of self

        :return: node. The next sister node of self. None if self has no next sister, no parent,
                       or if self.parent.children isn't iterable due to serious programmer mistakes.
        """
        siblings = self.parent
        siblings = siblings.children if siblings is not None else siblings
        if siblings:
            found = False
            for sibling in siblings:
                if found:
                    return sibling
                if sibling == self:
                    found = True


if __name__=="__main__":
    print("Error: This script is part of the OzDoc framework and should not be ran alone. Please locate and run OzDoc.py")
