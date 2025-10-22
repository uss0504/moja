#!/usr/bin/env python3
import json, time, pathlib, sys, requests
from typing import List, Dict, Any

# ─────────────────────────────────────────────────────────────────────────────
# 1️⃣ Config 로드
CONFIG_PATH = pathlib.Path(__file__).parent / "config.json"

def load_config(path: pathlib.Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

cfg = load_config(CONFIG_PATH)

API_URL         = cfg["api_url"]
CATEGORY_LIST   = cfg["categories"]
PAGE_LIMIT      = cfg.get("page_limit", 500)
SLEEP_BETWEEN   = cfg.get("sleep_between_calls", 0.5)
OUTPUT_DIR      = pathlib.Path(cfg.get("output_dir", "category_outputs")).absolute()

if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 2️⃣ 분류별 문서 가져오기
def fetch_category_members(category: str) -> List[Dict[str, Any]]:
    """API 호출 한 번에 한 개 카테고리의 문서 목록을 반환"""
    all_members = []
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category,
        "cmnamespace": 0,
        "cmfilterredir": "redirects",
        "cmlimit": PAGE_LIMIT,
        "cmprop": "ids|title|namespace"
    }

    while True:
        resp = requests.get(API_URL, params=params, timeout=30)
        data = resp.json()

        if "error" in data:
            raise RuntimeError(f"[!] API 오류: {data['error']}")

        cmembers = data["query"]["categorymembers"]
        all_members.extend(cmembers)

        if "continue" in data:
            params.update(data["continue"])
            time.sleep(SLEEP_BETWEEN)
        else:
            break

    return all_members

# ─────────────────────────────────────────────────────────────────────────────
# 3️⃣ 모든 카테고리 순회 → 딕셔너리(카테고리: 리스트) 반환
def crawl_all_categories(categories: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    results: Dict[str, List[Dict[str, Any]]] = {}

    for cat in categories:
        print(f"[+] {cat} 로딩 중…")
        members = fetch_category_members(cat)
        results[cat] = members
        print(f"   -> {len(members)} 문서 수집")

    return results

# ─────────────────────────────────────────────────────────────────────────────
# 4️⃣ 저장 함수
def write_json_per_category(data: Dict[str, List[Dict[str, Any]]]) -> None:
    """카테고리별 JSON 파일을 저장"""
    for cat, members in data.items():
        file_name = cat.replace(":", "_") + ".json"  # 예: Category_MachineLearning.json
        file_path = OUTPUT_DIR / file_name
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(members, f, ensure_ascii=False, indent=2)
        print(f"   저장 완료: {file_path}")

# ─────────────────────────────────────────────────────────────────────────────
# 5️⃣ 메인
def main() -> None:
    if not CATEGORY_LIST:
        print("❌ config 에 categories 가 비어 있습니다.", file=sys.stderr)
        sys.exit(1)

    # 카테고리별 결과
    per_cat = crawl_all_categories(CATEGORY_LIST)

    # ── 저장 ──
    print("\n📂 저장 디렉터리:", OUTPUT_DIR)
    write_json_per_category(per_cat)          # JSON 저장

    print("\n✅ 모든 카테고리 파일이 준비되었습니다.")

if __name__ == "__main__":
    main()