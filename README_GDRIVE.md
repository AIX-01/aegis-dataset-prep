# Google Drive Integration Guide

Google Drive API를 사용하여 특정 폴더의 파일 목록을 가져오고 다운로드하는 모듈입니다.

---

## 📋 목차

1. [사전 준비](#사전-준비)
2. [설치](#설치)
3. [Google Drive API 설정](#google-drive-api-설정)
4. [환경 설정](#환경-설정)
5. [사용법](#사용법)
6. [예제 코드](#예제-코드)

---

## 🔧 사전 준비

### 1. 필수 패키지 설치

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv
```

---

## 🔑 Google Drive API 설정

### 1. Google Cloud Console에서 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **API 및 서비스** > **라이브러리** 이동
4. **Google Drive API** 검색 후 **사용 설정** 클릭

### 2. OAuth 2.0 클라이언트 ID 생성

1. **API 및 서비스** > **사용자 인증 정보** 이동
2. **사용자 인증 정보 만들기** > **OAuth 클라이언트 ID** 선택
3. 애플리케이션 유형: **데스크톱 앱** 선택
4. 이름 입력 후 **만들기** 클릭
5. **JSON 다운로드** 클릭

### 3. credentials.json 파일 배치

다운로드한 JSON 파일을 프로젝트 루트 디렉토리에 `credentials.json`으로 저장:

```
/home/bgmbgm94/workspace/final-project-dataset-prep/credentials.json
```

---

## ⚙️ 환경 설정

### 1. .env 파일 수정

`.env` 파일을 열어서 Google Drive 폴더 ID를 설정하세요:

```bash
# Google Drive API Credentials
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials.json

# Google Drive Folder ID
# 폴더 URL 예시: https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j
# 여기서 1a2b3c4d5e6f7g8h9i0j 부분이 Folder ID입니다
GOOGLE_DRIVE_FOLDER_ID=1a2b3c4d5e6f7g8h9i0j

# Token 저장 경로
GOOGLE_DRIVE_TOKEN_PATH=token.pickle
```

### 2. 폴더 ID 찾는 방법

1. Google Drive에서 원하는 폴더 열기
2. 브라우저 주소창의 URL 확인:
   ```
   https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j
   ```
3. `folders/` 뒤의 문자열이 **Folder ID**입니다

### 3. 설정 검증

```bash
python settings.py
```

출력 예시:
```
=== Google Drive Settings ===
Credentials Path: credentials.json
Folder ID: 1a2b3c4d5e6f7g8h9i0j
Token Path: token.pickle
Scopes: ['https://www.googleapis.com/auth/drive.readonly']

✅ All settings are valid!
```

---

## 🚀 사용법

### 1. 기본 사용 (파일 목록 가져오기)

```bash
python gdrive_utils.py
```

첫 실행 시:
- 브라우저가 자동으로 열립니다
- Google 계정으로 로그인
- 권한 요청 승인
- `token.pickle` 파일이 자동 생성됩니다 (이후 재인증 불필요)

### 2. Python 코드에서 사용

```python
from gdrive_utils import GoogleDriveManager

# 매니저 초기화 (자동 인증)
manager = GoogleDriveManager()

# 모든 파일 목록 가져오기
all_files = manager.list_files()
print(f"Total files: {len(all_files)}")

# 비디오 파일만 필터링
video_files = manager.list_video_files()
print(f"Video files: {len(video_files)}")

# 파일 정보 출력
for file in video_files:
    print(f"Name: {file['name']}")
    print(f"ID: {file['id']}")
    print(f"Size: {int(file.get('size', 0)) / (1024*1024):.2f} MB")
    print()
```

---

## 📝 예제 코드

### 예제 1: 비디오 파일 목록 출력

```python
from gdrive_utils import GoogleDriveManager, print_file_list

manager = GoogleDriveManager()
video_files = manager.list_video_files()

# 보기 좋게 출력
print_file_list(video_files, show_size=True)
```

### 예제 2: 특정 파일 다운로드

```python
from gdrive_utils import GoogleDriveManager

manager = GoogleDriveManager()
video_files = manager.list_video_files()

# 첫 번째 비디오 다운로드
if video_files:
    first_video = video_files[0]
    manager.download_file(
        file_id=first_video['id'],
        destination_path=f"./downloads/{first_video['name']}"
    )
```

### 예제 3: 노트북 파일과 통합

기존 노트북 파일을 다음과 같이 수정:

```python
from gdrive_utils import GoogleDriveManager
import cv2
from PIL import Image

# Google Drive에서 비디오 파일 목록 가져오기
manager = GoogleDriveManager()
video_files = manager.list_video_files()

print(f"Found {len(video_files)} video files")

# 첫 번째 비디오 다운로드
video_file = video_files[0]
local_path = f"./downloads/{video_file['name']}"

print(f"Downloading: {video_file['name']}")
manager.download_file(
    file_id=video_file['id'],
    destination_path=local_path
)

# 기존 코드: OpenCV로 프레임 추출
cap = cv2.VideoCapture(local_path)
# ... (기존 로직 그대로)
```

### 예제 4: 여러 비디오 파일 일괄 처리

```python
from gdrive_utils import GoogleDriveManager
import cv2
from PIL import Image

manager = GoogleDriveManager()
video_files = manager.list_video_files()

for video_file in video_files[:5]:  # 처음 5개만
    print(f"\n{'='*60}")
    print(f"Processing: {video_file['name']}")
    print(f"{'='*60}")

    # 다운로드
    local_path = f"./downloads/{video_file['name']}"
    manager.download_file(video_file['id'], local_path)

    # 프레임 추출
    cap = cv2.VideoCapture(local_path)
    # ... 기존 프레임 추출 로직

    # 처리 완료 후 파일 삭제 (선택사항)
    # os.remove(local_path)
```

---

## 📂 파일 구조

```
final-project-dataset-prep/
├── .env                          # 환경 변수 (Git 제외)
├── .gitignore                    # Git 제외 파일 목록
├── credentials.json              # Google API 인증 (Git 제외)
├── token.pickle                  # 인증 토큰 (자동 생성, Git 제외)
├── settings.py                   # 설정 관리 모듈
├── gdrive_utils.py              # Google Drive API 유틸리티
├── README_GDRIVE.md             # 이 파일
└── 260114_Qwen3_VL_{카테고리명}_테스트.ipynb
```

---

## ⚠️ 주의사항

1. **credentials.json과 token.pickle은 절대 공유하지 마세요**
   - `.gitignore`에 이미 추가되어 있습니다
   - GitHub에 업로드하면 보안 위험이 있습니다

2. **첫 실행 시 브라우저 인증 필요**
   - 로컬 환경에서만 가능 (Colab에서는 다른 방법 필요)

3. **API 할당량 제한**
   - Google Drive API는 무료로 하루 1,000,000 쿼리까지 가능
   - 대용량 파일 다운로드 시 시간이 걸릴 수 있습니다

4. **읽기 전용 권한**
   - 현재 설정은 `drive.readonly` (읽기 전용)
   - 파일 수정/삭제 불가

---

## 🐛 문제 해결

### 문제: `credentials.json not found`
**해결**: Google Cloud Console에서 credentials.json 다운로드 후 프로젝트 루트에 배치

### 문제: `GOOGLE_DRIVE_FOLDER_ID is not set`
**해결**: `.env` 파일에서 `GOOGLE_DRIVE_FOLDER_ID` 설정

### 문제: 인증 창이 열리지 않음
**해결**:
```python
# gdrive_utils.py 수정
flow.run_local_server(port=8080)  # 포트 변경 시도
```

### 문제: `ModuleNotFoundError: No module named 'google'`
**해결**:
```bash
pip install --upgrade google-auth google-auth-oauthlib google-api-python-client
```

---

## 📞 도움말

- [Google Drive API 문서](https://developers.google.com/drive/api/v3/about-sdk)
- [Python Quickstart](https://developers.google.com/drive/api/v3/quickstart/python)

---

**작성일**: 2026-01-19
