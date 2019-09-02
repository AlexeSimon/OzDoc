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

import src.OzDocParser as OzDocParser
import src.ListTools as ListTools
import src.PrintTools as PrintTools
import re
import os
from yattag import Doc, indent
from pathlib import Path
from src import FileHandler as fh

supported_tags = ['@param', '@throws', '@return', '@see', '@since', '@version', '@pre', '@post', '@author', '@todo']
supported_names = ['Parameters', 'Throws', 'Returns', 'See Also', 'Since', 'Version', 'Pre-Conditions', 'Post-Conditions', 'Author', 'Todo']
supported_labels = ['paramLabel', 'throwLabel', 'returnLabel', 'seeLabel', 'sinceLabel', 'versionLabel', 'preLabel', 'postLabel', 'authorLabel', 'todoLabel']
TODO_TAG = '@todo'

OZ_FILE_CLASS = 'oz_file'
OZ_KEYWORD_CLASS = 'oz_keyword'
OZ_KEYWORD_SIMPLE_CLASS = 'oz_keyword_simple'
OZ_ATOM_CLASS = 'oz_atom'
OZ_COMMENT_CLASS = 'oz_comment'
OZ_COMMENT_CLASS_AST = 'oz_comment_ast'
SHOW_BUTTON_CLASS = 'showCodeButton'
REGEX_PATH_SPLIT = re.compile("/|\\\\")
ROOT_CONTEXTS = ["dir", "file", "text"]
USUAL_KEYWORDS = ["case", "class", "for", "fun", "if", "local", "meth", "proc", "try",
                  "andthen", "at", "break", "catch", "declare", "else", "elseif", "finally", "of", "in", "then"]

gen_directory = ""
settings = ""
# origin_parser = ""


def run(parser, settings_arg, out):
    global gen_directory, settings  # , origin_parser
    # origin_parser = parser
    settings = settings_arg
    gen_directory = out

    if parser.base_node.context_type == 'dir':
        generate_directory_doc(parser.base_node, out)
    elif parser.base_node.context_type == 'file':
        generate_file_doc(parser.base_node, out)
    elif parser.base_node.context_type == 'text':
        generate_file_doc(parser.base_node, out)
    else:
        raise Exception("An error has occured. Expected 'file', 'dir' or 'text' as top node of the tree, got: {}.")\
            .format(parser.base_node.context_type)

    if parser.base_node.description:
        base_node_name = REGEX_PATH_SPLIT.split(parser.base_node.description)
        if base_node_name[len(base_node_name) - 1] != 'index.oz':
            os.remove(Path(out + '/index.html'))


def generate_directory_doc(base_node, out, prepend=""):
    dirname = REGEX_PATH_SPLIT.split(base_node.description)
    dirname = dirname[len(dirname) - 1]
    new_out = out + '/' + dirname
    if not os.path.exists(Path(new_out)):
        os.mkdir(Path(new_out))

    for child in base_node.children:
        if child.context_type == 'dir':
            generate_directory_doc(child, new_out, "../"+prepend)
        else:
            generate_file_doc(child, new_out, "../"+prepend)


def generate_file_doc(base_node, out, prepend=""):
    filename = base_node.context_type
    destination = out + '/index.html'

    if base_node.description:
        filename = REGEX_PATH_SPLIT.split(base_node.description)
        filename = filename[len(filename) - 1]
        destination = out + '/' + filename[:len(filename) - 3] + '.html'

    destination = Path(destination)
    template_location = Path(gen_directory+'/index.html')
    if template_location != destination:
        fh.copy_file(template_location, destination)

    fh.replace_in_file("assets/", prepend+"assets/", destination, replace_all=True)
    fh.replace_in_file('@filename', filename, destination, replace_all=True)

    generate_code_doc(base_node, destination)


