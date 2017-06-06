import os
import re

from dfg.dfg import DFG
from astvisitor import ASTVisitor
from pycparser import c_parser
from pycparser.plyparser import ParseError
from config import debug, rewrite
import pickle

data_dir = 'ProgramData'
graph_dir = 'graph'
debug_dir = 'debug'


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


def process_file(f, graph_file_name, debug_file_name):
    d = open(debug_file_name, "w")
    code = f.read()
    parser = c_parser.CParser()
    try:
        ast = parser.parse(comment_remover(code))
        graphs = ASTVisitor().visit(ast)
        for name, graph in graphs:
            print("=========", file=d)
            print(code, file=d)
            print("-----", file=d)
            print(name, file=d)
            graph.print(d)
            dfg = DFG(graph)
            print("-----", file=d)
            dfg.print(d)
            with open(graph_file_name, "wb") as o:
                pickle.dump(dfg, o)

    except ParseError as e:
        print("{} can not parsed".format(f))
        raise e
    except Exception as e:
        print(f)
        raise e


def preprocess():
    ignores = [
        ("10", "696.txt"),
        ("46", "36.txt"),
        ("8", "1331.txt"),
        ("80", "282.txt"),
    ]

    for subdir_name in os.listdir(data_dir):
        data_subdir = data_dir + "/" + subdir_name
        graph_subdir = graph_dir + "/" + subdir_name
        debug_subdir = debug_dir + "/" + subdir_name

        if not os.path.exists(graph_subdir):
            os.mkdir(graph_subdir)

        if not os.path.exists(debug_subdir):
            os.mkdir(debug_subdir)

        for file_name in os.listdir(data_subdir):
            data_file = data_subdir + "/" + file_name
            graph_file = graph_subdir + "/" + file_name
            debug_file = debug_subdir + "/" + file_name

            if not rewrite and os.path.exists(graph_file):
                continue

            if (subdir_name, file_name) in ignores:
                continue

            with open(data_file, errors='ignore') as f:
                process_file(f, graph_file, debug_file)

            if debug:
                return
        print("{} completed".format(subdir_name))

preprocess()

print("preprocess end")

