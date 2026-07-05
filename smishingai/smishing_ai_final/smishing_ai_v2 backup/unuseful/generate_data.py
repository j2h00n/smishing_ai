import csv
import random

safe_sentences = [
    "오늘 점심 뭐 먹냐",
    "학교 끝나고 축구하자",
    "숙제 다 했어?",
    "생일 축하해",
    "주말에 영화 볼래?",
    "오늘 날씨 좋다",
    "같이 게임하자",
    "내일 시험 범위 알려줘",
    "도서관에서 공부하자",
    "저녁 뭐 먹을까"
]

banks = [
    "국민은행",
    "신한은행",
    "우리은행",
    "농협",
    "카카오뱅크"
]

danger_templates = [
    "{bank} 계좌 인증 필요",
    "{bank} 보안 확인 바랍니다",
    "긴급 계좌 인증 필요",
    "지원금 지급 대상입니다",
    "환급금 신청 바랍니다",
    "대출 승인 완료",
    "지금 바로 확인하세요",
    "계정이 정지될 예정입니다",
    "무료 상품권 지급 대상입니다",
    "쿠폰 당첨을 축하드립니다"
]

rows = []

# 매우 안전
for _ in range(100):
    rows.append([
        random.choice(safe_sentences),
        0
    ])

# 안전
for _ in range(50):
    rows.append([
        "수업 일정이 변경되었습니다",
        1
    ])

# 보통
for _ in range(50):
    rows.append([
        "배송 상태를 확인하세요",
        2
    ])

# 위험
for _ in range(50):
    rows.append([
        "본인 인증이 필요합니다",
        3
    ])

# 매우 위험
for _ in range(150):
    text = random.choice(
        danger_templates
    ).format(
        bank=random.choice(banks)
    )

    rows.append([
        text,
        4
    ])

random.shuffle(rows)

with open(
    "friend_data.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "text",
        "label"
    ])

    writer.writerows(rows)

print(
    "friend_data.csv 생성 완료"
)
print(
    "총 데이터:",
    len(rows)
)