import uuid

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
from marketing_agent.utils.logger import get_logger


logger = get_logger(__name__)


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
        slack_channel_id: str | None = None,
        slack_message_ts: str | None = None,
    ) -> ContentRequest:
        request_id = self._resolve_request_id(
            slack_channel_id=slack_channel_id,
            slack_message_ts=slack_message_ts,
        )

        existing_request = self._get_existing_request(
            request_id=request_id,
        )

        if existing_request is not None:
            return existing_request

        request = ContentRequest(
            request_id=request_id,
            source_text=source_text,
            drafts=drafts,
            status="pending_review",
            slack_channel_id=slack_channel_id,
            slack_message_ts=slack_message_ts,
        )

        image_paths = image_paths or []
        slack_file_ids = slack_file_ids or []

        images: list[ContentImage] = []

        for index, image_path in enumerate(
            image_paths
        ):
            copied_path = self.storage.copy_image(
                request_id=request.request_id,
                source_path=image_path,
            )

            slack_file_id = None

            if index < len(slack_file_ids):
                slack_file_id = (
                    slack_file_ids[index]
                )

            images.append(
                ContentImage(
                    slack_file_id=slack_file_id,
                    local_path=copied_path,
                )
            )

        request.images = images

        self._assign_images_to_drafts(
            request
        )

        self.storage.save_request(
            request
        )

        logger.info(
            "Created ContentRequest: "
            "request_id=%s "
            "channel_id=%s "
            "message_ts=%s",
            request.request_id,
            slack_channel_id,
            slack_message_ts,
        )

        return request

    def create_request_from_slack(
        self,
        source_text: str,
        drafts: list[PlatformDraft],
        slack_file_ids: list[str],
        slack_channel_id: str | None = None,
        slack_message_ts: str | None = None,
        content_type: str | None = None,
    ) -> ContentRequest:
        request_id = self._resolve_request_id(
            slack_channel_id=slack_channel_id,
            slack_message_ts=slack_message_ts,
        )

        existing_request = self._get_existing_request(
            request_id=request_id,
        )

        if existing_request is not None:
            return existing_request

        request = ContentRequest(
            request_id=request_id,
            source_text=source_text,
            content_type=content_type,
            drafts=drafts,
            status="pending_review",
            slack_channel_id=slack_channel_id,
            slack_message_ts=slack_message_ts,
        )

        request_dir = (
            self.storage.create_request_dir(
                request.request_id
            )
        )

        image_dir = (
            request_dir / "images"
        )

        images: list[ContentImage] = []

        for file_id in slack_file_ids:
            local_path = (
                self.slack_media.download_file(
                    file_id=file_id,
                    destination_dir=image_dir,
                )
            )

            images.append(
                ContentImage(
                    slack_file_id=file_id,
                    local_path=local_path,
                )
            )

        request.images = images

        self._assign_images_to_drafts(
            request
        )

        self.storage.save_request(
            request
        )

        logger.info(
            "Created Slack ContentRequest: "
            "request_id=%s "
            "channel_id=%s "
            "message_ts=%s "
            "images=%s",
            request.request_id,
            slack_channel_id,
            slack_message_ts,
            len(images),
        )

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
                "Draft not found: "
                f"platform={platform}"
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

        logger.info(
            "Updated draft: "
            "request_id=%s platform=%s",
            request_id,
            platform,
        )

        return request

    def delete_request(
        self,
        request_id: str,
    ) -> None:
        self.storage.delete_request(
            request_id=request_id
        )

        logger.info(
            "Deleted ContentRequest: "
            "request_id=%s",
            request_id,
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
                "Draft not found: "
                f"platform={platform}"
            )

        draft.status = "approved"

        self.storage.save_request(
            request
        )

        logger.info(
            "Approved draft: "
            "request_id=%s platform=%s",
            request_id,
            platform,
        )

        return request

    def get_draft(
        self,
        request_id: str,
        platform: str,
    ) -> tuple[
        ContentRequest,
        PlatformDraft,
    ]:
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
                "Draft not found: "
                f"platform={platform}"
            )

        return request, draft

    def mark_draft_published(
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
                "Draft not found: "
                f"platform={platform}"
            )

        draft.status = "published"

        self.storage.save_request(
            request
        )

        logger.info(
            "Marked draft as published: "
            "request_id=%s platform=%s",
            request_id,
            platform,
        )

        return request

    def mark_draft_failed(
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
                "Draft not found: "
                f"platform={platform}"
            )

        draft.status = "failed"

        self.storage.save_request(
            request
        )

        logger.info(
            "Marked draft as failed: "
            "request_id=%s platform=%s",
            request_id,
            platform,
        )

        return request

    def cleanup_if_completed(
        self,
        request_id: str,
    ) -> bool:
        request = self.get_request(
            request_id=request_id
        )

        if not request.drafts:
            return False

        all_published = all(
            draft.status == "published"
            for draft in request.drafts
        )

        if not all_published:
            logger.info(
                "ContentRequest cleanup skipped: "
                "request_id=%s",
                request_id,
            )

            return False

        self.storage.delete_request(
            request_id=request_id
        )

        logger.info(
            "ContentRequest cleanup completed: "
            "request_id=%s",
            request_id,
        )

        return True

    def _assign_images_to_drafts(
        self,
        request: ContentRequest,
    ) -> None:
        image_indexes = list(
            range(len(request.images))
        )

        for draft in request.drafts:
            draft.image_indexes = (
                image_indexes.copy()
            )

    def resolve_request_id(
        self,
        slack_channel_id: str,
        slack_message_ts: str,
    ) -> str:
        return self._resolve_request_id(
            slack_channel_id=slack_channel_id,
            slack_message_ts=slack_message_ts,
        )
        
    def _resolve_request_id(
        self,
        slack_channel_id: str | None,
        slack_message_ts: str | None,
    ) -> str:
        if (
            slack_channel_id is None
            and slack_message_ts is None
        ):
            return str(
                uuid.uuid4()
            )

        if (
            not slack_channel_id
            or not slack_message_ts
        ):
            raise ValueError(
                "slack_channel_id and "
                "slack_message_ts must be "
                "provided together."
            )

        idempotency_key = (
            "marketing-agent:"
            f"{slack_channel_id}:"
            f"{slack_message_ts}"
        )

        return str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                idempotency_key,
            )
        )

    def _get_existing_request(
        self,
        request_id: str,
    ) -> ContentRequest | None:
        try:
            request = self.get_request(
                request_id=request_id
            )

        except FileNotFoundError:
            return None

        logger.info(
            "Reusing existing ContentRequest: "
            "request_id=%s",
            request_id,
        )

        return request
