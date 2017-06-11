import io
import os
import tokenize
import sys
sys.path.append("..")
from util.util import comment_remover

data_dir = "ProgramData"
input_size = 96

class Generator:
    def __init__(self):
        self.nums = [[] for _ in range(104)]
        for i in range(1, 105):
            data_subdir = data_dir + "/" + str(i)
            for file_name in os.listdir(data_subdir):
                num = int(file_name[:-4])
                self.nums[i - 1].append(num)

        self.trains = [None] * 104
        self.tests = [None] * 104

        for i in range(104):
            rand_list = [True] * 400 + [False] * 100
            random.shuffle(rand_list)
            zip_list = list(zip(self.nums[i], rand_list))
            self.trains[i] = list(map(lambda x: x[0], filter(lambda x: x[1], zip_list)))
            self.tests[i] = list(map(lambda x: x[0], filter(lambda x: not x[1], zip_list)))

        self.cache = {}

    def next_batch(self, train):
        data = []
        label = []
        l, cls = self.gen_one(train)
        h = [0] * 104
        h[cls] = 1
        data.append(l)
        label.append(h)
        return data, label

    def gen_one(self, train):
        cls = random.randrange(0, 104)
        num = random.choice(self.trains[cls]) if train else random.choice(self.tests[cls])
        code = self.load_file(cls, num)
        l = list(filter(lambda x: x is not None, map(lambda c: self.one_hot(self.char2id(c)), code)))
        return l, cls

    def test_cases(self):
        for cls in range(104):
            for num in self.tests[cls]:
                code = self.load_file(cls, num)
                l = list(filter(lambda x: x is not None, map(lambda c: self.one_hot(self.char2id(c)), code)))
                h = [0] * 104
                h[cls] = 1
                data = [l]
                label = [h]
                yield data, label

    def load_file(self, cls, num):
        if (cls, num) in self.cache:
            return self.cache[(cls, num)]

        file_name = "{}/{}/{}.txt".format(data_dir, cls + 1, num)
        with open(file_name, errors="ignore") as f:
            code = f.read()
            code = comment_remover(code)
            self.cache[(cls, num)] = code
            return code

    @staticmethod
    def char2id(c):
        if 32 <= ord(c) <= 126:
            return ord(c) - 32
        elif ord(c) == ord("\n"):
            return 95
        elif ord(c) == ord("\t"):
            return None

    @staticmethod
    def one_hot(c):
        if c is None:
            return None

        l = [0] * input_size
        l[c] = 1
        return l

    @staticmethod
    def token_generator(file):
        fopen = open(file, errors="ignore")
        str = fopen.read()
        str = comment_remover(str)
        str = io.StringIO(str)
        tokens = tokenize.generate_tokens(str.readline)
        return tokens