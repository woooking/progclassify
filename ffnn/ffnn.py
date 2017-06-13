import tensorflow as tf
import sys

sys.path.append('..')

from word_embedding_rnn.generator import Generator
import numpy as np

generator = Generator()

maxL = 128 * 500
'''
count = 0
for data, label in generator.test_cases():
	if len(data[0]) > 1000:
		count += 1
for data, label in generator.train_cases():
	if len(data[0]) > 1000:
		count += 1
print(count)
'''
def batch_generator(batch_size, flag):
	data, labels = [], []
	for _ in range(batch_size):
		instance, label = generator.next_batch(flag)
		instance = np.array(instance[0])
		flat = instance[np.where( instance != 0)]
		#print(len(flat))
		#print(instance)
		#print(np.lib.pad(instance, (0, maxL - len(instance)), 'constant'))
		if len(flat) < maxL:
			#print(np.lib.pad(instance[0], (0, maxL - len(instance[0])), 'constant')[0])
			data.append(np.lib.pad(flat, (0, maxL - len(flat)), 'constant'))
			#print(len(data[-1]))
		else:
			data.append(flat[:maxL])
		labels.extend(label)

	return data, labels


def init(shape, stddev = 0.0):
	return tf.Variable(tf.random_normal(shape, stddev=stddev))
		

def model(X, w0, w1, b0, b1, p_drop):
	X = tf.nn.dropout(X, p_drop)
	h0 = tf.nn.relu(tf.matmul(X, w0) + b0)
	h0 = tf.nn.dropout(h0, p_drop)
	return tf.matmul(h0, w1) + b1


X = tf.placeholder(tf.float32, [None, maxL])
Y = tf.placeholder(tf.float32, [None, 104])

point_num1 = 5000

w0 = init([maxL, point_num1], 0.01)
w1 = init([point_num1, 104], 0.01)

b0 = init([point_num1])
b1 = init([104])

p_drop = tf.placeholder(tf.float32)

m = model(X, w0, w1, b0, b1, p_drop)
loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=Y, logits=m))
learning_rate = 0.001
train_step = tf.train.AdamOptimizer(learning_rate).minimize(loss)
correct_prediction = tf.equal(tf.argmax(Y,1), tf.argmax(m, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
saver = tf.train.Saver()


def train():
	with tf.Session() as sess:
		tf.global_variables_initializer().run()
		for _ in range(100000):
			batch_xs, batch_ys = batch_generator(32, True)
			#print(batch_xs)
			#print(batch_ys)
			res = sess.run([train_step, loss], feed_dict={X: batch_xs, Y: batch_ys, p_drop: 0.8})
			if _ % 20 == 0:
				print(res[1])
				testX, testY = batch_generator(200, False)
				print(accuracy.eval(feed_dict={X: testX, Y: testY,  p_drop: 1.0}))
			#saver.save(sess, "../model/word_embedding_ffnn")
			if _ % 10000 == 0 and _ != 0:
				#saver.save(sess, "../model/word_embedding_ffnn")
				result = 0.0
				num = 0
				for d, l in generator.test_cases():
					testX, testY = [], []
					flat = np.array(d[0]).flatten()
					if len(flat) < maxL:
						testX.append(np.lib.pad(flat, (0, maxL - len(flat)), 'constant'))
					else:
						testX.append(flat[:maxL])
					testY.extend(l)
					result += accuracy.eval(feed_dict={X: testX, Y: testY,  p_drop: 1.0})
					num += 1
					if num % 100 == 0:
						print(num, result / num)
				print("test accuracy: {}".format(result / num))


def test():
	with tf.Session() as sess:
		saver.restore(sess, "../model/word_embedding_ffnn")
		result, num = 0.0, 0
		for d, l in generator.test_cases():
			testX, testY = [], []
			flat = np.array(d[0]).flatten()
			if len(flat) < maxL:
				testX.append(np.lib.pad(flat, (0, maxL - len(flat)), 'constant'))
			else:
				testX.append(flat[:maxL])
			testY.extend(l)
			result += accuracy.eval(feed_dict={X: testX, Y: testY,  p_drop: 1.0})
			num += 1
			if num % 100 == 0:
				print(num, result / num)
		print("test accuracy: {}".format(result / num))


if __name__ == '__main__':
	train()
	#test()