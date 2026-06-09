def analyze_smishing_text(test_text):
    max_len = 50  # 최신 천재 뇌 크기 고정!
    
    # 🧼 양끝 공백만 가볍게 제거
    clean_text = test_text.strip()
    
    # 💡 짧습니다 필터 제거! 주소만 있든, 단어 하나만 있든 무조건 AI 예측 실행
    seq = ai_tokenizer.texts_to_sequences([clean_text])
    t_in = pad_sequences(seq, maxlen=max_len, padding="post")
    f_in = np.array([extract_features(clean_text)], dtype=np.float32)
    
    # 🔥 AI 최종 연산 돌리기
    _, pred_final = ai_model.predict([t_in, f_in], verbose=0)
    score = pred_final[0][0] * 1000
    
    # 🚦 3단계 판정 기준 적용
    if score < 40.0:
        return score, "🟢 [안전]", "스미싱 확률이 낮습니다. 안심하셔도 좋습니다.", "green"
    elif score < 75.0:
        return score, "🟡 [주의]", "의심스러운 정황이 있습니다. 확인 후 주의하세요!", "orange"
    else:
        return score, "🔴 [위험]", "스미싱 확률이 매우 높습니다! 절대 링크를 누르지 마세요!", "red"
