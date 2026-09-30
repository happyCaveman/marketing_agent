import json
import shutil
from pathlib import Path

from marketing_agent.config.settings import (
    PROJECT_ROOT,
    settings,
)
from marketing_agent.models.content_request import (
    ContentRequest,
)


class TemporaryStorageService:
    def __init__(self):
        storage_path = Path(
            settings.temp_storage_dir
        )

        if storage_path.is_absolute():
            self.base_dir = storage_path
        else:
            self.base_dir = (
                PROJECT_ROOT / storage_path
            )

        self.base_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def create_request_dir(
        self,
        request_id: str,
    ) -> Path:
        request_dir = (
            self.base_dir / request_id
        )

        (request_dir / "images").mkdir(
            parents=True,
            exist_ok=True,
        )

        return request_dir

    def save_request(
        self,
        request: ContentRequest,
    ) -> None:
        request_dir = self.create_request_dir(
            request.request_id
        )

        request_path = (
            request_dir / "request.json"
        )

        request_path.write_text(
            request.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

    def load_request(
        self,
        request_id: str,
    ) -> ContentRequest:
        request_path = (
            self.base_dir
            / request_id
            / "request.json"
        )

        data = json.loads(
            request_path.read_text(
                encoding="utf-8"
            )
        )

        return ContentRequest(
            **data
        )

    def copy_image(
        self,
        request_id: str,
        source_path: str,
    ) -> str:
        request_dir = self.create_request_dir(
            request_id
        )

        source = Path(source_path)

        destination = (
            request_dir
            / "images"
            / source.name
        )

        shutil.copy2(
            source,
            destination,
        )

        return str(destination)

    def delete_request(
        self,
        request_id: str,
    ) -> None:
        request_dir = (
            self.base_dir / request_id
        )

        if request_dir.exists():
            shutil.rmtree(
                request_dir
            )