# OneDrive Integration Guide

Microsoft Graph API를 사용하여 OneDrive 특정 폴더의 파일 목록을 가져오고 다운로드하는 모듈입니다.

---

## 📋 목차

1. [사전 준비](#사전-준비)
2. [설치](#설치)
3. [Azure AD 앱 등록](#azure-ad-앱-등록)
4. [환경 설정](#환경-설정)
5. [사용법](#사용법)
6. [예제 코드](#예제-코드)

---

## 🔧 사전 준비

### 1. 필수 패키지 설치

```bash
pip install msal requests python-dotenv
```

**패키지 설명:**
- `msal`: Microsoft Authentication Library (OAuth 인증)
- `requests`: HTTP 요청
- `python-dotenv`: 환경 변수 관리

---

## 🔑 Azure AD 앱 등록

### 1. Azure Portal에서 앱 등록

1. [Azure Portal](https://portal.azure.com/) 접속
2. **Azure Active Directory** (또는 **Microsoft Entra ID**) 선택
3. 왼쪽 메뉴에서 **앱 등록** 클릭
4. **새 등록** 클릭

### 2. 앱 등록 설정

**기본 정보 입력:**
- **이름**: `OneDrive File Manager` (원하는 이름)
- **지원되는 계정 유형**:
  - **이 조직 디렉터리의 계정만** (단일 테넌트) 선택
  - 또는 **모든 조직 디렉터리의 계정** (멀티테넌트) 선택
- **리디렉션 URI**:
  - 플랫폼: **퍼블릭 클라이언트/네이티브(모바일 및 데스크톱)**
  - URI: `http://localhost`

**등록** 클릭

### 3. 클라이언트 ID 및 테넌트 ID 복사

등록 완료 후 **개요** 페이지에서:
- **애플리케이션(클라이언트) ID** 복사 → `ONEDRIVE_CLIENT_ID`
- **디렉터리(테넌트) ID** 복사 → `ONEDRIVE_TENANT_ID`

### 4. 클라이언트 암호(Secret) 생성

1. 왼쪽 메뉴에서 **인증서 및 비밀** 클릭
2. **클라이언트 암호** 탭 선택
3. **새 클라이언트 암호** 클릭
4. 설명 입력 (예: `OneDrive Access`)
5. 만료 기간 선택 (예: 24개월)
6. **추가** 클릭
7. **값** 열의 암호를 즉시 복사 → `ONEDRIVE_CLIENT_SECRET`
   ⚠️ **주의**: 이 페이지를 벗어나면 다시 볼 수 없습니다!

### 5. API 권한 설정

1. 왼쪽 메뉴에서 **API 권한** 클릭
2. **권한 추가** 클릭
3. **Microsoft Graph** 선택
4. **위임된 권한** 선택
5. 다음 권한 추가:
   - `Files.Read` (파일 읽기)
   - `Files.Read.All` (모든 파일 읽기)
   - `offline_access` (오프라인 액세스)
6. **권한 추가** 클릭
7. **[조직]에 대한 관리자 동의 허용** 클릭 (관리자 권한 필요)

### 6. 인증 설정 (추가)

1. 왼쪽 메뉴에서 **인증** 클릭
2. **고급 설정** 섹션에서:
   - **공용 클라이언트 흐름 허용**: **예** 선택
3. **저장** 클릭

---

## ⚙️ 환경 설정

### 1. .env 파일 수정

`.env` 파일을 열어서 Azure AD 정보를 설정하세요:

```bash
# OneDrive API Credentials
ONEDRIVE_CLIENT_ID=12345678-1234-1234-1234-123456789abc
ONEDRIVE_CLIENT_SECRET=your_client_secret_here
ONEDRIVE_TENANT_ID=87654321-4321-4321-4321-cba987654321

# OneDrive Folder Path
# 루트: /
# 서브폴더: /Videos/CCTV 또는 /Documents/Dataset
ONEDRIVE_FOLDER_PATH=/Videos

# Token 저장 경로
ONEDRIVE_TOKEN_PATH=onedrive_token.json
```

### 2. 폴더 경로 설정

OneDrive 폴더 구조 예시:
```
OneDrive (개인용) 또는 OneDrive for Business
├── Documents/
├── Pictures/
└── Videos/
    └── CCTV/          ← 이 폴더를 사용하려면: /Videos/CCTV
        ├── video1.mp4
        └── video2.mp4
```

**경로 형식:**
- 루트 폴더: `/`
- 서브 폴더: `/폴더명/하위폴더명`
- 대소문자 구분하지 않음

### 3. 설정 검증

```bash
python settings.py
```

출력 예시:
```
=== OneDrive Settings ===
Client ID: 12345678-1234-1234...
Client Secret: ***
Tenant ID: 87654321-4321-4321-4321-cba987654321
Folder Path: /Videos
Token Path: onedrive_token.json
Scopes: ['Files.Read', 'Files.Read.All', 'offline_access']

✅ OneDrive settings are valid!
```

---

## 🚀 사용법

### 1. 기본 사용 (파일 목록 가져오기)

```bash
python onedrive_utils.py
```

첫 실행 시:
- 브라우저가 자동으로 열립니다
- Microsoft 계정으로 로그인
- 권한 요청 승인
- `onedrive_token.json` 파일이 자동 생성됩니다 (이후 재인증 불필요)

### 2. Python 코드에서 사용

```python
from onedrive_utils import OneDriveManager

# 매니저 초기화 (자동 인증)
manager = OneDriveManager()

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
from onedrive_utils import OneDriveManager, print_file_list

manager = OneDriveManager()
video_files = manager.list_video_files()

# 보기 좋게 출력
print_file_list(video_files, show_size=True)
```

### 예제 2: 특정 파일 다운로드

```python
from onedrive_utils import OneDriveManager

manager = OneDriveManager()
video_files = manager.list_video_files()

# 첫 번째 비디오 다운로드
if video_files:
    first_video = video_files[0]
    manager.download_file(
        download_url=first_video.get('@microsoft.graph.downloadUrl'),
        destination_path=f"./downloads/{first_video['name']}"
    )
```

### 예제 3: 특정 폴더의 파일 목록

```python
from onedrive_utils import OneDriveManager

manager = OneDriveManager()

# 다른 폴더 지정
cctv_files = manager.list_video_files(folder_path="/Videos/CCTV")
dataset_files = manager.list_video_files(folder_path="/Documents/Dataset")

print(f"CCTV videos: {len(cctv_files)}")
print(f"Dataset videos: {len(dataset_files)}")
```

### 예제 4: 노트북 파일과 통합

기존 노트북 파일을 다음과 같이 수정:

```python
from onedrive_utils import OneDriveManager
import cv2
from PIL import Image

# OneDrive에서 비디오 파일 목록 가져오기
manager = OneDriveManager()
video_files = manager.list_video_files(folder_path="/Videos/CCTV")

print(f"Found {len(video_files)} video files")

# 첫 번째 비디오 다운로드
video_file = video_files[0]
local_path = f"./downloads/{video_file['name']}"

print(f"Downloading: {video_file['name']}")
manager.download_file(
    download_url=video_file.get('@microsoft.graph.downloadUrl'),
    destination_path=local_path
)

# 기존 코드: OpenCV로 프레임 추출
cap = cv2.VideoCapture(local_path)
# ... (기존 로직 그대로)
```

### 예제 5: 여러 비디오 파일 일괄 처리

```python
from onedrive_utils import OneDriveManager
import cv2
from PIL import Image

manager = OneDriveManager()
video_files = manager.list_video_files()

for video_file in video_files[:5]:  # 처음 5개만
    print(f"\n{'='*60}")
    print(f"Processing: {video_file['name']}")
    print(f"{'='*60}")

    # 다운로드
    local_path = f"./downloads/{video_file['name']}"
    manager.download_file(
        download_url=video_file.get('@microsoft.graph.downloadUrl'),
        destination_path=local_path
    )

    # 프레임 추출
    cap = cv2.VideoCapture(local_path)
    # ... 기존 프레임 추출 로직

    # 처리 완료 후 파일 삭제 (선택사항)
    # os.remove(local_path)
```

### 예제 6: 파일 검색

```python
from onedrive_utils import OneDriveManager

manager = OneDriveManager()

# "assault" 키워드로 검색
results = manager.search_files(query="assault")

print(f"Found {len(results)} files matching 'assault'")
for file in results:
    print(f"- {file['name']}")
```

---

## 📂 파일 구조

```
final-project-dataset-prep/
├── .env                          # 환경 변수 (Git 제외)
├── .gitignore                    # Git 제외 파일 목록
├── onedrive_token.json           # 인증 토큰 (자동 생성, Git 제외)
├── settings.py                   # 설정 관리 모듈
├── onedrive_utils.py            # OneDrive API 유틸리티
├── README_ONEDRIVE.md           # 이 파일
└── 260114_Qwen3_VL_{카테고리명}_테스트.ipynb
```

---

## 🔄 Google Drive vs OneDrive 비교

| 기능 | Google Drive | OneDrive |
|-----|--------------|----------|
| 인증 방식 | OAuth 2.0 (Google) | OAuth 2.0 (Microsoft) |
| 폴더 식별 | Folder ID | Folder Path |
| API | Google Drive API | Microsoft Graph API |
| 패키지 | `google-auth`, `google-api-python-client` | `msal`, `requests` |
| 토큰 저장 | `token.pickle` | `onedrive_token.json` |

---

## ⚠️ 주의사항

1. **onedrive_token.json은 절대 공유하지 마세요**
   - `.gitignore`에 이미 추가되어 있습니다
   - GitHub에 업로드하면 보안 위험이 있습니다

2. **첫 실행 시 브라우저 인증 필요**
   - 로컬 환경에서만 가능 (Colab에서는 다른 방법 필요)

3. **API 할당량 제한**
   - Microsoft Graph API는 무료 계정 기준 제한이 있습니다
   - 대량 다운로드 시 속도 제한이 걸릴 수 있습니다

4. **읽기 전용 권한**
   - 현재 설정은 `Files.Read` (읽기 전용)
   - 파일 수정/삭제 불가

5. **개인 계정 vs 회사 계정**
   - 개인 OneDrive: 개인 Microsoft 계정 사용
   - OneDrive for Business: 회사/학교 계정 필요

---

## 🐛 문제 해결

### 문제: `Client ID is not set`
**해결**: `.env` 파일에서 `ONEDRIVE_CLIENT_ID`, `ONEDRIVE_CLIENT_SECRET`, `ONEDRIVE_TENANT_ID` 설정

### 문제: 인증 창이 열리지 않음
**해결**:
- Azure Portal에서 **인증** → **공용 클라이언트 흐름 허용** 활성화 확인
- 리디렉션 URI가 `http://localhost`로 설정되어 있는지 확인

### 문제: `insufficient_claims` 에러
**해결**:
- Azure Portal에서 **API 권한** → **관리자 동의 허용** 클릭
- 필요한 권한: `Files.Read`, `Files.Read.All`, `offline_access`

### 문제: `ModuleNotFoundError: No module named 'msal'`
**해결**:
```bash
pip install msal requests python-dotenv
```

### 문제: 폴더를 찾을 수 없음
**해결**:
- 폴더 경로 확인 (대소문자 구분 안 함)
- OneDrive 웹사이트에서 폴더 이름 확인
- 한글 폴더명도 지원됨 (예: `/비디오/CCTV`)

### 문제: Token has expired
**해결**:
```bash
# 토큰 파일 삭제 후 재인증
rm onedrive_token.json
python onedrive_utils.py
```

---

## 📚 참고 자료

- [Microsoft Graph API 문서](https://learn.microsoft.com/en-us/graph/api/overview)
- [MSAL Python 문서](https://github.com/AzureAD/microsoft-authentication-library-for-python)
- [OneDrive API 가이드](https://learn.microsoft.com/en-us/onedrive/developer/)
- [Azure AD 앱 등록 가이드](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)

---

## 🆚 Google Drive 모듈과 함께 사용하기

두 모듈을 동시에 사용할 수 있습니다:

```python
from gdrive_utils import GoogleDriveManager
from onedrive_utils import OneDriveManager

# Google Drive 파일
gdrive = GoogleDriveManager()
gdrive_videos = gdrive.list_video_files()

# OneDrive 파일
onedrive = OneDriveManager()
onedrive_videos = onedrive.list_video_files()

# 합치기
all_videos = {
    'google_drive': gdrive_videos,
    'onedrive': onedrive_videos
}

print(f"Total videos: {len(gdrive_videos) + len(onedrive_videos)}")
```

---

**작성일**: 2026-01-19
