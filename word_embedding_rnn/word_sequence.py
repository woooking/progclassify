import os
import pickle
from pycparser.c_parser import CParser
from util.util import comment_remover
from word_embedding_rnn.codetowordvisitor import CodeToWordVisitor


class WordSequence:
    def __init__(self):
        self.data = {}
        self.dictionary = {}

    def _add_words(self, words):
        for word in words:
            if not (word in self.dictionary):
                self.dictionary[word] = len(self.dictionary)

    def _words2data(self, words):
        return list(map(lambda x: self.dictionary[x], words))

    def build(self, data_dir):
        for i in range(1, 105):
            data_subdir = data_dir + "/" + str(i)
            for file_name in os.listdir(data_subdir):
                num = int(file_name[:-4])
                name = data_subdir + "/" + file_name
                with open(name, errors="ignore") as f:
                    code = f.read()
                    parser = CParser()
                    ast = parser.parse(comment_remover(code))
                    visitor = CodeToWordVisitor()
                    visitor.visit(ast)
                    seq = visitor.pre_order
                    self._add_words(seq)
                    self.data[(i, num)] = self._words2data(seq)
            print("Directory {} built".format(i))

        print("Vocabulary Size: {}".format(len(self.dictionary)))

    def save(self, dst="model/prog_words"):
        with open(dst, "wb") as f:
            pickle.dump({"data": self.data, "dictionary": self.dictionary}, f, protocol=4)

    def load(self, src="model/prog_words"):
        with open(src, "rb") as f:
            obj = pickle.load(f)
            self.data = obj["data"]
            self.dictionary = obj["dictionary"]
