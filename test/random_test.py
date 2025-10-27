import json
import random
import os

import bisect
from itertools import accumulate

sysrand = random.SystemRandom()

def sysrandom_choice(population, weights, k=1):
    cum_weights = list(accumulate(weights))      # 누적합(실수)
    total = cum_weights[-1]                      # 전체 가중치(실수)
    if total <= 0:
        raise ValueError("총 가중치가 0 이하이면 선택 불가")

    result = []
    for _ in range(k):
        # 0 ≤ r < total  (float)
        r = sysrand.random() * total            # sysrand.random() → [0,1)
        idx = bisect.bisect_right(cum_weights, r)
        result.append(population[idx])

    return result

''' 기존 코드 (문제: 가충치에 정수가 아닌 실수가 들어갔을때 오류가 있음.)
import bisect
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
'''

# ① JSON 파일 읽기
# 실제 데이터: Category_Playable_Characters_ko.json 테스트 데이터: test.json
with open('Category_Playable_Characters_ko.json', 'r', encoding='utf-8') as f:
    items = json.load(f)          # items는 list

# ② 가중치 리스트 생성 (가중치가 없으면 기본값 1)
weights = [obj.get('weight', 1) for obj in items]

# 시스템 random
selected_obj = sysrandom_choice(items, weights=weights, k=1)[0]

# 기존 일반 random
# selected_obj = random.choices(items, weights=weights, k=1)[0]


# ④ `ko` 필드만 뽑아 출력
ko_value = selected_obj.get('ko')
ko_text_value = selected_obj.get('ko_text')
en_value = selected_obj.get('title')
if ko_value:
    print("**ko(수동 번역)** 내용:")
    print(ko_value)
else:
    if ko_text_value:
        print("**ko_text(위키 번역)** 내용")
        print(ko_text_value)
    else:
        if en_value:
            print("**en(위키 제목)** 내용")
            print(en_value)
        else:
        # 가중치가 있는 객체지만 `ko` 가 없을 경우
            print("값이 없습니다.")
            print(json.dumps(selected_obj, ensure_ascii=False, indent=4))

#os.system("pause")

import time
#time.sleep(random.random()) # 조금 더 랜덤성을 위한 랜덤 대기시간