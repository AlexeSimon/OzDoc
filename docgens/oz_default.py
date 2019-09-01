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

supported_tags = ['@param', '@throws', '@return', '@see', '@since', '@version', '@pre', '@post']
supported_names = ['Parameters', 'Throws', 'Returns', 'See Also', 'Since', 'Version', 'Pre-Conditions', 'Post-Conditions']
supported_labels = ['paramLabel', 'throwLabel', 'returnLabel', 'seeLabel', 'sinceLabel', 'versionLabel', 'preLabel', 'postLabel']

OZ_FILE_CLASS = 'oz_file'
OZ_KEYWORD_CLASS = 'oz_keyword'
OZ_KEYWORD_SIMPLE_CLASS = 'oz_keyword_simple'
OZ_ATOM_CLASS = 'oz_atom'
OZ_COMMENT_CLASS = 'oz_comment'
OZ_COMMENT_CLASS_AST = 'oz_comment_ast'
SHOW_BUTTON_CLASS = 'showCodeButton'
REGEX_PATH_SPLIT = re.compile("/|\\\\")
gen_directory = ""


def run(parser, settings, out):
    global gen_directory
    gen_directory = out
    if parser.base_node.context_type == 'dir':
        generate_directory_doc(parser.base_node, settings, out)
    elif parser.base_node.context_type == 'file':
        generate_file_doc(parser.base_node, settings, out)
    elif parser.base_node.context_type == 'text':
        generate_file_doc(parser.base_node, settings, out)
    else:
        raise Exception("An error has occured. Expected 'file', 'dir' or 'text' as top node of the tree, got: {}.")\
            .format(parser.base_node.context_type)

    if parser.base_node.description:
        base_node_name = REGEX_PATH_SPLIT.split(parser.base_node.description)
        if base_node_name[len(base_node_name) - 1] != 'index.oz':
            os.remove(Path(out + '/index.html'))


def generate_directory_doc(base_node, settings, out, prepend=""):
    dirname = REGEX_PATH_SPLIT.split(base_node.description)
    dirname = dirname[len(dirname) - 1]
    new_out = out + '/' + dirname
    if not os.path.exists(Path(new_out)):
        os.mkdir(Path(new_out))

    for child in base_node.children:
        if child.context_type == 'dir':
            generate_directory_doc(child, settings, new_out, "../"+prepend)
        else:
            generate_file_doc(child, settings, new_out, "../"+prepend)


def generate_file_doc(base_node, settings, out, prepend=""):
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

    generate_code_doc(base_node, settings, destination)


