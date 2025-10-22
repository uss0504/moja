#랜덤 지정을 입력 받아서 배열에 있는 값(캐릭, 필보, 주보)으로 랜덤 돌리기.
"""
CATEGORY_LIST   = cfg["categories"]

def main():
    if not CATEGORY_LIST:
        print("❌ config 에 categories 가 비어 있습니다.", file=sys.stderr)
        sys.exit(1)

    for cat in CATEGORY_LIST:
        print(f"\n📂 카테고리 수집: {cat}")
        members = fetch_category_members(cat)
        print(f"   → {len(members)}개 문서 발견")

        print(f"🔍 한국어 번역 추출 중…")
        updated = extract_ko_for_pages(members)

        file_name = cat.replace(":", "_") + "_ko.json"
        file_path = OUTPUT_DIR / file_name
        # 기존 코드
        # with file_path.open("w", encoding="utf-8") as f:
        #     json.dump(updated, f, ensure_ascii=False, indent=2)
        # 교체 코드
        merged = merge_with_existing_json(updated, file_path)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        print(f"💾 병합 후 저장 완료: {file_path} (총 {len(merged)}개 항목)")

    print("\n✅ 모든 카테고리 처리 완료.")
"""


import json
import random

# ① JSON 파일 읽기
with open('data/Category_Playable_Characters_ko.json', 'r', encoding='utf-8') as f:
    items = json.load(f)          # items는 list

# ② 가중치 리스트 생성 (가중치가 없으면 기본값 1)
weights = [obj.get('weight', 1) for obj in items]

# ③ 가중치에 따라 한 개 선택
selected_obj = random.choices(items, weights=weights, k=1)[0]

# ④ `ko` 필드만 뽑아 출력
ko_value = selected_obj.get('ko')
ko_text_value = selected_obj.get('ko_text')
en_value = selected_obj.get('title')
if ko_value is not None:
    print("가중치에 따라 선택된 **ko** 내용:")
    print(ko_value)              # 문자열, 혹은 다른 객체가 들어있을 수도 있음
else:
    if ko_text_value is not None:
        print("**ko_text(위키 번역)** 내용")
        print(ko_text_value)
    else:
        if en_value is not None:
            print("**en(위키 제목)** 내용")
            print(en_value)
        else:
        # 가중치가 있는 객체지만 `ko` 가 없을 경우
            print("값이 없습니다.")
            print(json.dumps(selected_obj, ensure_ascii=False, indent=4))