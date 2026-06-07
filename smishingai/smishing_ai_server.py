import sys
import os
import json
import zipfile
import tempfile
import numpy as np
import pickle
import h5py
from http.server import BaseHTTPRequestHandler, HTTPServer
from flask import Flask

app=Flask((__name))

AI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smishing_ai_final", "smishing_ai_v2 backup")
sys.path.insert(0, AI_DIR)

from feature_extractor import extract_features

AI_PORT = int(os.environ.get("AI_PORT", "3002"))

print("AI 모델과 토크나이저를 불러오는 중...", flush=True)

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Dropout, Concatenate
from tensorflow.keras.regularizers import l2
from tensorflow.keras.preprocessing.sequence import pad_sequences

MAX_LEN = 50
FEATURE_DIM = 70


def build_model():
    text_input = Input(shape=(MAX_LEN,), name="text_input")
    x1 = Embedding(5000, 32)(text_input)
    x1 = LSTM(32, kernel_regularizer=l2(0.005))(x1)
    x1 = Dropout(0.4)(x1)

    feature_input = Input(shape=(FEATURE_DIM,), name="feature_input")
    x2 = Dense(32, activation="relu", kernel_regularizer=l2(0.005))(feature_input)
    x2 = Dropout(0.4)(x2)

    combined = Concatenate()([x1, x2])
    z = Dense(32, activation="relu", kernel_regularizer=l2(0.005))(combined)
    z = Dropout(0.3)(z)

    out_5 = Dense(5, activation="sigmoid", name="out_5")(z)
    out_final = Dense(1, activation="sigmoid", name="out_final")(z)

    return Model(inputs=[text_input, feature_input], outputs=[out_5, out_final])


model = build_model()

dummy_t = np.zeros((1, MAX_LEN))
dummy_f = np.zeros((1, FEATURE_DIM))
model.predict([dummy_t, dummy_f], verbose=0)

keras_path = os.path.join(AI_DIR, "smishing_ai_combined.keras")
with zipfile.ZipFile(keras_path) as zf:
    with tempfile.TemporaryDirectory() as tmpdir:
        weights_h5_path = os.path.join(tmpdir, "model.weights.h5")
        with zf.open("model.weights.h5") as src, open(weights_h5_path, "wb") as dst:
            dst.write(src.read())

        with h5py.File(weights_h5_path, "r") as hf:
            def get_vars(key):
                group = hf[f"layers\\{key}"]["vars"]
                return [group[str(i)][:] for i in sorted(int(k) for k in group.keys())]

            embedding_layer = model.get_layer("embedding")
            embedding_layer.set_weights(get_vars("embedding"))

            lstm_layer = model.get_layer("lstm")
            cell_group = hf["layers\\lstm\\cell"]["vars"]
            cell_keys = sorted(int(k) for k in cell_group.keys())
            lstm_layer.set_weights([cell_group[str(k)][:] for k in cell_keys])

            dense_layer = model.get_layer("dense")
            dense_layer.set_weights(get_vars("dense"))

            dense1_layer = model.get_layer("dense_1")
            dense1_layer.set_weights(get_vars("dense_1"))

            out5_layer = model.get_layer("out_5")
            out5_layer.set_weights(get_vars("dense_2"))

            outf_layer = model.get_layer("out_final")
            outf_layer.set_weights(get_vars("dense_3"))

print("모델 가중치 로드 완료!", flush=True)

import tf_keras
import tf_keras.src.preprocessing.text
sys.modules.setdefault("keras", tf_keras)
sys.modules.setdefault("keras.src", tf_keras.src)
sys.modules.setdefault("keras.src.preprocessing", tf_keras.src.preprocessing)
sys.modules.setdefault("keras.src.preprocessing.text", tf_keras.src.preprocessing.text)

with open(os.path.join(AI_DIR, "tokenizer_combined.pickle"), "rb") as f:
    tokenizer = pickle.load(f)

CATEGORIES = ["URL 위험도", "발신자 신뢰도", "문자 내용 위험도", "키워드 탐지", "URL 구조 분석"]
CATEGORY_KEYS = ["url_risk", "sender_risk", "content_risk", "keyword_risk", "url_struct"]

last_layer_weights = model.layers[-1].get_weights()[0]
raw_weights = np.mean(np.abs(last_layer_weights), axis=1)[:5]
ai_learned_weights = (raw_weights / np.sum(raw_weights)) * 100

cat_biases = model.get_layer("out_5").get_weights()[1]
final_bias = float(model.get_layer("out_final").get_weights()[1][0])

print(f"AI 서버 준비 완료 (포트 {AI_PORT})", flush=True)


