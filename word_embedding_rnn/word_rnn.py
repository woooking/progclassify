import tensorflow as tf

from word_embedding_rnn.generator import Generator
from util.util import new_variable
from config import wordembedding_rnn_config

input_size = wordembedding_rnn_config["embedding_size"]
hidden_size = wordembedding_rnn_config["rnn_hidden_size"]


class WordRNN:
    def __init__(self):
        self.input = tf.placeholder(tf.float32, [1, None, input_size])
        self.label = tf.placeholder(tf.float32, [1, 104])
        self.lstm = tf.contrib.rnn.BasicLSTMCell(hidden_size)
        self.state = self.lstm.zero_state(1, tf.float32)

        self.w = new_variable([hidden_size, 104])
        self.b = new_variable([104])

        self.outputs, self.last_state = tf.nn.dynamic_rnn(cell=self.lstm, inputs=self.x, dtype=tf.float32)
        self.s = tf.shape(self.outputs)
        output = tf.reshape(tf.slice(self.outputs, [0, s[1] - 1, 0], [-1, -1, -1]), [1, hidden_size])

        self.logits = tf.matmul(output, self.w) + self.b

        self.cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=self.label, logits=self.logits))
        self.train_step = tf.train.AdamOptimizer(1e-4).minimize(self.cross_entropy)
        self.correct_prediction = tf.equal(tf.argmax(self.logits, 1), tf.argmax(self.label, 1))
        self.accuracy = tf.reduce_mean(tf.cast(self.correct_prediction, tf.float32))

        self.init = tf.global_variables_initializer()

    def train(self):
        generator = BatchGenerator(batch_size)
        with tf.Session() as sess:
            sess.run(self.init)

            for i in range(10000):
                for _ in range(50):
                    data, label = generator.next_batch(True)
                    self.train_step.run(feed_dict={self.input: data, self.label: label})
                if i % 20 == 0:
                    print("===== train step {} =====".format(i))
                    run_test()


def run_test():
    result = 0
    for _ in range(200):
        data, label = generator.next_batch(False)
        result += accuracy.eval(feed_dict={x: data, y: label})
    print("test accuracy: {}".format(result / 200))


