import tensorflow as tf

from rnn.generator import BatchGenerator


def new_variable(shape):
    return tf.Variable(tf.random_normal(shape))


input_size = 96
hidden_size = 100
batch_size = 1

x = tf.placeholder(tf.float32, [batch_size, None, input_size])
y = tf.placeholder(tf.float32, [batch_size, 104])

lstm = tf.contrib.rnn.BasicLSTMCell(hidden_size)
state = lstm.zero_state(batch_size, tf.float32)

w = new_variable([hidden_size, 104])
b = new_variable([104])

outputs, last_state = tf.nn.dynamic_rnn(cell=lstm, inputs=x, dtype=tf.float32)
s = tf.shape(outputs)
output = tf.reshape(tf.slice(outputs, [0, s[1] - 1, 0], [-1, -1, -1]), [batch_size, hidden_size])

logits = tf.matmul(output, w) + b

cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=logits))
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
correct_prediction = tf.equal(tf.argmax(logits, 1), tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

init = tf.global_variables_initializer()

generator = BatchGenerator(batch_size)


def run_test():
    result = 0
    for _ in range(200):
        data, label = generator.next_batch(False)
        result += accuracy.eval(feed_dict={x: data, y: label})
    print("test accuracy: {}".format(result / 200))


with tf.Session() as sess:
    sess.run(init)

    for i in range(10000):
        for _ in range(50):
            data, label = generator.next_batch(True)
            train_step.run(feed_dict={x: data, y: label})
        if i % 20 == 0:
            print("===== train step {} =====".format(i))
            run_test()