def get_category_description(key, score):
    if key == "url_risk":
        if score >= 70: return "의심 URL 다수 포함"
        elif score >= 45: return "의심스러운 URL 포함"
        elif score >= 25: return "URL 위험 가능성 있음"
        else: return "URL 위협 없음"
    elif key == "sender_risk":
        if score >= 70: return "미등록·국제 발신, 공공기관 사칭"
        elif score >= 45: return "미등록 발신자 의심"
        elif score >= 25: return "발신자 확인 필요"
        else: return "발신자 이상 없음"
    elif key == "content_risk":
        if score >= 70: return "긴급·유도·금전 표현 다수"
        elif score >= 45: return "긴급·유도 표현 포함"
        elif score >= 25: return "의심 표현 일부 포함"
        else: return "내용 이상 없음"
    elif key == "keyword_risk":
        if score >= 70: return "스미싱 키워드 다수 탐지"
        elif score >= 45: return "스미싱 키워드 포함"
        elif score >= 25: return "주의 키워드 포함"
        else: return "위험 키워드 없음"
    elif key == "url_struct":
        if score >= 70: return "비정상 URL 구조 (단축·IP·무작위)"
        elif score >= 45: return "비정상 URL 구조 의심"
        elif score >= 25: return "URL 구조 일부 주의"
        else: return "URL 구조 정상"
    return ""


def analyze(text):
    clean_text = text.strip()
    seq = tokenizer.texts_to_sequences([clean_text])
    t_in = pad_sequences(seq, maxlen=MAX_LEN, padding="post")
    f_in = np.array([extract_features(clean_text)], dtype=np.float32)

    pred_5, pred_final = model.predict([t_in, f_in], verbose=0)

    score = round(float(pred_final[0][0]) * 100, 1)

    category_scores = {
        CATEGORY_KEYS[i]: round(float(pred_5[0][i]) * 100, 1)
        for i in range(5)
    }

    if score < 40.0:
        risk_level = "safe" if score < 20.0 else "low"
    elif score < 75.0:
        risk_level = "medium" if score < 57.0 else "high"
    else:
        risk_level = "critical"

    reasons = []
    threshold = 45.0

    if category_scores["url_risk"] >= threshold:
        reasons.append(f"[URL 위험] 의심스러운 URL이 포함되어 있습니다. (위험도 {category_scores['url_risk']:.0f}%)")
    if category_scores["sender_risk"] >= threshold:
        reasons.append(f"[발신자 사칭] 공공기관·금융기관 등을 사칭하는 발신자로 의심됩니다. (위험도 {category_scores['sender_risk']:.0f}%)")
    if category_scores["content_risk"] >= threshold:
        reasons.append(f"[문자 내용 위험] 스미싱에 자주 사용되는 내용 패턴이 감지되었습니다. (위험도 {category_scores['content_risk']:.0f}%)")
    if category_scores["keyword_risk"] >= threshold:
        reasons.append(f"[위험 키워드] 스미싱 관련 위험 키워드가 포함되어 있습니다. (위험도 {category_scores['keyword_risk']:.0f}%)")
    if category_scores["url_struct"] >= threshold:
        reasons.append(f"[URL 구조 이상] 비정상적인 URL 구조가 탐지되었습니다. (위험도 {category_scores['url_struct']:.0f}%)")

    if not reasons and risk_level != "safe":
        top_key = max(category_scores, key=category_scores.get)
        top_name = CATEGORIES[CATEGORY_KEYS.index(top_key)]
        reasons.append(f"[{top_name}] 복합적인 스미싱 패턴이 감지되었습니다. (위험도 {category_scores[top_key]:.0f}%)")

    weights_map = {CATEGORIES[i]: round(float(ai_learned_weights[i]), 1) for i in range(5)}

    weighted_contributions = {
        CATEGORIES[i]: round(category_scores[CATEGORY_KEYS[i]] * float(ai_learned_weights[i]) / 100, 1)
        for i in range(5)
    }
    weighted_sum = round(sum(weighted_contributions.values()), 1)

    biases = {CATEGORIES[i]: round(float(cat_biases[i]), 4) for i in range(5)}

    category_descriptions = {
        CATEGORIES[i]: get_category_description(CATEGORY_KEYS[i], category_scores[CATEGORY_KEYS[i]])
        for i in range(5)
    }

    return {
        "score": score,
        "riskLevel": risk_level,
        "reasons": reasons,
        "categoryScores": {CATEGORIES[i]: category_scores[CATEGORY_KEYS[i]] for i in range(5)},
        "weights": weights_map,
        "weightedContributions": weighted_contributions,
        "weightedSum": weighted_sum,
        "biases": biases,
        "finalBias": round(final_bias, 4),
        "categoryDescriptions": category_descriptions,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path != "/ai/analyze":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            text = data.get("message", "").strip()
            if not text:
                raise ValueError("message is empty")
            result = analyze(text)
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            self.send_response(400)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


if __name__ == "__main__":
    server = HTTPServer(("localhost", AI_PORT), Handler)
    print(f"AI HTTP 서버 실행 중: http://localhost:{AI_PORT}", flush=True)
    server.serve_forever()
