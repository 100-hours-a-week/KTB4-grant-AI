"""## 1. 가상 데이터셋을 생성한 뒤, 학습·검증·테스트 데이터셋으로 분할해 보세요."""

import numpy as np
from sklearn.model_selection import train_test_split


dummy_inps = np.random.rand(1000, 3, 224, 224) # 224x224 이미지 1000장

train_ratio = .8
val_ratio = .1
test_ratio = .1
train, eval = train_test_split(dummy_inps, train_size=train_ratio)
val, test = train_test_split(eval, test_size=.5)

print(train.shape, val.shape, test.shape)