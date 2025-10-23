import json
import requests
import re
import time

# -------------------------------------
# 설정
# -------------------------------------
API_URL = "https://genshin-impact.fandom.com/api.php"
SECTION_NAME = "Other Languages"
INPUT_JSON = "data/Category_Playable_Characters.json"
OUTPUT_JSON = "data/Playable_Characters_with_ko_text.json"
SLEEP_TIME = 1.0  # 초 단위 딜레이

# 한글 텍스트 추출용 정규식
KOREAN_TEXT_PATTERN = re.compile(r'[가-힣][가-힣ㄱ-ㅎㅏ-ㅣ0-9a-zA-Z\s·ㆍ“”"‘’()\[\]\-—.,!?~]*')

# 제외할 짧은 단어 목록 (언어코드 등)
EXCLUDE_WORDS = {"ko", "en", "ja", "zh", "zhs", "zht", "es", "fr", "de", "ru", "id", "th", "vi", "pt", "it", "tr"}

# -------------------------------------
# 함수 정의
# -------------------------------------

def get_sections(title):
    """문서 섹션 목록 반환"""
    params = {"action": "parse", "page": title, "prop": "sections", "format": "json"}
  
    r = requests.get(API_URL, params=params)
    data = r.json()
    if "error" in data:
        return None
    return data["parse"]["sections"]

def get_section_index(sections, section_name):
    """섹션 이름으로 index 찾기"""
    for s in sections:
        if s["line"].strip().lower() == section_name.strip().lower():
            return s["index"]
    return None

def get_wikitext(title, section_index):
    """특정 섹션의 wikitext 가져오기"""
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

def extract_korean_text(wikitext):
    """wikitext에서 한글 포함 문자열만 추출"""
    if not wikitext:
        return None
    korean_parts = KOREAN_TEXT_PATTERN.findall(wikitext)

    filtered = []
    for t in korean_parts:
        text = t.strip()
        if not text:
            continue
        # 불필요한 키워드 제외 (ko, en 등)
        if text.lower() in EXCLUDE_WORDS:
            continue
        filtered.append(text)

    if not filtered:
        return None
    return " ".join(filtered)

# -------------------------------------
# 메인
# -------------------------------------

def main():
	  
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        pages = json.load(f)

    updated_pages = []

    for i, page in enumerate(pages, 1):
        title = page["title"]
        print(f"[{i}/{len(pages)}] {title} ...", end=" ")

        try:
            sections = get_sections(title)
            if not sections:
                print("❌ 섹션 정보 없음")
                updated_pages.append(page)
                continue

            index = get_section_index(sections, SECTION_NAME)
            if not index:
                print("⚠️ Other Languages 섹션 없음")
                updated_pages.append(page)
                continue  # 섹션 없으면 건너뜀

            wikitext = get_wikitext(title, index)
            ko_text = extract_korean_text(wikitext)

			
	  

			 
            if ko_text:
                page["ko_text"] = ko_text
                print(f"✅ 한글 추출 완료 ({len(ko_text)}자)")
            else:
                print("⚠️ 한글 없음")

		   

        except Exception as e:
            print(f"❌ 오류: {e}")

        updated_pages.append(page)

        time.sleep(SLEEP_TIME)

	   
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(updated_pages, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 완료: {len(updated_pages)}개 문서 → {OUTPUT_JSON}")

# -------------------------------------
# 실행
# -------------------------------------
if __name__ == "__main__":
    main()
