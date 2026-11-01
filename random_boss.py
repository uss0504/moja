import bisect
import json
import secrets
from itertools import accumulate
from pathlib import Path
from typing import Any, List, Optional, Sequence


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CONFIG_PATH = BASE_DIR / "config.json"
HISTORY_PATH = DATA_DIR / "boss_history.json"


def boss_identifier(item: dict) -> str:
    page_id = item.get("pageid")
    if page_id is not None:
        return f"pageid:{page_id}"

    title = item.get("title")
    if title:
        return f"title:{title}"

    raise ValueError(f"보스 식별자가 없습니다: {item!r}")


def adjusted_weights(
    population: Sequence[dict],
    history: Sequence[str],
    recent_multipliers: Sequence[float],
) -> List[float]:
    recent_positions = {}
    for position, identifier in enumerate(history):
        recent_positions.setdefault(identifier, position)

    weights = []
    for item in population:
        weight = item.get("weight", 1)
        position = recent_positions.get(boss_identifier(item))
        if position is not None and position < len(recent_multipliers):
            weight *= recent_multipliers[position]
        weights.append(weight)
    return weights


def secrets_choice(
    population: Sequence[Any],
    weights: Sequence[float],
    k: int = 1,
    *,
    factor: int = 10**6,
    rnd: Optional[secrets.SystemRandom] = None,
) -> List[Any]:
    if len(population) != len(weights):
        raise ValueError("population과 weights의 길이가 같아야 합니다.")
    if not population:
        raise ValueError("선택할 항목이 없습니다.")

    if rnd is None:
        rnd = secrets.SystemRandom()

    int_weights = []
    for weight in weights:
        if weight < 0:
            raise ValueError("가중치는 음수일 수 없습니다.")
        scaled_weight = int(round(weight * factor))
        int_weights.append(max(1, scaled_weight) if weight > 0 else 0)

    cumulative_weights = list(accumulate(int_weights))
    total = cumulative_weights[-1]
    if total <= 0:
        raise ValueError("전체 가중치가 0 이하이면 선택할 수 없습니다.")

    result = []
    for _ in range(k):
        roll = rnd.randrange(total)
        index = bisect.bisect_right(cumulative_weights, roll)
        result.append(population[index])
    return result


def load_history(path: Path) -> List[str]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        history = json.load(file)
    if not isinstance(history, list) or not all(
        isinstance(identifier, str) for identifier in history
    ):
        raise ValueError(f"보스 기록 형식이 올바르지 않습니다: {path}")
    return history


def main() -> None:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = json.load(file)

    recent_multipliers = config.get(
        "recent_boss_weight_multipliers", [0.05, 0.12, 0.20, 0.40]
    )
    if not isinstance(recent_multipliers, list) or any(
        not isinstance(value, (int, float)) or isinstance(value, bool)
        or value <= 0 or value > 1
        for value in recent_multipliers
    ):
        raise ValueError(
            "recent_boss_weight_multipliers는 0 초과 1 이하의 숫자 목록이어야 합니다."
        )

    all_items = []
    for path in sorted(DATA_DIR.glob("*_Bosses_ko.json")):
        with path.open("r", encoding="utf-8") as file:
            items = json.load(file)
        if not isinstance(items, list):
            raise ValueError(f"보스 데이터는 목록이어야 합니다: {path}")
        all_items.extend(items)

    if not all_items:
        raise ValueError(f"보스 데이터를 찾을 수 없습니다: {DATA_DIR}")

    history = load_history(HISTORY_PATH)
    weights = adjusted_weights(all_items, history, recent_multipliers)
    selected_obj = secrets_choice(all_items, weights=weights, k=1)[0]

    history_limit = len(recent_multipliers)
    if history_limit:
        history.insert(0, boss_identifier(selected_obj))
        history = history[:history_limit]
    else:
        history = []
    HISTORY_PATH.write_text(
        json.dumps(history, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    ko_value = selected_obj.get("ko")
    ko_text_value = selected_obj.get("ko_text")
    en_value = selected_obj.get("title")
    if ko_value:
        print(f"랜덤 보스: {ko_value}")
    elif ko_text_value:
        print(f"랜덤 보스: {ko_text_value}")
    elif en_value:
        print(f"랜덤 보스: {en_value}")
    else:
        raise ValueError(f"선택한 보스에 출력할 이름이 없습니다: {selected_obj!r}")


if __name__ == "__main__":
    main()
