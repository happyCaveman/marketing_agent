from pathlib import Path
from urllib.parse import quote

from marketing_agent.config.settings import settings


class MediaUrlService:
    def create_public_url(
        self,
        request_id: str,
        local_path: str,
    ) -> str:
        filename = Path(
            local_path
        ).name

        encoded_filename = quote(
            filename
        )

        base_url = (
            settings.public_image_url.rstrip("/")
        )

        return (
            f"{base_url}"
            f"/media/{request_id}/"
            f"{encoded_filename}"
        )