import sys
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences

base = 'c:/Users/rkdwl/Downloads/smishingai/smishingai/smishing-detector'
ai_dir = 'c:/Users/rkdwl/Downloads/smishingai/smishingai/smishing_ai_final/smishing_ai_v2 backup'
for p in [base, ai_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

import ai_function
from feature_extractor import extract_features
from library_import import ai_model, ai_tokenizer

max_len = 50
last_layer_weights = ai_model.layers[-1].get_weights()[0]
raw_weights = np.mean(np.abs(last_layer_weights), axis=1)[:5]
raw_weights = np.where(raw_weights > 0, raw_weights, 1e-6)
weights = (raw_weights / np.sum(raw_weights)) * 100


def backup_logic(text):
    clean_text = text.strip()
    seq = ai_tokenizer.texts_to_sequences([clean_text])
    t_in = pad_sequences(seq, maxlen=max_len, padding='post')
    f_in = np.array([extract_features(clean_text)], dtype=np.float32)
    pred_5, _ = ai_model.predict([t_in, f_in], verbose=0)
    calculated_score = 0.0
    for i in range(5):
        calculated_score += pred_5[0][i] * weights[i]
    score = calculated_score
    if score < 40.0:
        level = '🟢 [안전]'
        action = '스미싱 확률이 낮습니다. 안심하셔도 좋습니다.'
        color = 'green'
    elif score < 75.0:
        level = '🟡 [주의]'
        action = '의심스러운 정황이 있습니다. 확인 후 주의하세요!'
        color = 'orange'
    else:
        level = '🔴 [위험]'
        action = '스미싱 확률이 매우 높습니다! 절대 링크를 누르지 마세요!'
        color = 'red'
    return round(score, 1), level, action, color

samples = [
    '안녕하세요',
    '계좌가 잠겼습니다. 즉시 확인하세요.',
    'https://bit.ly/abc123 클릭하면 보상드립니다',
    '고객님, 본인 확인이 필요합니다. 바로 확인하세요.'
]

for text in samples:
    current = ai_function.analyze_smishing_text(text)
    backup = backup_logic(text)
    print('TEXT:', text)
    print('CURRENT:', current)
    print('BACKUP :', backup)
    print('SCORE_MATCH:', round(current[0], 1) == round(backup[0], 1))
    print('LABEL_MATCH:', current[1:] == backup[1:])
    print('---')
