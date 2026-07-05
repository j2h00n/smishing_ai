import pickle
import numpy as np

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences


# 모델 불러오기
model = load_model("smishing_ai_model.h5")

# 토크나이저 불러오기
with open("tokenizer.pickle", "rb") as f:
    tokenizer = pickle.load(f)


levels = [
    "매우 안전",
    "안전",
    "보통",
    "위험",
    "매우 위험"
]


while True:

    print("\n==============================")
    text = input("문자 입력 (종료=q) : ")

    if text.lower() == "q":
        break

    seq = tokenizer.texts_to_sequences([text])

    padded = pad_sequences(
        seq,
        maxlen=30,
        padding="post"
    )

    pred = model.predict(
        padded,
        verbose=0
    )[0]

    best_index = np.argmax(pred)

    print("\n===== 분석 결과 =====")

    print(
        "최종 위험도 :",
        levels[best_index]
    )

    print(
        "AI 신뢰도 :",
        round(
            pred[best_index] * 100,
            2
        ),
        "%"
    )

    print("\n5단계 확률")

    for i in range(5):

        print(
            levels[i],
            ":",
            round(
                pred[i] * 100,
                2
            ),
            "%"
        )