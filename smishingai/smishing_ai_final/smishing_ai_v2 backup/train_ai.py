import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# CSV 읽기
data = pd.read_csv("friend_data.csv")

texts = data["text"].astype(str).tolist()
labels = data["label"].tolist()

print("데이터 개수:", len(texts))

# 토크나이저 생성
tokenizer = Tokenizer(
    num_words=5000,
    oov_token="<OOV>"
)

tokenizer.fit_on_texts(texts)

# 문장을 숫자로 변환
sequences = tokenizer.texts_to_sequences(texts)

# 길이 맞추기
X = pad_sequences(
    sequences,
    maxlen=30,
    padding="post"
)

y = np.array(labels)

print("입력 데이터 형태:", X.shape)
print("라벨 데이터 형태:", y.shape)

# 저장
with open("tokenizer.pickle", "wb") as f:
    pickle.dump(tokenizer, f)

print("tokenizer.pickle 저장 완료")
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# 학습용 / 테스트용 분리
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# 모델 생성
model = Sequential()

model.add(
    Embedding(
        input_dim=5000,
        output_dim=64,
        input_length=30
    )
)

model.add(
    LSTM(
        64,
        return_sequences=False
    )
)

model.add(
    Dropout(
        0.3
    )
)

model.add(
    Dense(
        32,
        activation="relu"
    )
)

model.add(
    Dense(
        5,
        activation="softmax"
    )
)

# 컴파일
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# 과적합 방지
early_stop = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)

print("\nAI 학습 시작...\n")

history = model.fit(
    X_train,
    y_train,
    validation_split=0.2,
    epochs=50,
    batch_size=4,
    callbacks=[early_stop],
    verbose=1
)

print("\n학습 완료\n")

# 평가
loss, acc = model.evaluate(
    X_test,
    y_test,
    verbose=0
)

print("테스트 정확도:", round(acc * 100, 2), "%")

# 모델 저장
model.save(
    "smishing_ai_model.h5"
)

print("smishing_ai_model.h5 저장 완료")