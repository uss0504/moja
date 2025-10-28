import json
from collections import Counter
from pathlib import Path

DATA_FILE = '../data/Category_Playable_Characters_ko.json'

def find_duplicate_pageids(file_path):
    # 1. 파일 읽기
    with open(file_path, 'r', encoding='utf-8') as f:
        items = json.load(f)

    # 2. pageid 수집
    pageids = [item.get('pageid') for item in items if 'pageid' in item]

    # 3. 중복 카운트
    counts = Counter(pageids)

    # 4. 중복인 것만 추출
    duplicates = {pid: cnt for pid, cnt in counts.items() if cnt > 1}

    return duplicates, items

def report_duplicates(duplicates):
    if not duplicates:
        print("✅ 중복되는 pageid 가 없습니다.")
        return

    print("⚠️ 중복되는 pageid 가 발견되었습니다!")
    for pid, cnt in duplicates.items():
        print(f"   - pageid {pid} 가 {cnt}번 등장합니다.")

# 실행
duplicates, items = find_duplicate_pageids(DATA_FILE)
report_duplicates(duplicates)

# ------------------------------
# 5. (옵션) 중복 항목을 표시해 보고 싶다면
#     예시: 중복인 모든 항목을 별도로 나열
if duplicates:
    print("\n--- 중복 항목 상세 보기 ---")
    for idx, item in enumerate(items, 1):
        pid = item.get('pageid')
        if pid in duplicates:
            print(f"{idx:02d}. {item}")