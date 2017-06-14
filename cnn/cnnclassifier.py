import os
import sys
sys.path.append('..')

import tensorflow as tf
import numpy as np

from word_embedding_rnn.generator import Generator

import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_1d, global_max_pool
from tflearn.layers.merge_ops import merge
from tflearn.layers.estimator import regression
from tflearn.helpers.trainer import TrainOp, Trainer
from tflearn.helpers.evaluator import Evaluator
#print(tflearn.__path__)

generator = Generator()

maxL = 1000

'''
count = 0
maxLL = 0
trainx = []
for d, l in generator.train_cases():
	if len(d[0]) > 1000:
		count += 1
print(count)
'''

def batch_generator(batch_size, flag):
	instances, labels = [], []
	for _ in range(batch_size):
		data, label = generator.next_batch(flag)
		data = np.array(data[0])
		if len(data) < maxL:
			data = np.lib.pad(data, ((0, maxL - len(data)), (0, 0)), 'constant')
		else:
			data = data[:maxL]
		instances.append(data)
		labels.extend(label)
	return instances, labels


X = input_data(shape=[None, 1000, 128], name='input')
Y = input_data(shape=[None, 104], name='Y')
branch1 = conv_1d(X, 128, 3, padding='valid', activation='relu', regularizer="L2")
branch2 = conv_1d(X, 128, 4, padding='valid', activation='relu', regularizer="L2")
branch3 = conv_1d(X, 128, 5, padding='valid', activation='relu', regularizer="L2")
network = merge([branch1, branch2, branch3], mode='concat', axis=1)
network = tf.expand_dims(network, 2)
network = global_max_pool(network)
network = dropout(network, 0.5)
network = fully_connected(network, 104)

loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=Y, logits=network))
learning_rate = 0.001
optimizer = tf.train.AdamOptimizer(learning_rate).minimize(loss)
correct_prediction = tf.equal(tf.argmax(Y, 1), tf.argmax(network, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
saver = tf.train.Saver()

# Training
#trainop = TrainOp(loss=loss, optimizer=optimizer, metric=accuracy)
#model = Trainer(train_ops=trainop, tensorboard_verbose=0)
def test(restore=False, sess=None):
	if restore:
		sess = tf.Session()
		saver.restore(sess, "../model/word_embedding_cnn")
	result = 0.0
	num = 0
	for d, l in generator.test_cases():
		testX, testY = [], []
		data = np.array(d[0])
		if len(data) < maxL:
			data = np.lib.pad(data, ((0, maxL - len(data)), (0, 0)), 'constant')
		else:
			data = data[:maxL]
		testX.append(data)
		testY.extend(l)
		result += accuracy.eval(session=sess, feed_dict={X: testX, Y: testY})
		num += 1
		if num % 100 == 0:
			print(num, result / num)
	print("test accuracy: {}".format(result / num))
	return result / num


def train():
	with tf.Session() as sess:
		tf.global_variables_initializer().run()
		maxAcc = 0.97
		for _ in range(20001):
			trainX, trainY = batch_generator(64, True)
			res = sess.run([optimizer, loss], feed_dict={X: trainX, Y: trainY})
			#val = model.fit_batch(feed_dicts={X: trainX, Y: trainY})
			if _ % 10 == 0:
				print("loss: {}".format(res[1]))
			if _ % 100 == 0:
				testX, testY = batch_generator(200, False)
				print("accuracy: {}".format(accuracy.eval(feed_dict={X: testX, Y: testY})))
			if _ % 1000 == 0 and _ != 0:
				acc = test(sess=sess)
				if acc > maxAcc:
					maxAcc = acc
					saver.save(sess, "../model/word_embedding_cnn")

if __name__ == '__main__':
	#train()
	test(restore=True)