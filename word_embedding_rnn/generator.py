import random
from word_embedding_rnn.word_sequence import WordSequence
from word_embedding_rnn.word_embedding import WordEmbedding


class Generator:
    def __init__(self):
        self.word_sequence = WordSequence()
        self.word_sequence.load()
        self.word_embedding = WordEmbedding(len(self.word_sequence.dictionary))
        self.word_embedding.load()

        self.nums = [[] for _ in range(104)]
        for (cls, num) in self.word_sequence.data:
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
        data = []
        label = []
        cls = random.randrange(0, 104)
        num = random.choice(self.trains[cls]) if train else random.choice(self.tests[cls])
        l = list(map(lambda x: self.word_embedding.predict(x), self.word_sequence.data[(cls + 1, num)]))
        h = [0] * 104
        h[cls] = 1
        data.append(l)
        label.append(h)
        return data, label
