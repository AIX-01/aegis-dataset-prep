"""
Google Drive utilities for listing and downloading files
"""
import os
import pickle
from pathlib import Path
from typing import List, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import settings


class GoogleDriveManager:
    """Manage Google Drive API interactions"""

    def __init__(self):
        """Initialize Google Drive Manager"""
        self.credentials = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Drive API"""
        # Check if token.pickle exists (previously authenticated)
        if os.path.exists(settings.GOOGLE_DRIVE_TOKEN_PATH):
            with open(settings.GOOGLE_DRIVE_TOKEN_PATH, 'rb') as token:
                self.credentials = pickle.load(token)

        # If credentials are invalid or don't exist, authenticate
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                # Run OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.GOOGLE_DRIVE_CREDENTIALS_PATH,
                    settings.GOOGLE_DRIVE_SCOPES
                )
                self.credentials = flow.run_local_server(port=0)

            # Save credentials for future use
            with open(settings.GOOGLE_DRIVE_TOKEN_PATH, 'wb') as token:
                pickle.dump(self.credentials, token)

        # Build the service
        self.service = build('drive', 'v3', credentials=self.credentials)

    def list_files(
        self,
        folder_id: Optional[str] = None,
        mime_type_filter: Optional[str] = None,
        max_results: int = 1000
    ) -> List[Dict]:
        """
        List files in a Google Drive folder

        Args:
            folder_id: Google Drive folder ID (uses default from settings if None)
            mime_type_filter: Filter by MIME type (e.g., 'video/mp4')
            max_results: Maximum number of results to return

        Returns:
            List of file dictionaries with keys: id, name, mimeType, size, createdTime
        """
        if folder_id is None:
            folder_id = settings.GOOGLE_DRIVE_FOLDER_ID

        # Build query
        query_parts = [f"'{folder_id}' in parents", "trashed=false"]

        if mime_type_filter:
            query_parts.append(f"mimeType='{mime_type_filter}'")

        query = " and ".join(query_parts)

        # Request files
        results = []
        page_token = None

        while True:
            response = self.service.files().list(
                q=query,
                pageSize=min(100, max_results - len(results)),
                fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime)",
                pageToken=page_token
            ).execute()

            files = response.get('files', [])
            results.extend(files)

            # Check if we have more pages and haven't reached max_results
            page_token = response.get('nextPageToken', None)
            if page_token is None or len(results) >= max_results:
                break

        return results[:max_results]

    def list_video_files(
        self,
        folder_id: Optional[str] = None,
        extensions: List[str] = None
    ) -> List[Dict]:
        """
        List video files in a folder

        Args:
            folder_id: Google Drive folder ID
            extensions: List of video extensions to filter (e.g., ['.mp4', '.avi'])

        Returns:
            List of video file dictionaries
        """
        if extensions is None:
            extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']

        all_files = self.list_files(folder_id=folder_id)

        # Filter by extension
        video_files = [
            f for f in all_files
            if any(f['name'].lower().endswith(ext) for ext in extensions)
        ]

        return video_files

    def download_file(
        self,
        file_id: str,
        destination_path: str,
        chunk_size: int = 1024 * 1024 * 10  # 10MB chunks
    ) -> str:
        """
        Download a file from Google Drive

        Args:
            file_id: Google Drive file ID
            destination_path: Local path to save the file
            chunk_size: Download chunk size in bytes

        Returns:
            Path to downloaded file
        """
        request = self.service.files().get_media(fileId=file_id)

        destination_path = Path(destination_path)
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        with open(destination_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request, chunksize=chunk_size)
            done = False

            while not done:
                status, done = downloader.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"Download progress: {progress}%", end='\r')

        print(f"\n✅ Downloaded: {destination_path}")
        return str(destination_path)

    def get_file_info(self, file_id: str) -> Dict:
        """
        Get detailed information about a file

        Args:
            file_id: Google Drive file ID

        Returns:
            Dictionary with file metadata
        """
        file_info = self.service.files().get(
            fileId=file_id,
            fields="id, name, mimeType, size, createdTime, modifiedTime, parents, webViewLink"
        ).execute()

        return file_info


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
        size_mb = int(file.get('size', 0)) / (1024 * 1024) if 'size' in file else 0

        print(f"{i:3d}. {name}")
        print(f"     ID: {file_id}")

        if show_size and size_mb > 0:
            print(f"     Size: {size_mb:.2f} MB")

        print()


# Example usage
if __name__ == "__main__":
    # Validate settings first
    try:
        settings.validate_settings()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        exit(1)

    # Initialize manager
    print("Authenticating with Google Drive...")
    manager = GoogleDriveManager()

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
        #     file_id=first_video['id'],
        #     destination_path=f"./downloads/{first_video['name']}"
        # )
