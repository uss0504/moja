import json
import random
import os


# secrets를 이용한 랜덤함수
import bisect
import secrets
from itertools import accumulate
from typing import List, Any, Optional

def secrets_choice(
    population: List[Any],
    weights:  List[float],
    k: int = 1,
    *,
    factor: int = 10 ** 6,      # 가중치 곱셈 비율 (필요에 따라 조정)
    rnd: Optional[secrets.SystemRandom] = None
) -> List[Any]:
    """
    암호학적으로 안전한 가중치 기반 선택 (weights 가 float 일 때도 동작).

    Parameters
    ----------
    population : list
        선택 대상(예: [{'name': 'A', 'weight': 0.23}, ...])
    weights : list[float]
        각 항목에 대한 가중치(소수 가능)
    k : int, optional
        선택할 개수 (default 1)
    factor : int, optional
        가중치를 정수화하기 위해 곱할 값 (default 10^6)
        factor 가 클수록 정밀도가 높아지지만, `total` 이 2**63‑1 이하가
        되도록 주의하세요.
    rnd : secrets.SystemRandom, optional
        테스트/디버깅 용으로 다른 RNG 를 주입할 수 있음
    Returns
    -------
    list
        선택된 항목들(리스트 형태)
    """
    if rnd is None:
        rnd = secrets.SystemRandom()

    # 1. 실수 → 정수 변환
    int_weights = [int(round(w * factor)) for w in weights]

    # 2. 누적합 & 전체 가중치
    cum_weights = list(accumulate(int_weights))
    total = cum_weights[-1]

    if total <= 0:
        raise ValueError("전체 가중치가 0 이하이면 선택할 수 없습니다.")

    # 3. 암호학적으로 안전한 난수 생성
    result = []
    for _ in range(k):
        r = secrets.randbelow(total)        # 0 ≤ r < total (int)
        idx = bisect.bisect_right(cum_weights, r)
        result.append(population[idx])

    return result

'''
# 시스템 랜덤을 이용한 choice, 실수 가능.
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
'''
'''
# secrets를 이용한 랜덤함수, 정수 가중치만 가능
import bisect
from itertools import accumulate
import secrets

def secure_choice(population, weights, k=1):
    cum_weights = list(accumulate(weights))
    total = cum_weights[-1]
    result = []
    for _ in range(k):
        r = secrets.randbelow(total)
        idx = bisect.bisect_right(cum_weights, r)
        result.append(population[idx])
    return result
'''

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
# 실제 데이터: Category_Playable_Characters_ko.json
# 테스트 데이터: test.json
with open('Category_Playable_Characters_ko.json', 'r', encoding='utf-8') as f:
    items = json.load(f)          # items는 list

# ② 가중치 리스트 생성 (가중치가 없으면 기본값 1)
weights = [obj.get('weight', 1) for obj in items]

# 시스템 random
selected_obj = secrets_choice(items, weights=weights, k=1)[0]

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