def generate_code_doc(base_node, destination):
    code = base_node.code
    OzDocParser.fuse_similar_successive_contexts(base_node, settings.inline_comment_keyword)

    ###################################################################################################################
    #                 Creation of repositories containing functions, classes, comments, etc.                          #
    ###################################################################################################################
    fun_repo = OzDocParser.build_link_context_with_repo(base_node, settings.fun_keyword, settings.def_keyword)
    OzDocParser.link_following_regex_to_repo(base_node, fun_repo, settings.declarations_name_regex,
                                             exception=settings.comment_keyword)
    # Example of how to print a repository:
    # PrintTools.print_repo(fun_repo)

    fun_call_repo = OzDocParser.build_context_repo_not_in(base_node, settings.def_keyword,
                                                      ListTools.get_list_column(fun_repo, 1))

    class_repo = OzDocParser.build_context_repo(base_node, settings.class_keyword)
    OzDocParser.link_following_regex_to_repo(base_node, class_repo, settings.declarations_name_regex,
                                             exception=settings.comment_keyword)

    meth_repo = OzDocParser.build_context_repo(base_node, settings.meth_keyword)
    OzDocParser.link_following_regex_to_repo(base_node, meth_repo, settings.meth_regex,
                                             exception=settings.comment_keyword)

    comment_repo = OzDocParser.build_context_repo(base_node, settings.comment_keyword)
    OzDocParser.link_all_regex_to_repo(base_node, comment_repo, settings.ozdoc_tag_regex)

    ###################################################################################################################
    #                                     Generating general information                                              #
    ###################################################################################################################
    doc, tag, text, line = Doc().ttl()
    with tag('div', klass='general-info'):
        title = base_node.context_type
        if base_node.description:
            title = REGEX_PATH_SPLIT.split(base_node.description)
            title = title[len(title)-1]
        line('h2', title, style='font-weight: bold;')
        doc.stag('br')

        nothing = True

        # Section for context hierarchy, if not root node
        if base_node.parent:
            nothing = False
            line('h3', 'From:')
            with tag('ul'):
                with tag('li'):
                    text(make_context_hierarchy(base_node.parent, fun_repo, class_repo, meth_repo))
            doc.stag('br')

        # Section for unusual keywords found
        unusual_kw = []
        USUAL_CONTEXT = USUAL_KEYWORDS + settings.fun_keyword + settings.class_keyword + settings.meth_keyword \
                        + settings.comment_keyword + settings.def_keyword + settings.string_keyword\
                        + ROOT_CONTEXTS + ["[]", "var", "atom"]
        for node in base_node.iter_children():
            if node.context_type not in USUAL_CONTEXT:
                unusual_kw.append(node)
        if unusual_kw:
            nothing = False
            line('h3', 'Non-frequent keywords found:')
            with tag('ul'):
                for kw in unusual_kw:
                    with tag('li', klass='oz-code'):
                        line('span', kw.context_type, klass=OZ_KEYWORD_SIMPLE_CLASS)
                        text(", at line " + str(kw.line_start))
                        hierarchy = make_context_hierarchy(kw.parent if kw.parent else kw, fun_repo, class_repo, meth_repo, get_root=False)
                        if hierarchy:
                            text(" (in ")
                            line('i', hierarchy)
                            text(")")
            doc.stag('br')

        # Section for TODO tags
        todotags = []
        for comment in comment_repo:
            taglist = comment[1]
            for i, tag_found in enumerate(taglist):
                if tag_found[0] == TODO_TAG:
                    # Origin (for context hierarchy)
                    origin = comment[0]
                    next_sister = origin.find_next_sister()
                    if next_sister:
                        if next_sister.context_type in settings.fun_keyword \
                                or next_sister.context_type in settings.meth_keyword \
                                or next_sister.context_type in settings.class_keyword:
                            origin = next_sister

                    if origin.context_type in settings.comment_keyword:
                        if origin.parent:
                            origin = origin.parent

                    # Content
                    start = tag_found[1]
                    end = taglist[i+1][1] - 1 if i < (len(taglist) - 1) else comment[0].end
                    content = code[start:end][(len(TODO_TAG)):].rstrip(' ').rstrip('/*%')

                    if todotags:
                        if origin.start == todotags[len(todotags)-1][0].start:
                            todotags[len(todotags)-1][1].append(content)
                        else:
                            todotags.append([origin, [content]])
                    else:
                        todotags.append([origin, [content]])
        if todotags:
            nothing = False
            with tag('div', klass='TODO'):
                line('h3', 'TODO', style='font-weight: bold;')
                for t in todotags:
                    with tag('ul'):
                        with tag('li'):
                            text(make_context_hierarchy(t[0], fun_repo, class_repo, meth_repo) + ', at line ' + str(t[0].line_start) + ':')
                            for content in t[1]:
                                with tag('ul'):
                                    line('li', content)
            doc.stag('br')

        if nothing:
            text('No unusual information concerning ' + title + '.')
    fh.replace_in_file('@general_info', doc.getvalue(), destination)

    ###################################################################################################################
    #                                     Generating abstract syntax tree                                             #
    ###################################################################################################################
    doc, tag, text = Doc().tagtext()
    with tag('pre', klass='oz-code'):
        doc.asis(gen_html_ast(base_node, ROOT_CONTEXTS + settings.oz_block_keywords, ["\'", "\"", "`"]))
    ast = doc.getvalue()
    fh.replace_in_file('@abstract_syntax_tree', ast, destination)

    ###################################################################################################################
    #                                          Generating source code                                                 #
    ###################################################################################################################
    doc, tag, text = Doc().tagtext()
    with tag('pre', klass='line-numbers'):
        with tag('code', klass='language-oz'):
            text(code)
    source_code = doc.getvalue()
    fh.replace_in_file('@source_code', source_code, destination)

    ###################################################################################################################
    #                        Generating the head of the table containing all of the classes                           #
    ###################################################################################################################
    new_classtablehead = ""
    if class_repo:
        doc, tag, text = Doc().tagtext()
        with tag('thead'):
            with tag('tr'):
                with tag('th'):
                    text('Class')
                with tag('th'):
                    text('Description')
        new_classtablehead = indent(doc.getvalue())
    fh.replace_in_file('@classtablehead', new_classtablehead, destination)

    ###################################################################################################################
    #                        Generating the body of the table containing all of the classes                           #
    ###################################################################################################################
    if class_repo:
        doc, tag, text, line = Doc().ttl()
        with tag('tbody'):
            for klass in class_repo:
                klassname = klass[1]
                with tag('tr'):
                    with tag('td'):
                        with tag('a', href="#" + klass[1] + str(klass[0].node_id)):
                            text(klassname)
                    with tag('td'):
                        description = ""
                        prev_sister = klass[0].find_previous_sister()
                        if prev_sister:
                            if prev_sister.context_type in settings.comment_keyword:  # if previous sister is a comment
                                description = code[prev_sister.start:prev_sister.end].split('\n')[0][:200]
                                description = description.lstrip('/*% ').rstrip('/*% ')
                        text(description)

                        # Getting methods of the class
                        methlist = []
                        for meth in meth_repo:
                            if meth[0].start > klass[0].start and meth[0].end < klass[0].end:
                                methlist.append(meth)
                        if methlist:
                            doc.stag('br')
                            line('u', 'Contains methods')
                            text(' : ')
                            for i, meth in enumerate(methlist):
                                if i > 0:
                                    doc.asis('&nbsp;')
                                    text(',')
                                    doc.asis('&nbsp;')
                                with tag('a', href="#" + meth[1] + str(meth[0].node_id)):
                                    text(meth[1])
                            text('.')

                        # Making context hierarchy
                        context_hierarchy = make_context_hierarchy(klass[0].parent if klass[0].parent else klass[0],
                                                                   fun_repo, class_repo, meth_repo)
                        if context_hierarchy:
                            doc.stag('br')
                            with tag('i'):
                                text('(from: ' + context_hierarchy + ')')
        new_classtablebody = indent(doc.getvalue())
        fh.replace_in_file('@classtablebody', new_classtablebody, destination)

    ###################################################################################################################
    #                     Generating the section containing the details of all of the methods                         #
    ###################################################################################################################
    new_methoddetails = ""
    if meth_repo:
        doc, tag, text, line = Doc().ttl()
        with tag('ul', klass='blockList'):
            with tag('li', klass='blockList'):
                with tag('ul', klass='blockList'):
                    klass = class_repo[0]  # @TODO
                    line('h3', klass[1], id=klass[1] + str(klass[0].node_id))
                    for method in meth_repo:
                        methname = method[1]
                        if methname != '$':
                            with tag('li', klass='blockListDetails'):
                                line('h4', methname, id=method[1] + str(method[0].node_id))
                                with tag('pre', style='font-style: italic;'):
                                    text(method[0].context_type + ' ' + method[1]) # normally function signature

                                    # @TODO
                                    # Check if the @throws tag is used.
                                    # (get sister, make taglist)
                                    # throws_found = tag_found_in_comment('@throws', taglist)
                                    # # If exception thrown, add :
                                    # text('\n\t\t\tthrows ')
                                    # line('a', 'Insert Exception Name', href='')

                                description = ""
                                prev_sister = method[0].find_previous_sister()
                                k = -1  # index of previous sister (if it is a comment) in comment_repo

                                if prev_sister:
                                    if prev_sister.context_type in settings.comment_keyword:
                                        # Entered if previous sister is a comment
                                        start = prev_sister.start
                                        end = prev_sister.end

                                        # Find it in comment_repo as well.
                                        for i, x in enumerate(comment_repo):
                                            if x[0].start == prev_sister.start:
                                                k = i
                                                for tag_found in comment_repo[k][1]:
                                                    if tag_found[0] in supported_tags:
                                                        end = tag_found[1]
                                                        break
                                                break
                                        description = code[start:end]

                                with tag('pre'):
                                    description = description.split('\n')
                                    for d in description:
                                        line('code', d.lstrip('/*% '), klass='block')

                                if k != -1:
                                    if comment_repo[k][1]:
                                        with tag('dl'):
                                            taglist = comment_repo[k][1]
                                            end_of_comment = comment_repo[k][0].end

                                            for i in range(len(supported_tags)):
                                                found = tag_found_in_comment(supported_tags[i], taglist)
                                                if found:
                                                    make_tagged_section(supported_tags[i], supported_names[i],
                                                                        supported_labels[i], taglist, end_of_comment,
                                                                        tag, text, line, code)

                                with tag('dd'):
                                    fun_id = method[1] + str(method[0].node_id) + 'code'
                                    line('button', 'Source Code', onclick='show' + fun_id + '()', klass=SHOW_BUTTON_CLASS)
                                    with tag('pre', ('data-start', str(method[0].line_start)),
                                             id=fun_id, style='display: none;', klass="line-numbers"):
                                        # line('code', (code[function[0].start:function[0].end]))
                                        with tag('code', klass='language-oz'):
                                            text(code[method[0].start:method[0].end])

                                    show_fun_def = 'function %s() {' \
                                                   '  var x = document.getElementById("%s");' \
                                                   '  if (x.style.display === "none") {' \
                                                   '    x.style.display = "block";' \
                                                   '  } else {' \
                                                   '    x.style.display = "none";' \
                                                   '   }' \
                                                   '}' % ('show' + fun_id, fun_id)
                                    line('script', show_fun_def)

        new_methoddetails = indent(doc.getvalue())
    fh.replace_in_file('@methoddetails', new_methoddetails, destination)

    ###################################################################################################################
    #                        Generating the head of the table containing all of the functions                         #
    ###################################################################################################################
    new_functablehead = ""
    if fun_repo and any(map(lambda e: e[2] != '$', fun_repo)):
        doc, tag, text = Doc().tagtext()
        with tag('thead'):
            with tag('tr'):
                with tag('th'):
                    text('Function')
                with tag('th'):
                    text('Type')
                with tag('th'):
                    text('Description')
        new_functablehead = indent(doc.getvalue())
    fh.replace_in_file('@functablehead', new_functablehead, destination)

    ###################################################################################################################
    #                        Generating the body of the table containing all of the functions                         #
    ###################################################################################################################
    new_functablebody = ""
    if fun_repo:
        doc, tag, text = Doc().tagtext()
        with tag('tbody'):
            for function in fun_repo:
                funcname = function[2]
                if funcname != '$':
                    with tag('tr'):
                        with tag('td'):
                            with tag('a', href="#" + function[2] + str(function[0].node_id)):
                                text(funcname)
                        with tag('td'):
                            text(function[0].context_type)
                        with tag('td'):
                            description = ""
                            prev_sister = function[0].find_previous_sister()
                            if prev_sister:
                                if prev_sister.context_type in settings.comment_keyword:  # if previous sister is a comment
                                    description = code[prev_sister.start:prev_sister.end].split('\n')[0][:200]
                                    description = description.lstrip('/*% ').rstrip('/*% ')
                            text(description)

                            context_hierarchy = make_context_hierarchy(function[0].parent if function[0].parent else function[0],
                                                                       fun_repo, class_repo, meth_repo)
                            if context_hierarchy:
                                doc.stag('br')
                                with tag('i'):
                                    text('(from: ' + context_hierarchy + ')')
        new_functablebody = indent(doc.getvalue())
    fh.replace_in_file('@functablebody', new_functablebody, destination)

    ###################################################################################################################
    #                     Generating the section containing the details of all of the functions                       #
    ###################################################################################################################
    new_functiondetails = ""
    if fun_repo and any(map(lambda e: e[2] != '$', fun_repo)):
        doc, tag, text, line = Doc().ttl()
        with tag('ul', klass='blockList'):
            with tag('li', klass='blockList'):
                line('h3', 'Function details')
                with tag('ul', klass='blockList'):
                    for function in fun_repo:
                        funcname = function[2]
                        if funcname != '$':
                            with tag('li', klass='blockList'):
                                line('h4', funcname, id=function[2] + str(function[0].node_id))
                                with tag('pre', style='font-style: italic;'):
                                    text(function[0].context_type + ' ' + code[function[1].start:function[1].end])

                                    # @TODO
                                    # Check if the @throws tag is used.
                                    # (get sister, make taglist)
                                    # throws_found = tag_found_in_comment('@throws', taglist)
                                    # # If exception thrown, add :
                                    # text('\n\t\t\tthrows ')
                                    # line('a', 'Insert Exception Name', href='')

                                description = ""
                                prev_sister = function[0].find_previous_sister()
                                k = -1  # index of previous sister (if it is a comment) in comment_repo

                                if prev_sister:
                                    if prev_sister.context_type in settings.comment_keyword:
                                        # Entered if previous sister is a comment
                                        start = prev_sister.start
                                        end = prev_sister.end

                                        # Find it in comment_repo as well.
                                        for i, x in enumerate(comment_repo):
                                            if x[0].start == prev_sister.start:
                                                k = i
                                                for tag_found in comment_repo[k][1]:
                                                    if tag_found[0] in supported_tags:
                                                        end = tag_found[1]
                                                        break
                                                break
                                        description = code[start:end]

                                with tag('pre'):
                                    description = description.split('\n')
                                    for d in description:
                                        line('code', d.lstrip('/*% '), klass='block')

                                if k != -1:
                                    if comment_repo[k][1]:
                                        with tag('dl'):
                                            taglist = comment_repo[k][1]
                                            end_of_comment = comment_repo[k][0].end

                                            for i in range(len(supported_tags)):
                                                found = tag_found_in_comment(supported_tags[i], taglist)
                                                if found:
                                                    make_tagged_section(supported_tags[i], supported_names[i],
                                                                        supported_labels[i], taglist, end_of_comment,
                                                                        tag, text, line, code)

                                with tag('dd'):  # or 'dt' for no space
                                    fun_id = function[2] + str(function[0].node_id) + 'code'
                                    line('button', 'Source Code', klass=SHOW_BUTTON_CLASS, onclick='show' + fun_id + '()')
                                    with tag('pre', ('data-start', str(function[0].line_start)),
                                             id=fun_id, style='display: none;', klass="line-numbers"):
                                        with tag('code', klass='language-oz'):
                                            text(code[function[0].start:function[0].end])

                                    show_fun_def = 'function %s() {' \
                                                   '  var x = document.getElementById("%s");' \
                                                   '  if (x.style.display === "none") {' \
                                                   '    x.style.display = "block";' \
                                                   '  } else {' \
                                                   '    x.style.display = "none";' \
                                                   '   }' \
                                                   '}' % ('show' + fun_id, fun_id)
                                    line('script', show_fun_def)
        new_functiondetails = indent(doc.getvalue())
    fh.replace_in_file('@functiondetails', new_functiondetails, destination)


