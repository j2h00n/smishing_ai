import re


def extract_features(text):

    text = text.lower()

    # URL
    url = int(
        bool(
            re.search(
                r"http|www\.|\.com|\.kr|bit\.ly",
                text
            )
        )
    )

    # 전화번호
    phone = int(
        bool(
            re.search(
                r"\d{2,4}-\d{3,4}-\d{4}",
                text
            )
        )
    )

    # 금융 관련
    money_keywords = [
        "계좌",
        "입금",
        "출금",
        "대출",
        "지원금",
        "환급",
        "송금",
        "은행",
        "카드"
    ]

    money = int(
        any(
            word in text
            for word in money_keywords
        )
    )

    # 인증 관련
    auth_keywords = [
        "인증",
        "확인",
        "로그인",
        "본인확인",
        "본인 인증"
    ]

    auth = int(
        any(
            word in text
            for word in auth_keywords
        )
    )

    # 긴급성
    urgent_keywords = [
        "긴급",
        "즉시",
        "지금",
        "바로",
        "당장"
    ]

    urgent = int(
        any(
            word in text
            for word in urgent_keywords
        )
    )

    # 개인정보 요구
    personal_keywords = [
        "주민번호",
        "계좌번호",
        "비밀번호",
        "개인정보",
        "신분증"
    ]

    personal = int(
        any(
            word in text
            for word in personal_keywords
        )
    )

    # 숫자 개수
    digit_count = sum(
        c.isdigit()
        for c in text
    )

    return [
        url,
        phone,
        money,
        auth,
        urgent,
        personal,
        digit_count
    ]


while True:

    msg = input("\n문자 입력 (종료=q) : ")

    if msg.lower() == "q":
        break

    result = extract_features(msg)

    print("\n특징 추출 결과")

    print("URL :", result[0])
    print("전화번호 :", result[1])
    print("금융 :", result[2])
    print("인증 :", result[3])
    print("긴급 :", result[4])
    print("개인정보 :", result[5])
    print("숫자개수 :", result[6])