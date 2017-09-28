# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/7/23 上午10:53
# @version: 1.0


from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np


IDS = [5,7,6,9,1,2,3,5]
# IDS = [[5,7],[6,9],[1,3,5],[2,5]]]
label_encoder = MultiLabelBinarizer()

label_encoder.fit(IDS)

print label_encoder.transform([[7,9]])
print label_encoder.inverse_transform(np.array([ [1,0,0,1,0,0,1] ]))


if __name__ == '__main__':
    pass

__END__ = True