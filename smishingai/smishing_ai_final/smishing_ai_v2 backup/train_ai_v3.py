import pandas as pd
import numpy as np
import pickle
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
# 1. 데이터 로드 및 전처리
# ==========================================
file_name = "smishing_ai_final/smishing_ai_v2 backup/labeled_presentation_dataset.csv"  # 👈 라벨러가 뱉은 파일명으로 맞춰주세요!
print(f"📦 [{file_name}] 데이터를 불러오는 중...")

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

# 💡 [조정] 영어 문장은 한글보다 길기 때문에 maxlen을 30에서 50으로 확장합니다.
max_len = 50
X_text = pad_sequences(tokenizer.texts_to_sequences(texts), maxlen=max_len, padding="post")

print("🔮 텍스트 특징(X_feature)을 추출하는 중... (시간이 조금 걸릴 수 있습니다)")
X_feature = np.array([extract_features(t) for t in texts], dtype=np.float32)

# 토크나이저 저장
with open("tokenizer_combined.pickle", "wb") as f:
    pickle.dump(tokenizer, f)

# Train / Test 분할
X_t_train, X_t_test, X_f_train, X_f_test, y5_train, y5_test, yf_train, yf_test = train_test_split(
    X_text, X_feature, y_5_categories, y_final, test_size=0.2, random_state=42
)

# ==========================================
# 2. 대용량/다국어 맞춤형 AI 모델 설계 (Multi-Task)
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
out_final = Dense(1, activation="sigmoid", name="out_final")(z)

model = Model(inputs=[text_input, feature_input], outputs=[out_5, out_final])

# 최종 정답(out_final) 예측에 가중치 2.0을 주어 더 집중하게 만듭니다.
model.compile(
    loss={"out_5": "binary_crossentropy", "out_final": "binary_crossentropy"},
    loss_weights={"out_5": 1.0, "out_final": 2.0},
    optimizer=Adam(learning_rate=0.0002), # 데이터가 많아졌으므로 보폭을 살짝 늘림 (0.0001 -> 0.0002)
    metrics=["accuracy"]
)

# ==========================================
# 3. AI 스마트 학습 시작 (EarlyStopping)
# ==========================================
print("\n🤖 [대용량 데이터 모드] 스스로 가중치를 찾아가는 딥러닝 학습을 시작합니다...")
# patience=3으로 설정하여 검증 오차가 3번 연속 악화되면 과적합으로 판단하고 자동 멈춤
early_stop = EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)

history = model.fit(
    [X_t_train, X_f_train], 
    {"out_5": y5_train, "out_final": yf_train},
    epochs=50, 
    batch_size=8,  # 데이터가 많으므로 배치를 4에서 8로 상향
    callbacks=[early_stop],
    validation_data=([X_t_test, X_f_test], {"out_5": y5_test, "out_final": yf_test}),
    verbose=1
)

model.save("smishing_ai_final/smishing_ai_v2 backup/smishing_ai_combined.keras")
print("\n✅ 학습 및 모델 저장 완료! 이제 진정한 인공지능이 완성되었습니다.")

# ==========================================
# 4. 실시간 탐지 테스트 모드
# ==========================================
categories = ["URL 위험도", "발신자 신뢰도", "문자 내용 위험도", "키워드 탐지", "URL 구조 분석"]

while True:
    test_text = input("\n🔍 테스트할 문자 입력 (종료하려면 'q' 입력) : ").strip()
    if test_text.lower() == 'q':
        break
    if not test_text:
        continue
        
    # 🛡️ 억까 방지 필터 (텍스트 전처리)
    clean_text = test_text.lower()
    if len(clean_text) <= 5 or clean_text in ["http", "https", "www", "www.", "http://", "https://"]:
        print("\n🚨 [안내] 입력된 내용이 너무 짧거나 단순 주소 형태입니다. (분석 제외)")
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