import json
import random
import bisect
import os

from itertools import accumulate

sysrand = random.SystemRandom()

def sysrandom_choice(population, weights, k=1):
    cum_weights = list(accumulate(weights))
    total = cum_weights[-1]
    result = []
    for _ in range(k):
        # SystemRandom 의 randbelow 가 없으므로 randint 를 사용
        r = sysrand.randint(0, total - 1)
        idx = bisect.bisect_right(cum_weights, r)
        result.append(population[idx])
    return result

# ① JSON 파일 읽기
with open('test.json', 'r', encoding='utf-8') as f:
    items = json.load(f)          # items는 list

# ② 가중치 리스트 생성 (가중치가 없으면 기본값 1)
weights = [obj.get('weight', 1) for obj in items]

# ③ 가중치에 따라 한 개 선택
selected_obj = sysrandom_choice(items, weights=weights, k=1)[0]

# ④ `ko` 필드만 뽑아 출력
ko_value = selected_obj.get('ko')
ko_text_value = selected_obj.get('ko_text')
en_value = selected_obj.get('title')
if ko_value is not None:
    print("가중치에 따라 선택된 **ko** 내용:")
    print(ko_value)
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

os.system("pause")