from pathlib import Path

import httpx

from marketing_agent.config.settings import settings
from marketing_agent.utils.logger import get_logger

logger = get_logger(__name__)


class SlackMediaService:
    def __init__(self):
        self.bot_token = settings.slack_bot_token

        self.headers = {
            "Authorization": f"Bearer {self.bot_token}",
        }

    def get_file_info(
        self,
        file_id: str,
    ) -> dict:
        response = httpx.get(
            "https://slack.com/api/files.info",
            headers=self.headers,
            params={
                "file": file_id,
            },
            timeout=30.0,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("ok"):
            raise RuntimeError(
                f"Slack files.info failed: "
                f"{data.get('error')}"
            )

        return data["file"]

    def download_file(
        self,
        file_id: str,
        destination_dir: str | Path,
    ) -> str:
        file_info = self.get_file_info(
            file_id=file_id
        )

        file_name = file_info["name"]

        download_url = (
            file_info.get("url_private_download")
            or file_info.get("url_private")
        )

        if not download_url:
            raise RuntimeError(
                f"No download URL for Slack file: {file_id}"
            )

        destination_dir = Path(
            destination_dir
        )

        destination_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination_path = (
            destination_dir / file_name
        )

        response = httpx.get(
            download_url,
            headers=self.headers,
            timeout=60.0,
            follow_redirects=True,
        )

        response.raise_for_status()

        destination_path.write_bytes(
            response.content
        )

        logger.info(
            "Downloaded Slack file: %s -> %s",
            file_name,
            destination_path,
        )

        return str(destination_path)