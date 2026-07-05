import numpy as np
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from feature_extractor import extract_features
import tensorflow as tf
import tensorflow.keras.backend as K
from tensorflow.keras.models import load_model

# 🌟 1. 케라스가 헤매지 않도록 f2_score 수식을 이 파일에도 똑같이 얹어줍니다.
def f2_score(y_true, y_pred):
    y_true = tf.cast(tf.reshape(y_true, [-1]), tf.float32)
    y_pred = tf.cast(tf.reshape(tf.round(y_pred), [-1]), tf.float32)
    
    tp = tf.reduce_sum(y_true * y_pred)
    fp = tf.reduce_sum((1.0 - y_true) * y_pred)
    fn = tf.reduce_sum(y_true * (1.0 - y_pred))
    
    p = tp / (tp + fp + K.epsilon())
    r = tp / (tp + fn + K.epsilon())
    
    return 5.0 * (p * r) / (4.0 * p + r + K.epsilon())

print(" 저장된 AI 모델과 토크나이저를 불러오는 중... (1초 소요)")

# 1. 파일에서 이미 완성된 AI 뇌(모델)와 토크나이저 불러오기
model = load_model("smishingai/smishing_ai_final/smishing_ai_v2 backup/smishing_ai_combined.keras"
,custom_objects={"f2_score": f2_score})

with open("smishingai/smishing_ai_final/smishing_ai_v2 backup/tokenizer_combined.pickle", "rb") as f:
    tokenizer = pickle.load(f)

# 설정값 (옛날 모델 크기인 50으로 세팅)
max_len = 50
categories = ["URL 위험도", "발신자 신뢰도", "문자 내용 위험도", "키워드 탐지", "URL 구조 분석"]

# 2. 모델의 맨 마지막 레이어에서 학습된 내부 가중치 직접 뜯어오기
last_layer_weights = model.layers[-1].get_weights()[0]
raw_weights = np.mean(np.abs(last_layer_weights), axis=1)[:5]
ai_learned_weights = (raw_weights / np.sum(raw_weights)) * 100
dict={
    "URL 위험도": ai_learned_weights[0],
    "발신자 신뢰도": ai_learned_weights[1],
    "문자 내용 위험도": ai_learned_weights[2],
    "키워드 탐지": ai_learned_weights[3],
    "URL 구조 분석": ai_learned_weights[4]
}

# 3. 시스템 가중치 대시보드 출력
print("\n" + "="*65)
print(" [AI가 스스로 세팅한 시스템 가중치]")
print("="*65)
for i in range(5):
    print(f"  {categories[i]:<12} : {ai_learned_weights[i]:>.1f}%")
print("="*65)
print(" 시스템 준비 완료! 언제든 문자를 입력하세요.")

# 4. 실시간 무한 탐지 루프 (3단계 판정 버전)
while True:
    test_text = input("\n 테스트할 문자 입력 (종료하려면 'q' 입력) : ").strip()
    if test_text.lower() == 'q':
        break
    if not test_text:
        continue
        
    # 입력한 문장을 AI가 이해할 수 있는 숫자로 변환
    seq = tokenizer.texts_to_sequences([test_text])
    t_in = pad_sequences(seq, maxlen=max_len, padding="post")
    f_in = np.array([extract_features(test_text)], dtype=np.float32)
    
    #  [여기서 확실하게 변수 선언!!] AI 예측 수행
    # pred_5와 pred_final 변수를 동시에 정확하게 생성합니다.
    pred_5, pred_final = model.predict([t_in, f_in], verbose=0)
    
    print("\n[ 실시간 AI 융합 분석 결과]")
    print("-" * 65)
    for i in range(5):
        print(f" - {categories[i]:<14}  : {pred_5[0][i]*100:>.1f}점")
    
    print("-" * 65)
    
  #  AI가 예측한 5대 항목 확률에 시스템 가중치를 직접 곱해서 100점 만점으로 연산
    calculated_score = 0.0
    for i in range(5):
        # pred_5[0][i] (0~1 사이 확률) * ai_learned_weights[i] (가중치 % 값)
        calculated_score += pred_5[0][i] * ai_learned_weights[i]
    
    # 계산된 누적 점수를 최종 score에 대입
    score = calculated_score
    
    #  3단계 위험도 판정 기준 적용
    if score < 40.0:
        level = "🟢 [안전]"
        action = "스미싱 확률이 낮습니다. 안심하셔도 좋습니다."
    elif score < 75.0:
        level = "🟡 [주의]"
        action = "의심스러운 정황이 있습니다. 링크 클릭이나 송금 전 반드시 확인하세요!"
    else:
        level = "🔴 [위험]"
        action = "스미싱일 확률이 매우 높습니다! 절대 링크를 누르지 마세요!"

    print(f" AI 최종 스미싱 위험도 점수 계산: {dict['URL 위험도']:.1f}%x{pred_5[0][0]*100:.1f} + {dict['발신자 신뢰도']:.1f}%x{pred_5[0][1]*100:.1f} + {dict['문자 내용 위험도']:.1f}%x{pred_5[0][2]*100:.1f} + {dict['키워드 탐지']:.1f}%x{pred_5[0][3]*100:.1f} + {dict['URL 구조 분석']:.1f}%x{pred_5[0][4]*100:.1f} = {calculated_score:.1f}")
    print(f" AI 최종 스미싱 위험도 점수: {calculated_score:.1f}")
    print(f" 판별 결과 : {level} {action}")
    print("="*65)