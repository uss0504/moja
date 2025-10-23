import json
import random
import os
import glob

# ① data 폴더 내 모든 *_Bosses_ko.json 파일 읽기
all_items = []
for path in glob.glob('data/*_Bosses_ko.json'):
    with open(path, 'r', encoding='utf-8') as f:
        try:
            items = json.load(f)
            all_items.extend(items)
        except Exception as e:
            print(f"[!] {path} 파일을 읽는 중 오류 발생:", e)

if not all_items:
    print("읽어올 데이터가 없습니다.")
    os.system("pause")
    exit()

# ② 가중치 리스트 생성 (없으면 기본값 1)
weights = [obj.get('weight', 1) for obj in all_items]

# ③ 랜덤 선택
selected_obj = random.choices(all_items, weights=weights, k=1)[0]

# ④ 출력 우선순위: ko > ko_text > title
ko_value = selected_obj.get('ko')
ko_text_value = selected_obj.get('ko_text')
en_value = selected_obj.get('title')

if ko_value:
    print(ko_value)
elif ko_text_value:
    print(ko_text_value)
elif en_value:
    print(en_value)
else:
    print("값이 없습니다.")
    print(json.dumps(selected_obj, ensure_ascii=False, indent=4))

os.system("pause")
