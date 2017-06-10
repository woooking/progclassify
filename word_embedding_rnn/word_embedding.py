import math
import pickle
import collections
import tensorflow as tf
import numpy as np
from config import wordembedding_rnn_config
from word_embedding_rnn.word_sequence import WordSequence

batch_size = wordembedding_rnn_config["batch_size"]
embedding_size = wordembedding_rnn_config["embedding_size"]
window_size = wordembedding_rnn_config["window_size"]
num_sampled = wordembedding_rnn_config["number_sampled"]


def pair_generator(data):
    while True:
        for (cls, num) in data:
            value = data[(cls, num)]
            data_index = 0
            span = 2 * window_size + 1
            buffer = collections.deque(maxlen=span)
            for _ in range(span):
                buffer.append(value[data_index])
                data_index += 1
            while data_index < len(value):
                for i in range(span):
                    if i == window_size:
                        continue
                    yield (buffer[window_size], buffer[i])
                buffer.append(value[data_index])
                data_index += 1


def batch_generator(data):
    generator = pair_generator(data)
    while True:
        batch = np.ndarray(shape=batch_size, dtype=np.int32)
        labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
        for i in range(batch_size):
            batch[i], labels[i, 0] = next(generator)
        yield batch, labels


class WordEmbedding:
    def __init__(self, vocabulary_size):
        self.train_inputs = tf.placeholder(tf.int32, shape=[batch_size])
        self.train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])

        self.embeddings = tf.Variable(tf.random_uniform([vocabulary_size, embedding_size], -1.0, 1.0))
        self.embed = tf.nn.embedding_lookup(self.embeddings, self.train_inputs)

        self.nce_weights = tf.Variable(tf.truncated_normal([vocabulary_size, embedding_size], stddev=1.0 / math.sqrt(embedding_size)))
        self.nce_biases = tf.Variable(tf.zeros([vocabulary_size]))

        self.loss = tf.reduce_mean(
            tf.nn.nce_loss(weights=self.nce_weights,
                           biases=self.nce_biases,
                           labels=self.train_labels,
                           inputs=self.embed,
                           num_sampled=num_sampled,
                           num_classes=vocabulary_size)
        )

        self.optimizer = tf.train.GradientDescentOptimizer(0.1).minimize(self.loss)

        self.norm = tf.sqrt(tf.reduce_sum(tf.square(self.embeddings), 1, keep_dims=True))
        self.normalized_embeddings = self.embeddings / self.norm

        self.init = tf.global_variables_initializer()

        self.saver = tf.train.Saver()

        self.final_embeddings = None

    def train(self, data, num_steps):
        generator = batch_generator(data)

        with tf.Session() as sess:
            self.init.run()
            print("Initialized")

            average_loss = 0
            for step in range(num_steps):
                batch_inputs, batch_labels = next(generator)
                feed_dict = {self.train_inputs: batch_inputs, self.train_labels: batch_labels}

                _, loss_val = sess.run([self.optimizer, self.loss], feed_dict=feed_dict)
                average_loss += loss_val

                if step % 2000 == 0:
                    if step > 0:
                        average_loss /= 2000
                    print("Average loss at step ", step, ": ", average_loss)
                    average_loss = 0
            self.final_embeddings = self.normalized_embeddings.eval()
            with open("model/word_embedding", "wb") as f:
                pickle.dump(self.final_embeddings, f)

    def load(self):
        with open("model/word_embedding", "rb") as f:
            self.final_embeddings = pickle.load(f)

    def predict(self, num):
        if self.final_embeddings is None:
            print("Please train or load the model first")
            raise RuntimeError()
        return self.final_embeddings[num]


if __name__ == "__main__":
    word_sequence = WordSequence()
    word_sequence.load()
    word_embedding = WordEmbedding(len(word_sequence.dictionary))
    word_embedding.train(word_sequence.data, wordembedding_rnn_config["word_embedding_steps"])
