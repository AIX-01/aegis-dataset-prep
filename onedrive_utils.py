"""
OneDrive utilities for listing and downloading files using Microsoft Graph API
"""
import os
import json
import requests
from pathlib import Path
from typing import List, Dict, Optional

import msal

import settings


class OneDriveManager:
    """Manage OneDrive API interactions using Microsoft Graph"""

    def __init__(self):
        """Initialize OneDrive Manager"""
        self.access_token = None
        self.client_app = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Microsoft Graph API using MSAL"""
        # Create MSAL client
        self.client_app = msal.PublicClientApplication(
            client_id=settings.ONEDRIVE_CLIENT_ID,
            authority=settings.ONEDRIVE_AUTHORITY
        )

        # Try to load cached token
        token_cache = self._load_token_cache()
        if token_cache:
            accounts = self.client_app.get_accounts()
            if accounts:
                # Try to acquire token silently
                result = self.client_app.acquire_token_silent(
                    scopes=settings.ONEDRIVE_SCOPES,
                    account=accounts[0]
                )
                if result and "access_token" in result:
                    self.access_token = result["access_token"]
                    self._save_token_cache(result)
                    return

        # If no cached token or silent acquisition failed, do interactive login
        result = self.client_app.acquire_token_interactive(
            scopes=settings.ONEDRIVE_SCOPES
        )

        if "access_token" in result:
            self.access_token = result["access_token"]
            self._save_token_cache(result)
        else:
            error = result.get("error", "Unknown error")
            error_desc = result.get("error_description", "No description")
            raise RuntimeError(f"Authentication failed: {error} - {error_desc}")

    def _load_token_cache(self) -> Optional[Dict]:
        """Load token from cache file"""
        if os.path.exists(settings.ONEDRIVE_TOKEN_PATH):
            try:
                with open(settings.ONEDRIVE_TOKEN_PATH, 'r') as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def _save_token_cache(self, token_data: Dict):
        """Save token to cache file"""
        with open(settings.ONEDRIVE_TOKEN_PATH, 'w') as f:
            json.dump(token_data, f, indent=2)

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def list_files(
        self,
        folder_path: Optional[str] = None,
        file_extension_filter: Optional[List[str]] = None,
        max_results: int = 1000
    ) -> List[Dict]:
        """
        List files in a OneDrive folder

        Args:
            folder_path: OneDrive folder path (e.g., '/Videos/CCTV')
            file_extension_filter: Filter by extensions (e.g., ['.mp4', '.avi'])
            max_results: Maximum number of results to return

        Returns:
            List of file dictionaries with keys: id, name, size, createdDateTime, @microsoft.graph.downloadUrl
        """
        if folder_path is None:
            folder_path = settings.ONEDRIVE_FOLDER_PATH

        # Build API endpoint
        # Use /me/drive/root:/path/to/folder:/children for path-based access
        if folder_path == "/" or folder_path == "":
            endpoint = "https://graph.microsoft.com/v1.0/me/drive/root/children"
        else:
            # Remove leading/trailing slashes
            folder_path = folder_path.strip('/')
            endpoint = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path}:/children"

        all_files = []
        next_link = endpoint

        while next_link and len(all_files) < max_results:
            response = requests.get(
                next_link,
                headers=self._get_headers()
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"Failed to list files: {response.status_code} - {response.text}"
                )

            data = response.json()
            files = data.get('value', [])

            # Filter out folders, keep only files
            files = [f for f in files if 'file' in f]

            # Apply extension filter if specified
            if file_extension_filter:
                files = [
                    f for f in files
                    if any(f['name'].lower().endswith(ext.lower()) for ext in file_extension_filter)
                ]

            all_files.extend(files)

            # Check for next page
            next_link = data.get('@odata.nextLink', None)

        return all_files[:max_results]

    def list_video_files(
        self,
        folder_path: Optional[str] = None,
        extensions: List[str] = None
    ) -> List[Dict]:
        """
        List video files in a folder

        Args:
            folder_path: OneDrive folder path
            extensions: List of video extensions to filter (e.g., ['.mp4', '.avi'])

        Returns:
            List of video file dictionaries
        """
        if extensions is None:
            extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']

        return self.list_files(
            folder_path=folder_path,
            file_extension_filter=extensions
        )

    def download_file(
        self,
        file_id: Optional[str] = None,
        download_url: Optional[str] = None,
        destination_path: str = None,
        chunk_size: int = 1024 * 1024 * 10  # 10MB chunks
    ) -> str:
        """
        Download a file from OneDrive

        Args:
            file_id: OneDrive file ID (if download_url is not provided)
            download_url: Direct download URL from file metadata
            destination_path: Local path to save the file
            chunk_size: Download chunk size in bytes

        Returns:
            Path to downloaded file
        """
        # Get download URL if not provided
        if download_url is None:
            if file_id is None:
                raise ValueError("Either file_id or download_url must be provided")

            # Get file metadata to retrieve download URL
            endpoint = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}"
            response = requests.get(endpoint, headers=self._get_headers())

            if response.status_code != 200:
                raise RuntimeError(
                    f"Failed to get file info: {response.status_code} - {response.text}"
                )

            file_info = response.json()
            download_url = file_info.get('@microsoft.graph.downloadUrl')

            if not download_url:
                raise RuntimeError("Download URL not found in file metadata")

        # Download file (no auth needed for download URL)
        destination_path = Path(destination_path)
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(download_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(destination_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = int((downloaded / total_size) * 100)
                        print(f"Download progress: {progress}%", end='\r')

        print(f"\n✅ Downloaded: {destination_path}")
        return str(destination_path)

    def get_file_info(self, file_id: str) -> Dict:
        """
        Get detailed information about a file

        Args:
            file_id: OneDrive file ID

        Returns:
            Dictionary with file metadata
        """
        endpoint = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}"
        response = requests.get(endpoint, headers=self._get_headers())

        if response.status_code != 200:
            raise RuntimeError(
                f"Failed to get file info: {response.status_code} - {response.text}"
            )

        return response.json()

    def search_files(self, query: str, max_results: int = 100) -> List[Dict]:
        """
        Search files in OneDrive

        Args:
            query: Search query string
            max_results: Maximum number of results

        Returns:
            List of matching file dictionaries
        """
        endpoint = f"https://graph.microsoft.com/v1.0/me/drive/root/search(q='{query}')"
        response = requests.get(endpoint, headers=self._get_headers())

        if response.status_code != 200:
            raise RuntimeError(
                f"Search failed: {response.status_code} - {response.text}"
            )

        data = response.json()
        files = data.get('value', [])

        # Filter out folders
        files = [f for f in files if 'file' in f]

        return files[:max_results]


def print_file_list(files: List[Dict], show_size: bool = True):
    """
    Pretty print file list

    Args:
        files: List of file dictionaries
        show_size: Whether to show file sizes
    """
    if not files:
        print("No files found.")
        return

    print(f"\n{'='*80}")
    print(f"Found {len(files)} file(s):")
    print(f"{'='*80}\n")

    for i, file in enumerate(files, 1):
        name = file['name']
        file_id = file['id']
        size_mb = int(file.get('size', 0)) / (1024 * 1024)

        print(f"{i:3d}. {name}")
        print(f"     ID: {file_id}")

        if show_size and size_mb > 0:
            print(f"     Size: {size_mb:.2f} MB")

        print()


# Example usage
if __name__ == "__main__":
    # Validate settings first
    try:
        settings.validate_onedrive_settings()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        exit(1)

    # Initialize manager
    print("Authenticating with OneDrive...")
    manager = OneDriveManager()

    # List all files
    print("\n=== Listing all files ===")
    all_files = manager.list_files()
    print_file_list(all_files)

    # List only video files
    print("\n=== Listing video files only ===")
    video_files = manager.list_video_files()
    print_file_list(video_files)

    # Example: Download first video file
    if video_files:
        print("\n=== Example: Download first video ===")
        first_video = video_files[0]
        print(f"Downloading: {first_video['name']}")

        # Uncomment to actually download
        # manager.download_file(
        #     download_url=first_video.get('@microsoft.graph.downloadUrl'),
        #     destination_path=f"./downloads/{first_video['name']}"
        # )
