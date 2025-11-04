import json
import random


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

# ① JSON 파일 읽기
with open('../../data/Category_Playable_Characters_ko.json', 'r', encoding='utf-8') as f:
    items = json.load(f)          # items는 list

# ② 가중치 리스트 생성 (가중치가 없으면 기본값 1)
weights = [obj.get('weight', 1) for obj in items]

# secret 을 이용한 random
selected_obj = secrets_choice(items, weights=weights, k=1)[0]

# 일반 random
# selected_obj = random.choices(items, weights=weights, k=1)[0]

# ④ `ko` 필드만 뽑아 출력
ko_value = selected_obj.get('ko')
ko_text_value = selected_obj.get('ko_text')
en_value = selected_obj.get('title')

if ko_value:
    print(f"랜덤 캐릭터: {ko_value}")
elif ko_text_value:
    print(f"랜덤 캐릭터: {ko_text_value}")
elif en_value:
    print(f"랜덤 캐릭터: {en_value}")
else:
    print(f"값이 없습니다.")
    print(json.dumps(selected_obj, ensure_ascii=False, indent=4))

# os.system("pause")
# input("작업 완료 – 엔터 키를 눌러 종료...")