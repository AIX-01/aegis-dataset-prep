"""
Settings module for Google Drive and OneDrive integration
Loads configuration from .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Google Drive API Settings
GOOGLE_DRIVE_CREDENTIALS_PATH = os.getenv(
    "GOOGLE_DRIVE_CREDENTIALS_PATH",
    "credentials.json"
)

GOOGLE_DRIVE_FOLDER_ID = os.getenv(
    "GOOGLE_DRIVE_FOLDER_ID",
    ""
)

GOOGLE_DRIVE_TOKEN_PATH = os.getenv(
    "GOOGLE_DRIVE_TOKEN_PATH",
    "token.pickle"
)

# API Scopes
GOOGLE_DRIVE_SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly'  # Read-only access
]

# ============================================================
# OneDrive API Settings
# ============================================================

ONEDRIVE_CLIENT_ID = os.getenv("ONEDRIVE_CLIENT_ID", "")
ONEDRIVE_CLIENT_SECRET = os.getenv("ONEDRIVE_CLIENT_SECRET", "")
ONEDRIVE_TENANT_ID = os.getenv("ONEDRIVE_TENANT_ID", "")
ONEDRIVE_FOLDER_PATH = os.getenv("ONEDRIVE_FOLDER_PATH", "/Videos")
ONEDRIVE_TOKEN_PATH = os.getenv("ONEDRIVE_TOKEN_PATH", "onedrive_token.json")

# OneDrive API Scopes
ONEDRIVE_SCOPES = [
    'Files.Read',
    'Files.Read.All',
    'offline_access'
]

# OneDrive Authority URL
ONEDRIVE_AUTHORITY = f"https://login.microsoftonline.com/{ONEDRIVE_TENANT_ID}"

# ============================================================
# Notion API Settings
# ============================================================

NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")

# ============================================================
# Validation
# ============================================================
def validate_settings():
    """Validate required settings"""
    errors = []

    if not GOOGLE_DRIVE_FOLDER_ID:
        errors.append("GOOGLE_DRIVE_FOLDER_ID is not set in .env")

    if not os.path.exists(GOOGLE_DRIVE_CREDENTIALS_PATH):
        errors.append(f"Credentials file not found: {GOOGLE_DRIVE_CREDENTIALS_PATH}")

    if errors:
        raise ValueError(
            "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
        )

    return True


def validate_onedrive_settings():
    """Validate OneDrive required settings"""
    errors = []

    if not ONEDRIVE_CLIENT_ID:
        errors.append("ONEDRIVE_CLIENT_ID is not set in .env")

    if not ONEDRIVE_CLIENT_SECRET:
        errors.append("ONEDRIVE_CLIENT_SECRET is not set in .env")

    if not ONEDRIVE_TENANT_ID:
        errors.append("ONEDRIVE_TENANT_ID is not set in .env")

    if errors:
        raise ValueError(
            "OneDrive configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
        )

    return True


def validate_notion_settings():
    """Validate Notion required settings"""
    errors = []

    if not NOTION_API_KEY:
        errors.append("NOTION_API_KEY is not set in .env")

    if not NOTION_DATABASE_ID:
        errors.append("NOTION_DATABASE_ID is not set in .env")

    if errors:
        raise ValueError(
            "Notion configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
        )

    return True


if __name__ == "__main__":
    # Test settings
    print("=== Google Drive Settings ===")
    print(f"Credentials Path: {GOOGLE_DRIVE_CREDENTIALS_PATH}")
    print(f"Folder ID: {GOOGLE_DRIVE_FOLDER_ID}")
    print(f"Token Path: {GOOGLE_DRIVE_TOKEN_PATH}")
    print(f"Scopes: {GOOGLE_DRIVE_SCOPES}")

    try:
        validate_settings()
        print("\n✅ Google Drive settings are valid!")
    except ValueError as e:
        print(f"\n❌ {e}")

    print("\n" + "="*60)
    print("=== OneDrive Settings ===")
    print(f"Client ID: {ONEDRIVE_CLIENT_ID[:20] + '...' if ONEDRIVE_CLIENT_ID else 'Not set'}")
    print(f"Client Secret: {'***' if ONEDRIVE_CLIENT_SECRET else 'Not set'}")
    print(f"Tenant ID: {ONEDRIVE_TENANT_ID}")
    print(f"Folder Path: {ONEDRIVE_FOLDER_PATH}")
    print(f"Token Path: {ONEDRIVE_TOKEN_PATH}")
    print(f"Scopes: {ONEDRIVE_SCOPES}")

    try:
        validate_onedrive_settings()
        print("\n✅ OneDrive settings are valid!")
    except ValueError as e:
        print(f"\n❌ {e}")

    print("\n" + "="*60)
    print("=== Notion Settings ===")
    print(f"API Key: {'***' if NOTION_API_KEY else 'Not set'}")
    print(f"Database ID: {NOTION_DATABASE_ID[:20] + '...' if NOTION_DATABASE_ID else 'Not set'}")

    try:
        validate_notion_settings()
        print("\n✅ Notion settings are valid!")
    except ValueError as e:
        print(f"\n❌ {e}")