def tag_found_in_comment(tag_searched, taglist):
    for tag_found in taglist:
        if tag_found[0] == tag_searched:
            return True
    return False


def make_tagged_section(section_tag, section_name, section_label, taglist, end_of_comment, tag, text, line, code):
    with tag('dt'):
        line('span', '{}:'.format(section_name), klass=section_label)
    for i in range(len(taglist)):
        tag_found = taglist[i]
        if tag_found[0] == section_tag:
            start = tag_found[1]
            end = taglist[i + 1][1] - 1 if i < (len(taglist) - 1) else end_of_comment

            with tag('dd', klass=section_label):
                with tag('code'):
                    text('-- ')
                text(code[start:end][(len(section_tag)):].rstrip(' ').rstrip('/*%'))


def make_context_hierarchy(node, fun_repo, class_repo, meth_repo, get_root=True):
    context_hierarchy = ""
    link = ""

    got_root = False
    while node.parent:

        if node.context_type in settings.fun_keyword:
            name = ""
            for repo_node in fun_repo:
                if repo_node[0].start == node.start:
                    name = repo_node[2]
                    break
            context_hierarchy = node.context_type + '(' + name + ')' + link + context_hierarchy

        elif node.context_type in settings.class_keyword:
            name = ""
            for repo_node in class_repo:
                if repo_node[0].start == node.start:
                    name = repo_node[1]
                    break
            context_hierarchy = node.context_type + '(' + name + ')' + link + context_hierarchy

        elif node.context_type in settings.meth_keyword:
            name = ""
            for repo_node in meth_repo:
                if repo_node[0].start == node.start:
                    name = repo_node[1]
                    break
            context_hierarchy = node.context_type + '(' + name + ')' + link + context_hierarchy

        elif node.context_type in ROOT_CONTEXTS:
            if get_root:
                name = ""
                if node.description:
                    name = REGEX_PATH_SPLIT.split(node.description)
                    name = name[len(name)-1]
                if name:
                    context_hierarchy = name + link + context_hierarchy
                else:
                    context_hierarchy = node.context_type + link + context_hierarchy
                got_root = True
            break

        else:
            context_hierarchy = node.context_type + link + context_hierarchy
        node = node.parent
        link = " > "
    if get_root and node.description and not got_root:
        filename = REGEX_PATH_SPLIT.split(node.description)
        context_hierarchy = filename[len(filename) - 1] + link + context_hierarchy
    return context_hierarchy


