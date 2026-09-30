from marketing_agent.models.content_request import (
    ContentImage,
    ContentRequest,
)
from marketing_agent.models.platform_draft import (
    PlatformDraft,
)
from marketing_agent.services.slack_media_service import (
    SlackMediaService,
)
from marketing_agent.services.temporary_storage_service import (
    TemporaryStorageService,
)


class ContentRequestService:
    def __init__(self):
        self.storage = TemporaryStorageService()
        self.slack_media = SlackMediaService()

    def create_request(
        self,
        source_text: str,
        drafts: list[PlatformDraft],
        image_paths: list[str] | None = None,
        slack_file_ids: list[str] | None = None,
    ) -> ContentRequest:
        request = ContentRequest(
            source_text=source_text,
            drafts=drafts,
            status="pending_review",
        )

        image_paths = image_paths or []
        slack_file_ids = slack_file_ids or []

        images = []

        for index, image_path in enumerate(image_paths):
            copied_path = self.storage.copy_image(
                request_id=request.request_id,
                source_path=image_path,
            )

            slack_file_id = None

            if index < len(slack_file_ids):
                slack_file_id = slack_file_ids[index]

            images.append(
                ContentImage(
                    slack_file_id=slack_file_id,
                    local_path=copied_path,
                )
            )

        request.images = images

        self._assign_images_to_drafts(request)

        self.storage.save_request(request)

        return request

    def create_request_from_slack(
        self,
        source_text: str,
        drafts: list[PlatformDraft],
        slack_file_ids: list[str],
    ) -> ContentRequest:
        request = ContentRequest(
            source_text=source_text,
            drafts=drafts,
            status="pending_review",
        )

        request_dir = self.storage.create_request_dir(
            request.request_id
        )

        image_dir = request_dir / "images"

        images = []

        for file_id in slack_file_ids:
            local_path = self.slack_media.download_file(
                file_id=file_id,
                destination_dir=image_dir,
            )

            images.append(
                ContentImage(
                    slack_file_id=file_id,
                    local_path=local_path,
                )
            )

        request.images = images

        self._assign_images_to_drafts(request)

        self.storage.save_request(request)

        return request

    def get_request(
        self,
        request_id: str,
    ) -> ContentRequest:
        return self.storage.load_request(
            request_id
        )
        
    def update_draft(
    self,
    request_id: str,
    platform: str,
    title: str | None = None,
    body: str | None = None,
    hashtags: list[str] | None = None,
    ) -> ContentRequest:
        request = self.get_request(
            request_id=request_id
        )

        draft = next(
            (
                draft
                for draft in request.drafts
                if draft.platform == platform
            ),
            None,
        )

        if draft is None:
            raise ValueError(
                f"Draft not found: platform={platform}"
            )

        if title is not None:
            draft.title = title

        if body is not None:
            draft.body = body

        if hashtags is not None:
            draft.hashtags = hashtags

        draft.status = "pending_review"

        self.storage.save_request(
            request
        )

        return request

    def delete_request(
        self,
        request_id: str,
    ) -> None:
        self.storage.delete_request(
            request_id
        )

    def approve_draft(
    self,
    request_id: str,
    platform: str,
    ) -> ContentRequest:
        request = self.get_request(
            request_id=request_id
        )

        draft = next(
            (
                draft
                for draft in request.drafts
                if draft.platform == platform
            ),
            None,
        )

        if draft is None:
            raise ValueError(
                f"Draft not found: platform={platform}"
            )

        draft.status = "approved"

        self.storage.save_request(
            request
        )

        return request
    
    def get_draft(
        self,
        request_id: str,
        platform: str,
    ):
        request = self.get_request(
            request_id=request_id
        )

        draft = next(
            (
                draft
                for draft in request.drafts
                if draft.platform == platform
            ),
            None,
        )

        if draft is None:
            raise ValueError(
                f"Draft not found: platform={platform}"
            )

        return request, draft
    def _assign_images_to_drafts(
        self,
        request: ContentRequest,
    ) -> None:
        image_indexes = list(
            range(len(request.images))
        )

        for draft in request.drafts:
            draft.image_indexes = image_indexes