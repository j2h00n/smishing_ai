import pandas as pd
import numpy as np
import pickle
import tensorflow as tf
import tensorflow.keras.backend as K
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Dropout, Concatenate
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2
from feature_extractor import extract_features

# ==========================================
# 1. 차원 억까를 원천 차단하는 무적의 F2 수식
# ==========================================
def f2_score(y_true, y_pred):
    # 입력이 1D든 2D든 무조건 일렬(1차원)로 펴서 타입을 맞춤
    y_true = tf.cast(tf.reshape(y_true, [-1]), tf.float32)
    y_pred = tf.cast(tf.reshape(tf.round(y_pred), [-1]), tf.float32)
    
    tp = tf.reduce_sum(y_true * y_pred)
    fp = tf.reduce_sum((1.0 - y_true) * y_pred)
    fn = tf.reduce_sum(y_true * (1.0 - y_pred))
    
    p = tp / (tp + fp + K.epsilon())
    r = tp / (tp + fn + K.epsilon())
    
    return 5.0 * (p * r) / (4.0 * p + r + K.epsilon())

# ==========================================
# 2. 데이터 로드 및 전처리
# ==========================================
file_name = "smishingai/smishing_ai_final/smishing_ai_v2 backup/labeled_presentation_dataset.csv"
print(f" 📂 [{file_name}] 데이터를 불러오는 중...")

data = pd.read_csv(file_name, encoding="utf-8-sig")

# 출력 1: 5가지 세부 카테고리 (라벨러가 만든 컬럼들)
required_cols = ["url_risk", "sender_risk", "content_risk", "keyword_risk", "url_struct"]
y_5_categories = data[required_cols].values.astype(np.float32)

# 출력 2: 최종 정답 (새 데이터셋은 이미 0과 1이므로 전처리 없이 바로 사용)
y_final = pd.to_numeric(data['label']).values.astype(np.float32)

# 텍스트 데이터 토큰화
texts = data["text"].astype(str).tolist()
tokenizer = Tokenizer(num_words=5000, oov_token="<OOV>")
tokenizer.fit_on_texts(texts)

max_len = 50
X_text = pad_sequences(tokenizer.texts_to_sequences(texts), maxlen=max_len, padding="post")

print(" ⚙️ 텍스트 특징(X_feature)을 추출하는 중... (시간이 조금 걸릴 수 있습니다)")
X_feature = np.array([extract_features(t) for t in texts], dtype=np.float32)

# 토크나이저 저장
with open("smishingai/smishing_ai_final/smishing_ai_v2 backup/tokenizer_combined.pickle", "wb") as f:
    pickle.dump(tokenizer, f)

# Train / Test 분할
X_t_train, X_t_test, X_f_train, X_f_test, y5_train, y5_test, yf_train, yf_test = train_test_split(
    X_text, X_feature, y_5_categories, y_final, test_size=0.2, random_state=42
)

# 🌟 [수정 수순 1] 최종 출력 데이터를 완벽한 2차원(batch_size, 1) 형태로 사전 변환
yf_train_2d = np.array(yf_train).reshape(-1, 1)
yf_test_2d = np.array(yf_test).reshape(-1, 1)

# ==========================================
# 3. 대용량/다국어 맞춤형 AI 모델 설계 (Multi-Task)
# ==========================================
# 텍스트 입력 처리층
text_input = Input(shape=(max_len,), name="text_input")
x1 = Embedding(5000, 32)(text_input)
x1 = LSTM(32, kernel_regularizer=l2(0.005))(x1)  # 과적합 방지용 L2 규제 적용
x1 = Dropout(0.4)(x1)

# 구조적 특징 입력 처리층
feature_input = Input(shape=(X_feature.shape[1],), name="feature_input")
x2 = Dense(32, activation="relu", kernel_regularizer=l2(0.005))(feature_input)
x2 = Dropout(0.4)(x2)

# 두 신경망 결합
combined = Concatenate()([x1, x2])
z = Dense(32, activation="relu", kernel_regularizer=l2(0.005))(combined)
z = Dropout(0.3)(z)

# [출력 1] 5가지 세부 분석 결과
out_5 = Dense(5, activation="sigmoid", name="out_5")(z)

# [출력 2] 최종 스미싱 여부 (우리가 가장 중요하게 여길 메인 타깃)
out_final = Dense(1, activation="sigmoid", name="out_final")(out_5) 

model = Model(inputs=[text_input, feature_input], outputs=[out_5, out_final])

# 🌟 [수정 수순 2] 컴파일 메트릭을 'accuracy' 대신 'binary_accuracy'로 원천 교정
model.compile(
    loss={"out_5": "binary_crossentropy", "out_final": "binary_crossentropy"},
    loss_weights={"out_5": 1.0, "out_final": 2.0},
    optimizer=Adam(learning_rate=0.0002), 
    metrics={'out_5': 'binary_accuracy', "out_final": f2_score}
)

# ==========================================
# 4. AI 스마트 학습 시작 (EarlyStopping)
# ==========================================
print("\n 🚀 [대용량 데이터 모드] 스스로 가중치를 찾아가는 딥러닝 학습을 시작합니다...")
early_stop = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)

# 🌟 [수정 수순 3] 사전에 정제해 둔 2D 변환 타깃 데이터(yf_train_2d) 투입
history = model.fit(
    [X_t_train, X_f_train], 
    {"out_5": y5_train, "out_final": yf_train_2d}, 
    epochs=50, 
    batch_size=8, 
    callbacks=[early_stop],
    validation_data=([X_t_test, X_f_test], {"out_5": y5_test, "out_final": yf_test_2d}), 
    verbose=1
)

model.save("smishingai/smishing_ai_final/smishing_ai_v2 backup/smishing_ai_combined.keras")
print("\n 🎉 학습 및 모델 저장 완료! 이제 인공지능이 완성되었습니다.")

# ==========================================
# 5. 실시간 탐지 테스트 모드
# ==========================================
categories = ["URL 위험도", "발신자 신뢰도", "문자 내용 위험도", "키워드 탐지", "URL 구조 분석"]

while True:
    test_text = input("\n🔍 테스트할 문자 입력 (종료하려면 'q' 입력) : ").strip()
    if test_text.lower() == 'q':
        break
    if not test_text:
        continue
        
    # 데이터 변환
    seq = tokenizer.texts_to_sequences([test_text])
    t_in = pad_sequences(seq, maxlen=max_len, padding="post")
    f_in = np.array([extract_features(test_text)], dtype=np.float32)
    
    # 예측 수행
    pred_5, pred_final = model.predict([t_in, f_in], verbose=0)
    
    print("\n[🎯 AI 융합 분석 결과]")
    for i in range(5):
        print(f" - {categories[i]:<15} : {pred_5[0][i]*100:>5.1f}%")
    
    print("-" * 50)
    print(f"🔥 AI가 빅데이터를 바탕으로 내린 최종 스미싱 확률: {pred_final[0][0]*100:.1f} / 100")