def gen_html_ast(tree, fold, ignore):
    AST_SIMPLE_KEYWORDS = settings.def_keyword + ['var', 'atom', 'string1', 'string2']

    def rec_print(node, level, last, lines, folded):
        ans = ""
        for j in range(level):
            if lines[j]:
                ans += "&#9474;"  # "│"
            else:
                ans += " "
            ans += " " * 9

        if last:
            ans += "&#9492;"  # "└"
        else:
            ans += "&#9500;"  # "├"

        if node.context_type not in fold:
            node_string = str(node)
            if any(word in node_string for word in AST_SIMPLE_KEYWORDS):
                node_string = replace_adequate_word(node_string, AST_SIMPLE_KEYWORDS, OZ_ATOM_CLASS)
            elif any(word in node_string for word in settings.comment_keyword):
                node_string = replace_adequate_word(node_string, settings.comment_keyword, OZ_COMMENT_CLASS_AST)
            else:
                node_string = replace_adequate_word(node_string, settings.oz_simple_keywords, OZ_KEYWORD_SIMPLE_CLASS)

            ans += node_string
            folded.append(False)
        else:
            node_string = str(node)
            if 'file' in node_string:
                node_string = wrap_color_class(node_string, OZ_FILE_CLASS)
            else:
                node_string = replace_adequate_word(node_string, settings.oz_block_keywords, OZ_KEYWORD_CLASS)
            ans += "<button class=\"collapsible\">" + node_string + "</button><div class=\"content\">"
            folded.append(True)

        ans += "\n"

        kids = []
        for kid in node.children:
            if kid.context_type not in ignore:
                kids.append(kid)

        for i in range(len(kids)):
            if i == len(kids) - 1:
                lines.append(False)
                ans += rec_print(kids[i], level + 1, True, lines, folded)
            else:
                lines.append(True)
                ans += rec_print(kids[i], level + 1, False, lines, folded)
        del lines[-1]

        if last:
            for j in range(level):
                if lines[j]:
                    ans += "&#9474;"  # "│"
                else:
                    ans += " "
                ans += " " * 9

        if folded[-1]:
            ans = ans[:-1] + "</div>\n"
        elif last:
            ans += "\n"
        del folded[-1]
        return ans

    return rec_print(tree, 0, True, [False], [True])


# Used by AST creator
def replace_adequate_word(source_string, word_list, color_class):
    for word in word_list:
        if word in source_string:
            return color_string(source_string, word, color_class)
    return source_string


def color_string(source_string, string_to_replace, color_class):
    return source_string.replace(string_to_replace, wrap_color_class(string_to_replace, color_class))


def wrap_color_class(string, color_class):
    return "<span class=\"" + color_class + "\">" + string+"</span>"


if __name__=="__main__":
    print("Error: This script is part of the OzDoc framework and should not be ran alone. "
          "Please locate and run OzDoc.py")
