import json, glob, bisect, secrets
from itertools import accumulate
from typing import List, Any, Optional

def secrets_choice(
    population: List[Any],
    weights: List[float],
    k: int = 1,
    *,
    factor: int = 10**6,
    rnd: Optional[secrets.SystemRandom] = None
) -> List[Any]:
    if rnd is None:
        rnd = secrets.SystemRandom()

    # 정수화
    int_weights = [int(round(w * factor)) for w in weights]

    # 누적 가중치
    cum_weights = list(accumulate(int_weights))
    total = cum_weights[-1]
    if total <= 0:
        raise ValueError("전체 가중치가 0 이하이면 선택할 수 없습니다.")

    result = []
    for _ in range(k):
        r = secrets.randbelow(total)   # 0 ≤ r < total
        idx = bisect.bisect_right(cum_weights, r) # population와 weights가 같은 길이인 것을 보장
        result.append(population[idx])
    return result

''' 기존 system 랜덤
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
'''

# ---------- 데이터 로드 ----------
all_items = []
for path in glob.glob('data/*_Bosses_ko.json'):
    with open(path, 'r', encoding='utf-8') as f:
        try:
            items = json.load(f)
            all_items.extend(items)
        except Exception as e:
            print(f"[!] {path} 파일을 읽는 중 오류 발생: {e}")

if not all_items:
    print("오류: 읽어올 데이터가 없습니다.")
    # input("작업 완료 – 엔터 키를 눌러 종료...")
    exit()

# ---------- 가중치 ----------
weights = [obj.get('weight', 1) for obj in all_items]

# ---------- 선택 ----------
selected_obj = secrets_choice(all_items, weights=weights, k=1)[0]

# 시스템 random
# selected_obj = sysrandom_choice(items, weights=weights, k=1)[0]

# 일반 random
# selected_obj = random.choices(items, weights=weights, k=1)[0]

# ---------- 출력 ----------
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

# input("작업 완료 – 엔터 키를 눌러 종료...")