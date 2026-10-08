from pathlib import Path

from supabase import create_client

from marketing_agent.config.settings import (
    settings,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


class SupabaseStorageService:
    def __init__(self):
        self.client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )

        self.bucket = (
            settings.supabase_storage_bucket
        )

    def upload_image(
        self,
        request_id: str,
        local_path: str,
    ) -> str:
        file_path = Path(
            local_path
        )

        object_path = (
            f"{request_id}/"
            f"{file_path.name}"
        )

        with file_path.open(
            "rb"
        ) as file:
            self.client.storage.from_(
                self.bucket
            ).upload(
                path=object_path,
                file=file,
                file_options={
                    "upsert": "true",
                },
            )

        public_url = (
            self.client.storage.from_(
                self.bucket
            ).get_public_url(
                object_path
            )
        )

        logger.info(
            "Uploaded image to Supabase: "
            "request_id=%s path=%s",
            request_id,
            object_path,
        )

        return public_url

    def delete_request_images(
        self,
        request_id: str,
    ) -> None:
        files = (
            self.client.storage.from_(
                self.bucket
            ).list(
                path=request_id
            )
        )

        if not files:
            logger.info(
                "No Supabase images to delete: "
                "request_id=%s",
                request_id,
            )
            return

        paths = [
            f"{request_id}/{item['name']}"
            for item in files
        ]

        self.client.storage.from_(
            self.bucket
        ).remove(
            paths
        )

        logger.info(
            "Deleted Supabase images: "
            "request_id=%s count=%s",
            request_id,
            len(paths),
        )