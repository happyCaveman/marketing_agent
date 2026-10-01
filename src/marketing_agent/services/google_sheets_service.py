from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from marketing_agent.config.settings import settings
from marketing_agent.utils.logger import get_logger

logger = get_logger(__name__)


class GoogleSheetsService:
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ]

    def __init__(self):
        credentials = Credentials.from_service_account_file(
            settings.google_service_account_file,
            scopes=self.SCOPES,
        )

        self.service = build(
            "sheets",
            "v4",
            credentials=credentials,
        )

        self.spreadsheet_id = settings.google_spreadsheet_id

    def get_rows(self, sheet_name: str) -> list[list[str]]:
        range_name = f"{sheet_name}!A:E"

        result = (
            self.service
            .spreadsheets()
            .values()
            .get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
            )
            .execute()
        )

        rows = result.get("values", [])

        logger.info(
            "Loaded %s rows from Google Sheet: %s",
            len(rows),
            sheet_name,
        )

        return rows