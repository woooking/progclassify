import os
import pickle
import sys
sys.path.append("..")
from util.util import comment_remover

def token_generator(file):
    fopen = open(file, errors="ignore")
    str = fopen.read()
    str = comment_remover(str)
    str = io.StringIO(str)
    try:
        tokens = list(tokenize.generate_tokens(str.readline))
    except IndentationError:
        print("IndentationErrot in Original Cpp File")
        return []
    return tokens
    
class TokenSequence:
    def __init__(self):
        self.data = {}
        self.dictionary = {}

    def _add_token(self, token):
        if not (token.string in self.dictionary):
            self.dictionary[token.string] = len(self.dictionary)

    def _add_tokens(self, tokens):
        for tok in tokens:
            if not (tok.string in self.dictionary):
                self.dictionary[tok.string] = len(self.dictionary)

    def _tokens2data(self, tokens):
        return list(map(lambda x: self.dictionary[x], map(lambda y: y.string, tokens)))

    def build(self, data_dir):
        for i in range(1, 105):
            data_subdir = data_dir + "/" + str(i)
            for file_name in os.listdir(data_subdir):
                num = int(file_name[:-4])
                name = data_subdir + "/" + file_name
                with open(name, errors="ignore") as f:
                    tokens = token_generator(name)
                    self._add_tokens(tokens)
                    self.data[(i, num)] = self._tokens2data(tokens)
                    # print(self.data[(i, num)])
            print("Directory {} built".format(i))
        print("Token Size: {}".format(len(self.dictionary)))

    def save(self, dst="../model/tokens"):
        with open(dst, "wb") as f:
            pickle.dump({"data": self.data, "dictionary": self.dictionary}, f, protocol=4)
    
    def load(self, src="../model/tokens"):
        with open(src, "rb") as f:
            obj = pickle.load(f)
            self.data = obj["data"]
            self.dictionary = obj["dictionary"]

'''if __name__ == "__main__":
    tok_seq = TokenSequence()
    tok_seq.build("../ProgramData")
    tok_seq.save()'''
