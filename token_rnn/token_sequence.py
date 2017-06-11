import os
import pickle
import sys
from generator import Generator
sys.path.append("..")
from util.util import comment_remover

class TokenSequence:
    def __init__(self):
        self.data = {}
        self.dictionary = {}

    def _add_token(self, token):
        if not (token in self.dictionary):
            self.dictionary[token] = len(self.dictionary)

    def _add_tokens(self, tokens):
        for tok in tokens:
            if not (tok in self.dictionary):
                self.dictionary[tok] = len(self.dictionary)

    def _tokens2data(self, tokens):
        return list(map(lambda x: self.dictionary[x], tokens))

    def build(self, data_dir):
        for i in range(1, 105):
            data_subdir = data_dir + "/" + str(i)
            for file_name in os.listdir(data_subdir):
                num = int(file_name[:-4])
                name = data_subdir + "/" + file_name
                with open(name, errors="ignore") as f:
                    tokens = token_generator(name)
                    self._add_words(tokens)
                    self.data[(i, num)] = self._tokens2data(tokens)
            print("Directory {} built".format(i))

        print("Token Size: {}".format(len(self.dictionary)))

    def save(self, dst="model/tokens"):
        with open(dst, "wb") as f:
            pickle.dump({"data": self.data, "dictionary": self.dictionary}, f, protocol=4)
    
    def load(self, src="model/tokens"):
        with open(src, "rb") as f:
            obj = pickle.load(f)
            self.data = obj["data"]
            self.dictionary = obj["dictionary"]

if __name__ == "__main__":
    token_sequence = TokenSequence()
    token_sequence.build("../ProgramData")
    