import os
import re

from astvisitor import ASTVisitor
from pycparser import c_parser
from pycparser.plyparser import ParseError

datadir = 'ProgramData'


def comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return ""
        else:
            return s

    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

success = 0

ignores = [
    ("10", "696.txt"),
    ("46", "36.txt"),
    ("8", "1331.txt"),
    ("80", "282.txt"),
]

for subdir_name in os.listdir(datadir):
    # subdir_name = "71"
    subdir = datadir + "/" + subdir_name
    for file_name in os.listdir(subdir):
        # file_name = "270.txt"
        file = subdir + "/" + file_name
        if (subdir_name, file_name) in ignores:
            continue
        # print(file)
        with open(file, errors='ignore') as f:
            code = f.read()
            parser = c_parser.CParser()
            try:
                ast = parser.parse(comment_remover(code))
                success += 1
                # ast.show(showcoord=True)
                graphs = ASTVisitor().visit(ast)
                # for name, graph in graphs:
                #     print(name)
                #     graph.print()

            except ParseError as e:
                print("{} can not parsed".format(file))
                raise e
            except Exception as e:
                print(file)
                raise e
        # exit(0)
    print("{} completed".format(subdir_name))

