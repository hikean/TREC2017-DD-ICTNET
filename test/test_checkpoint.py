# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/7/28 下午9:04
# @version: 1.0

import time
import math
from keras.models import Sequential,load_model
from keras.layers import Dense, Activation
from keras.callbacks import ModelCheckpoint, EarlyStopping, Callback
from keras.metrics import categorical_accuracy


class ZHIHUMetrics(Callback):
    def on_epoch_end(self, batch, logs={}):
        y_pred = np.asarray(self.model.predict(self.validation_data[0]))
        y_true = self.validation_data[1]

        print(y_pred.shape, y_true.shape)

        y_pred = np.argsort(-y_pred)[:, :5]

        y_true_list = []
        for i in range(y_pred.shape[0]):
            y_true_list.append([])

        nozero_row, nozero_col = np.nonzero(y_true)

        for i in range(len(nozero_row)):
            y_true_list[nozero_row[i]].append(nozero_col[i])

        right_label_num = 0
        right_label_at_pos_num = [0, 0, 0, 0, 0]
        sample_num = 0
        all_marked_label_num = 0

        for i in range(len(y_true_list)):
            sample_num += 1
            marked_label_set = set(y_true_list[i])
            all_marked_label_num += len(marked_label_set)
            for pos, label in zip(range(0, min(len(y_pred[i]), 5)), y_pred[i]):
                if label in marked_label_set:
                    right_label_num += 1
                    right_label_at_pos_num[pos] += 1

        precision = 0.0
        for pos, right_num in zip(range(0, 5), right_label_at_pos_num):
            precision += ((right_num / float(sample_num))) / math.log(2.0 + pos)
        recall = float(right_label_num) / all_marked_label_num
        eps = 0.000000000000000001
        print('Recall:', recall)
        print(' Precision:', precision)
        print(' res:', recall * precision / (recall + precision + eps))
        print('')

model = Sequential()
model.add(Dense(units=64, input_dim=4))
model.add(Activation("relu"))
model.add(Dense(units=2))
model.add(Activation("softmax"))
model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])


x_train = [ [1,0,0,1],[1,1,0,0], [1,1,1,0] ]
y_train = [[1,0],[0,1],[0,1] ]

x_test = [ [1,0,1,0],[1,1,0,1] ]

mat = ZHIHUMetrics()

model_dir = "./test_save.model"
mdir = "./model"

print str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())))

def get_time_tag():
    return  str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())))

checkpointer = ModelCheckpoint(filepath=mdir + "/" + "c_lstm_" + get_time_tag() + ".hdf5",
                                       period=1,
                                       verbose=1)
earlystop = EarlyStopping(monitor='val_loss', patience=1, verbose=0, mode='min')

print "fiting..."
model.fit(x_train, y_train, epochs=5, batch_size=1,initial_epoch=0,callbacks=[earlystop, mat, checkpointer])

print "saving..."
model.save(model_dir)


print "loading..."
model = load_model(model_dir)

print "test..."
print model.predict(x_test)

__END__ = True