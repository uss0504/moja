# 데이터 가공 스크립트(수동번역용 개체 추가, 가중치 추가)

# 경로: ../data/Category_Playable_Characters_ko.json  ../data/Category_Normal_Bosses_ko.json  ../data/Category_Weekly_Bosses_ko.json
# todo: 
# 나중엔 이거 자동화도 한번 해봐야.
# 함수로 위 파일들을 한번에.
# 기존에 값이 있는 경우엔 무시하게...

import json
#import shutil   # 파일 백업용 (옵션)
#import copy     # 필요하면 깊은 복사

# 1. JSON 파일 읽기
with open('../data/Category_Playable_Characters_ko.json', 'r', encoding='utf-8') as f:
    items = json.load(f)        # items는 list

# 2. 백업 (필요하면 한 줄 아래 주석 해제)
# shutil.copy('data.json', 'data_backup.json')

# 3. 각 객체에 ko_text 복사
for item in items:
    if isinstance(item, dict) and 'ko_text' in item: # if 'ko_text' in item: 조건문이 바로 무시 부분을 처리합니다.  
        # 단순 복사: item['ko'] = item['ko_text']
        # 혹은 deep copy 필요하면:
        # item['ko'] = copy.deepcopy(item['ko_text'])
        item['ko'] = item['ko_text']
    item['weight'] = 1 # weight 가중치 추가

# 4. 같은 파일에 덮어쓰기
with open('../data/Category_Playable_Characters_ko.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=4)

print("✅ 완료!")