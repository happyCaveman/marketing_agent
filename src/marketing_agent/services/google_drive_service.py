from io import BytesIO

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from marketing_agent.config.settings import settings
from marketing_agent.utils.logger import get_logger

logger = get_logger(__name__)


class GoogleDriveService:
    SCOPES = [
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    def __init__(self):
        credentials = Credentials.from_service_account_file(
            settings.google_service_account_file,
            scopes=self.SCOPES,
        )

        self.service = build(
            "drive",
            "v3",
            credentials=credentials,
        )

    def list_files(self, folder_id: str) -> list[dict]:
        query = f"'{folder_id}' in parents and trashed = false"

        result = (
            self.service
            .files()
            .list(
                q=query,
                fields="files(id,name,mimeType,modifiedTime)",
            )
            .execute()
        )

        files = result.get("files", [])

        logger.info(
            "Loaded %s files from Google Drive folder",
            len(files),
        )

        return files

    def download_file(
        self,
        file_id: str,
        mime_type: str,
    ) -> bytes:
        if mime_type == "application/vnd.google-apps.document":
            request = (
                self.service
                .files()
                .export_media(
                    fileId=file_id,
                    mimeType="text/plain",
                )
            )
        else:
            request = (
                self.service
                .files()
                .get_media(fileId=file_id)
            )

        buffer = BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False

        while not done:
            _, done = downloader.next_chunk()

        return buffer.getvalue()