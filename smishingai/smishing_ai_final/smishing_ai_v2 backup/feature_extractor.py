import re


def extract_features(text):

    text_lower = text.lower()

    features = []

    # URL 관련
    features.append(int("http" in text_lower))
    features.append(int("https" in text_lower))
    features.append(int("www" in text_lower))
    features.append(int(".com" in text_lower))
    features.append(int(".kr" in text_lower))
    features.append(int("bit.ly" in text_lower))
    features.append(int("tinyurl" in text_lower))

    # 연락처 관련
    features.append(
        int(bool(re.search(r"\d{2,4}-\d{3,4}-\d{4}", text)))
    )

    features.append(
        int(bool(re.search(r"010\d{8}", text)))
    )

    # 금융
    bank_words = [
        "은행", "계좌", "입금", "출금", "송금",
        "환급", "지원금", "대출", "카드", "결제"
    ]

    for word in bank_words:
        features.append(int(word in text))

    # 인증
    auth_words = [
        "인증", "확인", "본인확인",
        "로그인", "otp", "보안", "인증번호"
    ]

    for word in auth_words:
        features.append(int(word in text_lower))

    # 긴급성
    urgent_words = [
        "긴급", "즉시", "지금",
        "바로", "당장", "오늘까지", "마감"
    ]

    for word in urgent_words:
        features.append(int(word in text))

    # 개인정보
    personal_words = [
        "비밀번호",
        "주민번호",
        "계좌번호",
        "개인정보",
        "신분증"
    ]

    for word in personal_words:
        features.append(int(word in text))

    # 사칭
    fake_words = [
        "검찰",
        "경찰",
        "국세청",
        "금감원",
        "정부",
        "은행"
    ]

    for word in fake_words:
        features.append(int(word in text))

    # 설치 유도
    install_words = [
        "설치",
        "다운로드",
        "업데이트",
        "앱",
        "apk"
    ]

    for word in install_words:
        features.append(int(word in text_lower))

    # 보상 / 이벤트
    reward_words = [
        "무료",
        "당첨",
        "쿠폰",
        "상품권",
        "경품",
        "이벤트"
    ]

    for word in reward_words:
        features.append(int(word in text))

    # 위협
    threat_words = [
        "정지",
        "차단",
        "제한",
        "잠금",
        "불이익"
    ]

    for word in threat_words:
        features.append(int(word in text))

    # 숫자 개수
    digit_count = sum(c.isdigit() for c in text)
    features.append(digit_count)

    # 문자 길이
    features.append(len(text))

    # =========================
    # 카테고리 점수 계산
    # =========================

    financial_score = sum(features[9:19])
    auth_score = sum(features[19:26])
    urgent_score = sum(features[26:33])
    personal_score = sum(features[33:38])
    fake_score = sum(features[38:44])
    install_score = sum(features[44:49])
    reward_score = sum(features[49:55])
    threat_score = sum(features[55:60])

    category_scores = [
        financial_score,
        auth_score,
        urgent_score,
        personal_score,
        fake_score,
        install_score,
        reward_score,
        threat_score
    ]

    features.extend(category_scores)

    return features


# 테스트
if __name__ == "__main__":

    while True:

        msg = input("\n문자 입력 (종료=q): ")

        if msg.lower() == "q":
            break

        result = extract_features(msg)

        print("\nFeature 개수 :", len(result))
        print(result)
        score=0
        for i in result:
            score+=int(i)
        print('점수:{0}'.format(score))