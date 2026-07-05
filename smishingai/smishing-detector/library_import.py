import os
import sys
import numpy as np
import pickle
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "smishing_ai_final", "smishing_ai_v2 backup"))
for path in [BASE_DIR, AI_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from feature_extractor import extract_features


def f2_score(y_true, y_pred):
    y_true = tf.cast(tf.reshape(y_true, [-1]), tf.float32)
    y_pred = tf.cast(tf.reshape(tf.round(y_pred), [-1]), tf.float32)
    tp = tf.reduce_sum(y_true * y_pred)
    fp = tf.reduce_sum((1.0 - y_true) * y_pred)
    fn = tf.reduce_sum(y_true * (1.0 - y_pred))
    p = tp / (tp + fp + tf.keras.backend.epsilon())
    r = tp / (tp + fn + tf.keras.backend.epsilon())
    return 5.0 * (p * r) / (4.0 * p + r + tf.keras.backend.epsilon())


# UI 시작 시 AI 모델 미리 탑재 (오래 걸리니까 한 번만)
ai_model = load_model(
    os.path.join(AI_DIR, "smishing_ai_combined.keras"),
    custom_objects={"f2_score": f2_score},
)
with open(os.path.join(AI_DIR, "tokenizer_combined.pickle"), "rb") as f:
    ai_tokenizer = pickle.load(f)