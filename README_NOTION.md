# Notion API Integration Guide

Notion 데이터베이스의 테이블 데이터를 읽어오기 위한 Python 모듈입니다.

## 설치

필요한 라이브러리를 설치합니다:

```bash
pip install notion-client python-dotenv
```

## 설정 방법

### 1. Notion Integration 생성

1. [Notion Integrations 페이지](https://www.notion.so/my-integrations)로 이동
2. **+ New integration** 클릭
3. Integration 이름을 입력 (예: "Dataset Manager")
4. **Submit** 클릭
5. **Internal Integration Token**을 복사 (secret_XXXX...)

### 2. 데이터베이스에 Integration 연결

1. Notion에서 사용할 데이터베이스 페이지로 이동
2. 우측 상단의 `...` 메뉴 클릭
3. **Add connections** 선택
4. 생성한 Integration을 검색하여 추가

### 3. Database ID 가져오기

데이터베이스 URL에서 Database ID를 추출합니다:

**전체 페이지 URL 형식:**
```
https://www.notion.so/{workspace}/{database_id}?v={view_id}
```

**공유 링크 형식:**
```
https://www.notion.so/{database_id}?v={view_id}
```

예시:
```
https://www.notion.so/myworkspace/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4?v=...
                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                               이 부분이 Database ID입니다 (32자)
```

### 4. .env 파일 설정

`.env` 파일에 다음 정보를 입력합니다:

```bash
# Notion Integration Token
NOTION_API_KEY=secret_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Notion Database ID (32자의 영숫자 조합)
NOTION_DATABASE_ID=a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4
```

## 사용 방법

### 기본 사용법

```python
from notion_utils import create_notion_reader

# Reader 생성
reader = create_notion_reader()

# 데이터베이스 스키마 확인
reader.print_database_schema()

# 모든 데이터 읽기
all_data = reader.get_all_rows()
for row in all_data:
    print(row)
```

### 특정 컬럼만 읽기

```python
# "분류", "특이사항" 컬럼만 읽기
columns = ["분류", "특이사항"]
data = reader.get_columns(columns)

for row in data:
    print(f"분류: {row['분류']}")
    print(f"특이사항: {row['특이사항']}")
```

### 필터링과 정렬

```python
# 필터 적용
filter_dict = {
    "property": "분류",
    "select": {
        "equals": "긴급"
    }
}

# 정렬 적용
sorts = [
    {
        "property": "생성일",
        "direction": "descending"
    }
]

rows = reader.query_database(filter_dict=filter_dict, sorts=sorts)
```

## 테스트

테스트 스크립트를 실행하여 연결을 확인합니다:

```bash
python test_notion.py
```

테스트 내용:
1. Notion 연결 테스트
2. 데이터베이스 스키마 확인
3. "분류", "특이사항" 컬럼 읽기
4. 전체 데이터 읽기

## API Reference

### NotionTableReader 클래스

#### `__init__(api_key, database_id)`
Notion 클라이언트를 초기화합니다.

**Parameters:**
- `api_key` (str, optional): Notion API key (기본값: settings.NOTION_API_KEY)
- `database_id` (str, optional): Database ID (기본값: settings.NOTION_DATABASE_ID)

#### `query_database(filter_dict=None, sorts=None)`
데이터베이스를 쿼리합니다.

**Parameters:**
- `filter_dict` (dict, optional): Notion 필터 객체
- `sorts` (list, optional): 정렬 객체 리스트

**Returns:**
- `list`: 페이지 객체 리스트

#### `get_all_rows(property_names=None)`
모든 행을 가져옵니다.

**Parameters:**
- `property_names` (list, optional): 가져올 속성 이름 리스트 (None이면 모든 속성)

**Returns:**
- `list[dict]`: 행 데이터 리스트

#### `get_columns(column_names)`
특정 컬럼만 가져옵니다.

**Parameters:**
- `column_names` (list): 컬럼 이름 리스트

**Returns:**
- `list[dict]`: 지정된 컬럼만 포함된 행 데이터 리스트

#### `get_property_value(page, property_name)`
페이지에서 특정 속성 값을 추출합니다.

**Parameters:**
- `page` (dict): Notion 페이지 객체
- `property_name` (str): 속성 이름

**Returns:**
- `Any`: 속성 값 (타입은 속성 타입에 따라 다름)

**지원하는 속성 타입:**
- title, rich_text: 문자열
- number: 숫자
- select: 문자열
- multi_select: 문자열 리스트
- date: 날짜 문자열
- checkbox: 불린
- url, email, phone_number: 문자열
- status: 문자열

#### `print_database_schema()`
데이터베이스 스키마 정보를 출력합니다.

## 예제

### 예제 1: 특정 컬럼 읽기

```python
from notion_utils import create_notion_reader

reader = create_notion_reader()

# "분류", "특이사항" 컬럼 읽기
data = reader.get_columns(["분류", "특이사항"])

for row in data:
    print(f"분류: {row.get('분류', 'N/A')}")
    print(f"특이사항: {row.get('특이사항', 'N/A')}")
    print("-" * 40)
```

### 예제 2: 필터링된 데이터 가져오기

```python
from notion_utils import NotionTableReader

reader = NotionTableReader()

# "분류"가 "긴급"인 항목만 가져오기
filter_dict = {
    "property": "분류",
    "select": {
        "equals": "긴급"
    }
}

urgent_items = reader.query_database(filter_dict=filter_dict)

for page in urgent_items:
    분류 = reader.get_property_value(page, "분류")
    특이사항 = reader.get_property_value(page, "특이사항")
    print(f"분류: {분류}, 특이사항: {특이사항}")
```

### 예제 3: 모든 데이터 읽고 CSV로 저장

```python
import csv
from notion_utils import create_notion_reader

reader = create_notion_reader()
data = reader.get_all_rows()

# CSV로 저장
if data:
    keys = [k for k in data[0].keys() if not k.startswith("_")]

    with open("notion_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()

        for row in data:
            filtered_row = {k: v for k, v in row.items() if not k.startswith("_")}
            writer.writerow(filtered_row)

    print("Data saved to notion_data.csv")
```

## 문제 해결

### 인증 오류
```
Error: Unauthorized
```
- Integration Token이 올바른지 확인
- 데이터베이스에 Integration이 연결되었는지 확인

### Database ID 오류
```
Error: Could not find database with ID
```
- Database ID가 32자의 영숫자 조합인지 확인
- 하이픈(-)이 포함되지 않았는지 확인

### 속성 이름 오류
```
Property "XXX" not found
```
- 데이터베이스에 해당 속성(컬럼)이 존재하는지 확인
- 속성 이름의 대소문자와 공백이 정확한지 확인
- `reader.print_database_schema()`로 사용 가능한 속성 확인

## 참고 자료

- [Notion API Documentation](https://developers.notion.com/)
- [notion-client Python SDK](https://github.com/ramnes/notion-sdk-py)
- [Notion API Database Query](https://developers.notion.com/reference/post-database-query)
