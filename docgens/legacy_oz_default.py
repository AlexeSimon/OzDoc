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
from yattag import Doc, indent
from src import FileHandler as fh

supported_tags = ['@param', '@throws', '@return', '@see', '@since', '@version', '@pre', '@post']
supported_names = ['Parameters', 'Throws', 'Returns', 'See Also', 'Since', 'Version', 'Pre-Conditions', 'Post-Conditions']
supported_labels = ['paramLabel', 'throwLabel', 'returnLabel', 'seeLabel', 'sinceLabel', 'versionLabel', 'preLabel', 'postLabel']


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


def run(parser, settings, out):
    destination = out + '/index.html'
    code = parser.base_node.code
    # Creation of the repository of all functions
    fun_repo = OzDocParser.build_link_context_with_repo(parser.base_node, settings.fun_keyword, settings.def_keyword)
    OzDocParser.link_following_regex_to_repo(parser.base_node, fun_repo, settings.fun_regex,
                                             exception=settings.comment_keyword)

    # Creation of the repository of all function calls
    call_repo = OzDocParser.build_context_repo_not_in(parser.base_node, settings.def_keyword,
                                                      ListTools.get_list_column(fun_repo, 1))
    # Creation of the repository of all comments
    comment_repo = OzDocParser.build_context_repo(parser.base_node, settings.comment_keyword)
    OzDocParser.link_all_regex_to_repo(parser.base_node, comment_repo, settings.ozdoc_tag_regex)

    # Generating the body of the table containing all of the functions.
    doc, tag, text = Doc().tagtext()
    with tag('tbody'):
        for function in fun_repo:
            funcname = function[2]
            if funcname != '$':
                with tag('tr'):
                    with tag('td'):
                        text(funcname)
                    with tag('td'):
                        description = ""
                        prev_sister = function[0].find_previous_sister()
                        if prev_sister:
                            if prev_sister.context_type in settings.comment_keyword:  # if previous sister is a comment
                                description = code[prev_sister.start:prev_sister.end].split('\n')[0][:80]
                                description = description.lstrip('/*% ').rstrip('/*% ')
                        text(description)
    new_tablebody = doc.getvalue()
    fh.replace_in_file('@tablebody', new_tablebody, destination)

    # Generating the head of the table containing all of the functions.
    doc, tag, text = Doc().tagtext()
    with tag('thead'):
        with tag('tr'):
            with tag('th'):
                text('Function')
            with tag('th'):
                text('Description')
    new_tablehead = indent(doc.getvalue())
    fh.replace_in_file('@tablehead', new_tablehead, destination)

    # Generating the section containing the details of all of the functions.
    doc, tag, text, line = Doc().ttl()
    with tag('ul', klass='blockList'):
        with tag('li', klass='blockList'):
            with tag('ul', klass='blockList'):
                with tag('li', klass='blockList'):
                    for function in fun_repo:
                        funcname = function[2]
                        if funcname != '$':
                            line('h4', funcname)
                            with tag('pre', style='font-style: italic;'):
                                text(code[function[1].start:function[1].end])

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
                            with tag('dt'):
                                line('span', 'Source Code:', klass='codeLabel')
                            with tag('dd'):
                                id = str(function[0].node_id)
                                line('button', 'Show', onclick='show' + id + '()')
                                with tag('pre', id=id, style='display: none;'):
                                    line('code', (code[function[0].start:function[0].end]))
                                show_fun_def = 'function %s() {' \
                                               '  var x = document.getElementById("%s");' \
                                               '  if (x.style.display === "none") {' \
                                               '    x.style.display = "block";' \
                                               '  } else {' \
                                               '    x.style.display = "none";' \
                                               '   }' \
                                               '}' % ('show' + id, id)
                                line('script', show_fun_def)

    new_functiondetails = indent(doc.getvalue())
    fh.replace_in_file('@functiondetails', new_functiondetails, destination)


if __name__=="__main__":
    print("Error: This script is part of the OzDoc framework and should not be ran alone. Please locate and run OzDoc.py")