def generate_code_doc(base_node, settings, destination):
    code = base_node.code
    OzDocParser.fuse_similar_successive_contexts(base_node, settings.inline_comment_keyword)

    ###################################################################################################################
    #                      Creation of the repository of all functions, and function calls                            #
    ###################################################################################################################
    fun_repo = OzDocParser.build_link_context_with_repo(base_node, settings.fun_keyword, settings.def_keyword)
    OzDocParser.link_following_regex_to_repo(base_node, fun_repo, settings.fun_regex,
                                             exception=settings.comment_keyword)

    call_repo = OzDocParser.build_context_repo_not_in(base_node, settings.def_keyword,
                                                      ListTools.get_list_column(fun_repo, 1))

    meth_repo = OzDocParser.build_context_repo(base_node, settings.meth_keyword)
    OzDocParser.link_following_regex_to_repo(base_node, meth_repo, settings.meth_regex,
                                             exception=settings.comment_keyword)

    # PrintTools.print_repo(meth_repo)

    ###################################################################################################################
    #                               Creation of the repository of all comments                                        #
    ###################################################################################################################
    comment_repo = OzDocParser.build_context_repo(base_node, settings.comment_keyword)
    OzDocParser.link_all_regex_to_repo(base_node, comment_repo, settings.ozdoc_tag_regex)

    class_repo = OzDocParser.build_link_context_with_repo(base_node, settings.class_keyword, ['{'])
    OzDocParser.link_following_regex_to_repo(base_node, class_repo, settings.fun_regex,
                                             exception=settings.comment_keyword)

    ###################################################################################################################
    #                                     Generating abstract syntax tree                                             #
    ###################################################################################################################
    doc, tag, text = Doc().tagtext()
    with tag('pre', klass='oz-code'):
        doc.asis(gen_html_ast(base_node, ["dir", "file", "text"] + settings.oz_block_keywords, ["\'", "\"", "`"], settings))
    ast = doc.getvalue()
    fh.replace_in_file('@abstract_syntax_tree', ast, destination)

    doc, tag, text = Doc().tagtext()
    with tag('script'):
        text(open(Path(gen_directory+"/assets/ast/ast_script.js"), "r").read())
    fh.replace_in_file('@abstract_syntax_tree_script', indent(doc.getvalue()), destination)

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
    if fun_repo:
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
    doc, tag, text = Doc().tagtext()
    with tag('tbody'):
        for klass in class_repo:
            klassname = klass[2]
            if klassname != '$':
                with tag('tr'):
                    with tag('td'):
                        with tag('a', href="#" + klass[2] + str(klass[0].node_id)):
                            text(klassname)
                    with tag('td'):
                        description = ""
                        prev_sister = klass[0].find_previous_sister()
                        if prev_sister:
                            if prev_sister.context_type in settings.comment_keyword:  # if previous sister is a comment
                                description = code[prev_sister.start:prev_sister.end].split('\n')[0][:80]
                                description = description.lstrip('/*% ').rstrip('/*% ')
                        text(description)

                        context_hierarchy = make_context_hierarchy(klass[0], fun_repo, settings)
                        if context_hierarchy:
                            doc.stag('br')
                            with tag('i'):
                                text('(from: ' + context_hierarchy + ')')
    new_classtablebody = indent(doc.getvalue())
    fh.replace_in_file('@classtablebody', new_classtablebody, destination)

    ###################################################################################################################
    #                        Generating the head of the table containing all of the functions                         #
    ###################################################################################################################
    new_functablehead = ""
    if fun_repo:
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

                        context_hierarchy = make_context_hierarchy(function[0], fun_repo, settings)
                        if context_hierarchy:
                            doc.stag('br')
                            with tag('i'):
                                text('(from: ' + context_hierarchy + ')')
    new_functablebody = indent(doc.getvalue())
    fh.replace_in_file('@functablebody', new_functablebody, destination)

    ###################################################################################################################
    #                     Generating the section containing the details of all of the functions                       #
    ###################################################################################################################
    doc, tag, text, line = Doc().ttl()
    with tag('ul', klass='blockList'):
        with tag('li', klass='blockList'):
            with tag('ul', klass='blockList'):
                with tag('li', klass='blockList'):
                    for function in fun_repo:
                        funcname = function[2]
                        if funcname != '$':
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

                            # Making the button to show the Source Code.
                            # with tag('dt'):
                            #     line('span', 'Source Code:', klass='codeLabel')
                            with tag('dd'):
                                fun_id = function[2] + str(function[0].node_id) + 'code'
                                line('button', 'Source Code', onclick='show' + fun_id + '()', klass=SHOW_BUTTON_CLASS)
                                with tag('pre', ('data-start', str(function[0].line_start)),
                                         id=fun_id, style='display: none;', klass="line-numbers"):
                                    # line('code', (code[function[0].start:function[0].end]))
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

            with tag('dd'):
                with tag('code'):
                    text('-- ')
                text(code[start:end][(len(section_tag)):].rstrip(' ').rstrip('/*%'))


def make_context_hierarchy(node, fun_repo, settings):
    context_hierarchy = ""
    link = ""
    if node.parent:
        node = node.parent
    while node.parent:
        if node.context_type in settings.fun_keyword:
            name = ""
            for repo_node in fun_repo:
                if repo_node[0].start == node.start:
                    name = repo_node[2]
                    break
            context_hierarchy = node.context_type + '(' + name + ')' + link + context_hierarchy
        else:
            context_hierarchy = node.context_type + link + context_hierarchy
        node = node.parent
        link = " > "
    if node.description:
        filename = REGEX_PATH_SPLIT.split(node.description)
        context_hierarchy = filename[len(filename) - 1] + link + context_hierarchy
    return context_hierarchy


def gen_html_ast(tree, fold, ignore, settings):
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
