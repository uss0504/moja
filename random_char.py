import json
import random
import os

import bisect
from itertools import accumulate

sysrand = random.SystemRandom()

def sysrandom_choice(population, weights, k=1):
    cum_weights = list(accumulate(weights))
    total = cum_weights[-1]
    if total <= 0:
        raise ValueError("총 가중치가 0 이하이면 선택 불가")

    result = []
    for _ in range(k):
        # 0 ≤ r < total  (float)
        r = sysrand.random() * total            # sysrand.random() → [0,1)
        idx = bisect.bisect_right(cum_weights, r)
        result.append(population[idx])

    return result

# ① JSON 파일 읽기
with open('data/Category_Playable_Characters_ko.json', 'r', encoding='utf-8') as f:
    items = json.load(f)          # items는 list

# ② 가중치 리스트 생성 (가중치가 없으면 기본값 1)
weights = [obj.get('weight', 1) for obj in items]

# ③ 가중치에 따라 한 개 선택
selected_obj = sysrandom_choice(items, weights=weights, k=1)[0]

# ④ `ko` 필드만 뽑아 출력
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