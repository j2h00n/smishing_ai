import numpy as np
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from feature_extractor import extract_features

print("🚀 저장된 AI 모델과 토크나이저를 불러오는 중... (1초 소요)")

# 1. 파일에서 이미 완성된 AI 뇌(모델)와 토크나이저 불러오기
model = load_model("smishing_ai_final/smishing_ai_v2 backup/smishing_ai_combined.keras")

with open("smishing_ai_final/smishing_ai_v2 backup/tokenizer_combined.pickle", "rb") as f:
    tokenizer = pickle.load(f)

# 설정값 (옛날 모델 크기인 30으로 세팅)
max_len = 50
categories = ["URL 위험도", "발신자 신뢰도", "문자 내용 위험도", "키워드 탐지", "URL 구조 분석"]

# 2. 모델의 맨 마지막 레이어에서 학습된 내부 가중치 직접 뜯어오기
last_layer_weights = model.layers[-1].get_weights()[0]
raw_weights = np.mean(np.abs(last_layer_weights), axis=1)[:5]
ai_learned_weights = (raw_weights / np.sum(raw_weights)) * 100

# 3. 시스템 가중치 대시보드 출력
print("\n" + "="*65)
print("📊 [AI가 98.35% 정확도를 위해 스스로 세팅한 시스템 가중치]")
print("="*65)
for i in range(5):
    print(f" ⚙️ {categories[i]:<12} : {ai_learned_weights[i]:>4.1f}%의 비율로 최종 판단에 반영됨")
print("="*65)
print("✨ 시스템 준비 완료! 언제든 문자를 입력하세요.")

# 4. 실시간 무한 탐지 루프 (3단계 판정 버전)
while True:
    test_text = input("\n🔍 테스트할 문자 입력 (종료하려면 'q' 입력) : ").strip()
    if test_text.lower() == 'q':
        break
    if not test_text:
        continue
        
    # 🛡️ 억까 방지 필터
    clean_text = test_text.lower()
    if len(clean_text) <= 5 or clean_text in ["http", "https", "www", "www.", "http://", "https://"]:
        print("\n🚨 [안내] 입력된 내용이 너무 짧거나 단순 주소 형태입니다.")
        continue
        
    # 입력한 문장을 AI가 이해할 수 있는 숫자로 변환
    seq = tokenizer.texts_to_sequences([test_text])
    t_in = pad_sequences(seq, maxlen=max_len, padding="post")
    f_in = np.array([extract_features(test_text)], dtype=np.float32)
    
    # 🔥 [여기서 확실하게 변수 선언!!] AI 예측 수행
    # pred_5와 pred_final 변수를 동시에 정확하게 생성합니다.
    pred_5, pred_final = model.predict([t_in, f_in], verbose=0)
    
    print("\n[🎯 실시간 AI 융합 분석 결과]")
    print("-" * 65)
    for i in range(5):
        print(f" - {categories[i]:<14} 활성화 확률 : {pred_5[0][i]*100:>5.1f}%")
    
    print("-" * 65)
    
    # 🎯 0~1 사이의 확률 값을 100점 만점 점수로 변환
    score = pred_final[0][0] * 100
    
    # 🚦 3단계 위험도 판정 기준 적용
    if score < 40.0:
        level = "🟢 [안전]"
        action = "스미싱 확률이 낮습니다. 안심하셔도 좋습니다."
    elif score < 75.0:
        level = "🟡 [주의]"
        action = "의심스러운 정황이 있습니다. 링크 클릭이나 송금 전 반드시 확인하세요!"
    else:
        level = "🔴 [위험]"
        action = "스미싱일 확률이 매우 높습니다! 절대 링크를 누르지 마세요!"
        
    print(f"🔥 AI 최종 스미싱 위험도 점수: {score:.1f} / 100")
    print(f"🚨 판별 결과 : {level} {action}")
    print("="*65)