import numpy as np
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from feature_extractor import extract_features

# UI 시작 시 AI 모델 미리 탑재 (오래 걸리니까 한 번만)
ai_model = load_model("smishing_ai_combined.keras")
with open("tokenizer_combined.pickle", "rb") as f:
    ai_tokenizer = pickle.load(f)