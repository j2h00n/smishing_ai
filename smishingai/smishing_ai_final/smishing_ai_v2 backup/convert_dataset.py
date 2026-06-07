import pandas as pd

data = pd.read_csv("presentation_smishing_dataset.csv")

label_map = {
    "가족": 0,
    "친구": 0,
    "학교": 1,
    "일정": 1,
    "쇼핑몰": 2,
    "택배": 2,
    "계정인증": 3,
    "금융": 4,
    "정부": 4,
    "청첩장/부고": 4
}

data["label"] = data["category"].map(label_map)

data[["text", "label"]].to_csv(
    "friend_data.csv",
    index=False,
    encoding="utf-8-sig"
)

print("변환 완료")