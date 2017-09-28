# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/7/23 下午10:15
# @version: 1.0


import numpy as np
from utils import mat_to_csc

def test_init_dic():
    a = [1,3,5]
    b = [2,4,6]
    a = np.array(a)
    b = np.array(b)

    d = {a:b}
    print d


def test_params(**args):
    print type(args)
    print args


# test_params({a:2,b:4})

from sklearn.feature_selection import VarianceThreshold

X = [[0, 0, 1], [0, 1, 0], [1, 0, 0], [0, 1, 1], [0, 1, 0], [0, 1, 1]]
y = X

y_new = mat_to_csc(X,6,3)
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
X_new = SelectKBest(chi2, k=2).fit_transform(X, y_new)

print X_new
# if __name__ == '__main__':
    # test_init_dic()

__END__ = True

from keras.layers import Embedding

char_embedding_layer = Embedding(len(self.cd.char_index) + 1,
                                 self.cd.EMBEDDING_DIM,
                                 weights=[self.cd.char_embedding_matrix],
                                 embeddings_initializer=initializers.RandomUniform(minval=-0.2, maxval=0.2,
                                                                                   seed=None), trainable=True)

char_static_embedding_layer = Embedding(len(self.cd.char_index) + 1,
                                        self.cd.EMBEDDING_DIM,
                                        weights=[self.cd.char_embedding_matrix],
                                        embeddings_initializer=initializers.RandomUniform(minval=-0.2, maxval=0.2,
                                                                                          seed=None), trainable=False)

word_embedding_layer = Embedding(len(self.cd.word_index) + 1,
                                 self.cd.EMBEDDING_DIM,
                                 weights=[self.cd.word_embedding_matrix],
                                 embeddings_initializer=initializers.RandomUniform(minval=-0.2, maxval=0.2,
                                                                                   seed=None), trainable=True)

word_static_embedding_layer = Embedding(len(self.cd.word_index) + 1,
                                        self.cd.EMBEDDING_DIM,
                                        weights=[self.cd.word_embedding_matrix],
                                        embeddings_initializer=initializers.RandomUniform(minval=-0.2, maxval=0.2,
                                                                                          seed=None), trainable=False)

sequence_inputs = []

sequence_outputs = []

model_outputs = []

for i in range(4):
    document = Input(shape=(self.cd.x_train_list[i].shape[1],), name=inputlabel[i])
    sequence_inputs.append(document)
    if i % 2 == 0:
        doc_embedding = char_embedding_layer(document)
        doc_static_embedding = char_static_embedding_layer(document)

    else:
        doc_embedding = word_embedding_layer(document)
        doc_static_embedding = word_static_embedding_layer(document)
    now_gpu = i % 2
    with tf.device('/gpu:%d' % (now_gpu)):
        for doc_embed in [doc_embedding, doc_static_embedding]:

            # if 1:
            conv_blocks = []
            for sz in range(0, 3):
                conv = Conv1D(filters=num_filters,
                              kernel_size=filter_sizes[sz],
                              padding="valid",
                              activation="relu",
                              strides=1)(doc_embed)
                conv = MaxPooling1D(pool_size=filter_sizes[sz])(conv)
                # conv = Flatten()(conv)
                conv = LSTM(256)(conv)
                conv_blocks.append(conv)

            together = Concatenate(axis=1)(conv_blocks) if len(conv_blocks) > 1 else conv_blocks[0]

            sequence_outputs.append(together)

sequence_outputs = merge(sequence_outputs, mode='concat', concat_axis=-1)

z = Dropout(dropout_prob[1])(z)
model_output = Dense(len(self.cd.label_num_dict), activation="softmax", name=outputlabel[1],
                     activity_regularizer=regularizers.l2(0.0001))(z)

self.model = Model(sequence_inputs, model_output)

print self.model.summary()