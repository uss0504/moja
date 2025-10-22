#!/usr/bin/env python3
import json, time, pathlib, sys, requests, re
from typing import List, Dict, Any

# ─────────────────────────────────────────────────────────────
# 1️⃣ Config 로드
# ─────────────────────────────────────────────────────────────
CONFIG_PATH = pathlib.Path(__file__).parent / "config.json"

def load_config(path: pathlib.Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

cfg = load_config(CONFIG_PATH)

API_URL         = cfg["api_url"]
CATEGORY_LIST   = cfg["categories"]
PAGE_LIMIT      = cfg.get("page_limit", 500)
SLEEP_BETWEEN   = cfg.get("sleep_between_calls", 0.5)
OUTPUT_DIR      = pathlib.Path(cfg.get("output_dir", "outputs")).absolute()
SECTION_NAME    = cfg.get("section_name", "Other Languages")
SLEEP_TIME      = cfg.get("sleep_time", 1.0)

if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# 2️⃣ Category 문서 목록 수집
# ─────────────────────────────────────────────────────────────
def fetch_category_members(category: str) -> List[Dict[str, Any]]:
    """한 개 카테고리의 문서 목록 수집"""
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

# ─────────────────────────────────────────────────────────────
# 3️⃣ Fandom 문서 섹션 파싱 + 한글 추출
# ─────────────────────────────────────────────────────────────
KOREAN_TEXT_PATTERN = re.compile(r"[가-힣][가-힣ㄱ-ㅎㅏ-ㅣ0-9a-zA-Z\s·ㆍ“”\"‘’()\[\]\-—.,!?~]*")
EXCLUDE_WORDS = {"ko", "en", "ja", "zh", "zhs", "zht", "es", "fr", "de", "ru", "id", "th", "vi", "pt", "it", "tr"}

def get_sections(title: str):
    params = {"action": "parse", "page": title, "prop": "sections", "format": "json"}
    r = requests.get(API_URL, params=params)
    data = r.json()
    if "error" in data:
        return None
    return data["parse"]["sections"]

def get_section_index(sections, section_name):
    for s in sections:
        if s["line"].strip().lower() == section_name.strip().lower():
            return s["index"]
    return None

def get_wikitext(title, section_index):
    params = {
        "action": "parse",
        "page": title,
        "prop": "wikitext",
        "format": "json",
        "section": section_index
    }
    r = requests.get(API_URL, params=params)
    data = r.json()
    if "error" in data:
        return None
    return data["parse"]["wikitext"]["*"]

def extract_korean_text(wikitext: str):
    """wikitext에서 한글 포함 문자열만 추출"""
    if not wikitext:
        return None
    korean_parts = KOREAN_TEXT_PATTERN.findall(wikitext)
    filtered = []
    for t in korean_parts:
        text = t.strip()
        if not text or text.lower() in EXCLUDE_WORDS:
            continue
        filtered.append(text)
    return " ".join(filtered) if filtered else None

# ─────────────────────────────────────────────────────────────
# 4️⃣ 문서별 ko_text 수집
# ─────────────────────────────────────────────────────────────
def extract_ko_for_pages(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    updated = []
    for i, page in enumerate(pages, 1):
        title = page["title"]
        print(f"   [{i}/{len(pages)}] {title} ...", end=" ")

        try:
            sections = get_sections(title)
            if not sections:
                print("❌ 섹션 정보 없음")
                updated.append(page)
                continue

            index = get_section_index(sections, SECTION_NAME)
            if not index:
                print("⚠️ 섹션 없음")
                updated.append(page)
                continue

            wikitext = get_wikitext(title, index)
            ko_text = extract_korean_text(wikitext)
            if ko_text:
                page["ko_text"] = ko_text
                print(f"✅ ({len(ko_text)}자)")
            else:
                print("⚠️ 한글 없음")

        except Exception as e:
            print(f"❌ 오류: {e}")

        updated.append(page)
        time.sleep(SLEEP_TIME)
    return updated

def merge_with_existing_json(new_data: List[Dict[str, Any]], file_path: pathlib.Path) -> List[Dict[str, Any]]:
    """기존 JSON 파일과 병합:
       - pageid 기준으로 기존 데이터 유지
       - 새 데이터의 ko_text 업데이트 / 신규 추가"""
    if file_path.exists():
        try:
            with file_path.open("r", encoding="utf-8") as f:
                old_data = json.load(f)
        except Exception:
            old_data = []
    else:
        old_data = []

    old_by_id = {item["pageid"]: item for item in old_data if "pageid" in item}

    for new_item in new_data:
        pid = new_item.get("pageid")
        if pid in old_by_id:
            old_by_id[pid].update(new_item)  # ko_text 등 새 데이터 덮어쓰기
        else:
            old_by_id[pid] = new_item  # 새 항목 추가

    merged = list(old_by_id.values())
    return merged


# ─────────────────────────────────────────────────────────────
# 5️⃣ 메인
# ─────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
