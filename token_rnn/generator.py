import random
from token_sequence import TokenSequence
from token_embedding import TokenEmbedding

class Generator:
    def __init__(self):
        self.token_sequence = TokenSequence()
        self.token_sequence.load()
        self.token_embedding = TokenEmbedding(len(self.token_sequence.dictionary))
        self.token_embedding.load()

        self.nums = [[] for _ in range(104)]
        for (cls, num) in self.token_sequence.data:
            self.nums[cls - 1].append(num)

        self.trains = [None] * 104
        self.tests = [None] * 104

        for i in range(104):
            rand_list = [True] * 400 + [False] * 100
            random.shuffle(rand_list)
            zip_list = list(zip(self.nums[i], rand_list))
            self.trains[i] = list(map(lambda x: x[0], filter(lambda x: x[1], zip_list)))
            self.tests[i] = list(map(lambda x: x[0], filter(lambda x: not x[1], zip_list)))

    def next_batch(self, train):
        cls = random.randrange(0, 104)
        num = random.choice(self.trains[cls]) if train else random.choice(self.tests[cls])
        l = list(map(lambda x: self.token_embedding.predict(x), self.token_sequence.data[(cls + 1, num)]))
        h = [0] * 104
        h[cls] = 1
        data = [l]
        label = [h]
        return data, label

    def test_cases(self):
        for cls in range(104):
            for num in self.tests[cls]:
                l = list(map(lambda x: self.token_embedding.predict(x), self.token_sequence.data[(cls + 1, num)]))
                h = [0] * 104
                h[cls] = 1
                data = [l]
                label = [h]
                yield data, label
                