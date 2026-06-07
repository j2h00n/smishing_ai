import pandas as pd
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
print("발신자 검사를 강화한 자동 라벨링을 시작합니다...")


def read_csv_with_fallback(filename):
    path = BASE_DIR / filename
    encodings = ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr', 'latin1']
    for encoding in encodings:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            raise
    return pd.read_csv(path, encoding='utf-8', errors='replace')

# 데이터 불러오기
try:
    df1 = read_csv_with_fallback("data spam sms(eng).csv")
    df1 = df1[['Teks', 'Label']].rename(columns={'Teks': 'text', 'Label': 'label'})
    df1['label'] = df1['label'].replace('spam', 1)
    df1['label'] = df1['label'].replace('ham', 0)

    df2 = read_csv_with_fallback("presentation_smishing_dataset.csv")
    df2 = df2[['text', 'label']]
    df2['label'] = df2['label'].replace('normal', 0)
    df2['label'] = df2['label'].replace('smishing', 1)

    df3 = read_csv_with_fallback("lgaidataset_all_classified.csv")
    df3 = df3[['content', 'class']].rename(columns={'content': 'text', 'class': 'label'})
    df3['label'] = df3['label'].replace(1, 0)
    df3['label'] = df3['label'].replace(2, 1)
    df3['label'] = df3['label'].replace(3, 0)

    # 하나로 합치기
    df_combined= pd.concat([df1, df2, df3], ignore_index=True)

    # 결측치(비어있는 행) 제거
    df_combined= df_combined.dropna(subset=['text', 'label'])

    # 최종 파일 저장 (엑셀 등에서 깨지지 않게 utf-8-sig 적용)
    df_combined.to_csv(BASE_DIR / 'combined_smishing_dataset.csv', index=False, encoding='utf-8-sig')
    print("통합본(combined_smishing_dataset.csv) 저장 완료!")
except Exception as e:
    print(f"파일 불러오기 실패: {e}")
    exit()

def check_url_risk(text):
    if re.search(r'(http|https|www\.)', str(text).lower()): return 1
    return 0

def check_url_struct(text):
    if re.search(r'(tinyurl\.com|secure-check\.kr|verify-user\.net|bit\.ly)', str(text).lower()): return 1
    return 0

def check_sender_risk(text):
    if re.search(r'\[(국세청|정부24|경찰|검찰|신한은행|국민은행|우체국|CJ대한통운|카카오|네이버|쿠팡)\]', str(text)): 
        return 1
    return 0

def check_content_risk(text):
    if re.search(r'(재인증|본인\s*확인|이용\s*제한|비정상\s*로그인|과태료|환급금|소멸)', str(text)): return 1
    return 0

def check_keyword_risk(text):
    if re.search(r'(부고장|전자문서|인증번호)', str(text)): return 1
    return 0

# 라벨링 적용
df_combined['url_risk'] = df_combined['text'].apply(check_url_risk)
df_combined['sender_risk'] = df_combined['text'].apply(check_sender_risk)
df_combined['content_risk'] = df_combined['text'].apply(check_content_risk)
df_combined['keyword_risk'] = df_combined['text'].apply(check_keyword_risk)
df_combined['url_struct'] = df_combined['text'].apply(check_url_struct)

#라벨이 normal이면 무조건 0으로 클린하게 밀어버림
if 'label' in df_combined.columns:
    df_combined.loc[df_combined['label'] == 'normal', ['url_risk', 'sender_risk', 'content_risk', 'keyword_risk', 'url_struct']] = 0

labeled_df = df_combined[['text','label','url_risk', 'sender_risk', 'content_risk', 'keyword_risk', 'url_struct']].copy()

def normalize_label(value):
    if isinstance(value, str):
        return 1 if value.strip().lower() == 'smishing' else 0
    try:
        return int(value)
    except Exception:
        return 0

labeled_df['label'] = labeled_df['label'].apply(normalize_label)
labeled_df.to_csv(BASE_DIR / "labeled_presentation_dataset.csv", index=False, encoding="utf-8-sig")
print("정답지(labeled_presentation_dataset.csv) 생성 완료!")