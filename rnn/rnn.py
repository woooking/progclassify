import tensorflow as tf

from rnn.generator import Generator
from util.util import new_variable
from config import rnn_config

input_size = rnn_config["input_size"]
hidden_size = rnn_config["hidden_size"]


class RNN:
    def __init__(self):
        self.input = tf.placeholder(tf.float32, [1, None, input_size])
        self.label = tf.placeholder(tf.float32, [1, 104])
        self.lstm = tf.contrib.rnn.BasicLSTMCell(hidden_size)
        self.state = self.lstm.zero_state(1, tf.float32)

        self.w = new_variable([hidden_size, 104])
        self.b = new_variable([104])

        self.outputs, self.last_state = tf.nn.dynamic_rnn(cell=self.lstm, inputs=self.x, dtype=tf.float32)
        self.s = tf.shape(self.outputs)
        self.output = tf.reshape(tf.slice(self.outputs, [0, self.s[1] - 1, 0], [-1, -1, -1]), [1, hidden_size])

        self.logits = tf.matmul(self.output, self.w) + self.b

        self.cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=self.label, logits=self.logits))
        self.train_step = tf.train.AdamOptimizer(1e-4).minimize(self.cross_entropy)
        self.correct_prediction = tf.equal(tf.argmax(self.logits, 1), tf.argmax(self.label, 1))
        self.accuracy = tf.reduce_mean(tf.cast(self.correct_prediction, tf.float32))

        self.init = tf.global_variables_initializer()

        self.saver = tf.train.Saver()

        self.generator = Generator()

    def train(self):
        with tf.Session() as sess:
            sess.run(self.init)

            for i in range(10000):
                for _ in range(50):
                    data, label = self.generator.next_batch(True)
                    self.train_step.run(feed_dict={self.input: data, self.label: label})
                if i % 20 == 0:
                    print("===== train step {} =====".format(i))
                    self.run_test()
            self.saver.save(sess, "model/rnn")

    def test(self):
        with tf.Session() as sess:
            self.saver.restore(sess, "model/rnn")
            result = 0
            num = 0
            for data, label in self.generator.test_cases():
                result += self.accuracy.eval(feed_dict={self.input: data, self.label: label})
                num += 1
            print("Result {} / {}, Accuracy: {}".format(num, result, result / num))

    def run_test(self):
        result = 0
        for _ in range(200):
            data, label = self.generator.next_batch(False)
            result += self.accuracy.eval(feed_dict={x: data, y: label})
        print("test accuracy: {}".format(result / 200))



