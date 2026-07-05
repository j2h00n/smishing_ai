import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences

try:
    from library_import import ai_model, ai_tokenizer
except Exception:
    ai_model = None
    ai_tokenizer = None

from feature_extractor import extract_features


def _get_ai_learned_weights():
    if hasattr(_get_ai_learned_weights, "weights_cache"):
        return _get_ai_learned_weights.weights_cache

    if ai_model is None:
        weights = np.array([20.0, 20.0, 20.0, 20.0, 20.0], dtype=np.float32)
        _get_ai_learned_weights.weights_cache = weights
        return weights

    try:
        last_layer_weights = ai_model.layers[-1].get_weights()[0]
        raw_weights = np.mean(np.abs(last_layer_weights), axis=1)[:5]
        raw_weights = np.where(raw_weights > 0, raw_weights, 1e-6)
        weights = (raw_weights / np.sum(raw_weights)) * 100
    except Exception:
        weights = np.array([20.0, 20.0, 20.0, 20.0, 20.0], dtype=np.float32)

    _get_ai_learned_weights.weights_cache = weights
    return weights


def analyze_smishing_text(test_text):
    max_len = 50

    clean_text = test_text.strip()
    seq = ai_tokenizer.texts_to_sequences([clean_text])
    t_in = pad_sequences(seq, maxlen=max_len, padding="post")
    f_in = np.array([extract_features(clean_text)], dtype=np.float32)

    pred_5, _ = ai_model.predict([t_in, f_in], verbose=0)
    ai_learned_weights = _get_ai_learned_weights()

    calculated_score = float(np.sum(pred_5[0] * ai_learned_weights))
    score = round(calculated_score, 1)

    if score < 40.0:
        return score, "🟢 [안전]", "스미싱 확률이 낮습니다. 안심하셔도 좋습니다.", "green"
    elif score < 75.0:
        return score, "🟡 [주의]", "의심스러운 정황이 있습니다. 확인 후 주의하세요!", "orange"
    else:
        return score, "🔴 [위험]", "스미싱 확률이 매우 높습니다! 절대 링크를 누르지 마세요!", "red"