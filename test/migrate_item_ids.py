import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def migrate_file(path: Path, identifiers_by_pageid: dict, identifiers_by_title: dict) -> None:
    with path.open("r", encoding="utf-8") as file:
        items = json.load(file)
    if not isinstance(items, list):
        raise ValueError(f"데이터는 목록이어야 합니다: {path}")
    if not all(isinstance(item, dict) for item in items):
        raise ValueError(f"항목은 객체여야 합니다: {path}")

    prefix = path.stem
    used_ids = set()
    next_id = 1
    for item in items:
        item_id = item.get("id")
        if isinstance(item_id, str):
            item_id = item_id.removeprefix(f"{prefix}:")
            if item_id.isdigit():
                next_id = max(next_id, int(item_id) + 1)
        elif isinstance(item_id, int) and not isinstance(item_id, bool):
            next_id = max(next_id, item_id + 1)

    changed = False
    for item in items:
        item_id = item.get("id")
        if isinstance(item_id, str):
            item_id = item_id.removeprefix(f"{prefix}:")
            item_id = int(item_id) if item_id.isdigit() else None
        elif not isinstance(item_id, int) or isinstance(item_id, bool):
            item_id = None
        if item_id is None or item_id in used_ids:
            while next_id in used_ids:
                next_id += 1
            item_id = next_id
            next_id += 1
        if item.get("id") != item_id:
            item["id"] = item_id
            changed = True
        used_ids.add(item_id)

        pageid = item.get("pageid")
        if pageid is not None:
            identifiers_by_pageid.setdefault(
                f"pageid:{pageid}", f"id:{prefix}:{item_id}"
            )
        title = item.get("title")
        if title:
            identifiers_by_title.setdefault(
                f"title:{title}", f"id:{prefix}:{item_id}"
            )

    if changed:
        with path.open("w", encoding="utf-8") as file:
            json.dump(items, file, ensure_ascii=False, indent=2)
        print(f"ID 추가 완료: {path.name}")
    else:
        print(f"변경 없음: {path.name}")


def migrate_history(identifiers_by_pageid: dict, identifiers_by_title: dict) -> None:
    history_path = DATA_DIR / "boss_history.json"
    if not history_path.exists():
        return

    with history_path.open("r", encoding="utf-8") as file:
        history = json.load(file)
    if not isinstance(history, list) or not all(
        isinstance(identifier, str) for identifier in history
    ):
        raise ValueError(f"보스 기록 형식이 올바르지 않습니다: {history_path}")

    migrated = [
        identifiers_by_pageid.get(
            identifier, identifiers_by_title.get(identifier, identifier)
        )
        for identifier in history
    ]
    if migrated != history:
        with history_path.open("w", encoding="utf-8") as file:
            json.dump(migrated, file, ensure_ascii=False, indent=2)
            file.write("\n")
        print("보스 기록 ID 갱신 완료")


def main() -> None:
    identifiers_by_pageid = {}
    identifiers_by_title = {}
    paths = sorted(DATA_DIR.glob("Category_*_ko.json"))
    if not paths:
        raise FileNotFoundError(f"크롤러 데이터 파일이 없습니다: {DATA_DIR}")

    for path in paths:
        migrate_file(path, identifiers_by_pageid, identifiers_by_title)
    migrate_history(identifiers_by_pageid, identifiers_by_title)


if __name__ == "__main__":
    main()
