import pickle
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from feature_extractor import extract_features

# ==========================
# 1. 모델 및 토크나이저 불러오기
# ==========================
try:
    model = load_model("smishing_ai_final/smishing_ai_v2 backup/smishing_ai_combined.keras")
    with open("smishing_ai_final/smishing_ai_v2 backup/tokenizer_v2.pickle", "rb") as f:
        tokenizer = pickle.load(f)
except Exception as e:
    print(f"🚨 파일을 불러오는 데 실패했습니다. 먼저 train_ai_v2.py를 실행했는지 확인하세요.\n에러: {e}")
    exit()

# UI 대시보드와 일치하는 항목 및 가중치 (합산 100)
categories = [
    "URL 위험도",
    "발신자 신뢰도",
    "문자 내용 위험도",
    "키워드 탐지",
    "URL 구조 분석"
]
weights = [30, 20, 20, 15, 15]

# ==========================
# 2. 예측 시작
# ==========================
while True:
    text = input("\n📩 문자 내용 입력 (종료하려면 'q' 입력) : ")
    if text.lower() == "q":
        print("프로그램을 종료합니다.")
        break

    # 텍스트 변환 (Tokenizer)
    sequence = tokenizer.texts_to_sequences([text])
    text_input = pad_sequences(sequence, maxlen=30, padding="post")
    
    # 특징 추출 (Feature Extractor)
    feature = extract_features(text)
    feature_input = np.array([feature], dtype=np.float32)

    # AI 예측 수행 (5개의 독립적 확률 도출)
    prediction = model.predict([text_input, feature_input], verbose=0)[0]

    # ==========================
    # 3. 결과 출력 및 가중치 계산
    # ==========================
    print("\n=======================================================")
    print(f"{'분석 항목':<15} | {'AI 판단 확률':<10} | {'가중치':<6} | {'위험도 기여'}")
    print("-------------------------------------------------------")

    total_risk_score = 0
    for i in range(5):
        ai_prob = prediction[i]                # 0 ~ 1 사이의 확률
        weight = weights[i]                    # 할당된 가중치
        contribution = ai_prob * weight        # 획득 점수
        total_risk_score += contribution

        print(f"{categories[i]:<15} | {ai_prob * 100:>8.1f}% | {weight:<6} | {contribution:>5.1f}점")

    print("-------------------------------------------------------")
    print(f"최종 위험 점수                                    | {total_risk_score:.1f} / 100")
    
    # 점수에 따른 등급 분류
    if total_risk_score >= 80:
        result_label = "🚨 매우 위험 (스미싱 확정)"
    elif total_risk_score >= 60:
        result_label = "⚠️ 위험 (주의 요망)"
    elif total_risk_score >= 40:
        result_label = "🟡 보통 (확인 필요)"
    elif total_risk_score >= 20:
        result_label = "🟢 안전"
    else:
        result_label = "✅ 매우 안전"

    print(f"최종 판정 결과                                    | {result_label}")
    print("=======================================================\n")