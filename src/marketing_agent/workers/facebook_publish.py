import json

import httpx

from marketing_agent.config.settings import (
    settings,
)
from marketing_agent.services.slack_notification_service import (
    SlackNotificationService,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


FACEBOOK_GRAPH_API_BASE_URL = (
    "https://graph.facebook.com/v26.0"
)


class FacebookPublishWorker:
    def __init__(
        self,
        slack_channel_id: str,
    ):
        self.slack_channel_id = (
            slack_channel_id
        )

        self.slack_notification_service = (
            SlackNotificationService()
        )

        self.page_id = (
            settings.facebook_page_id
        )

        self.access_token = (
            settings.facebook_page_access_token
        )

    async def publish(
        self,
        body: str,
        hashtags: list[str],
        image_urls: list[str],
    ) -> str:
        message = self._build_message(
            body=body,
            hashtags=hashtags,
        )

        try:
            if image_urls:
                post_id = (
                    await self._publish_with_images(
                        message=message,
                        image_urls=image_urls,
                    )
                )

            else:
                post_id = (
                    await self._publish_text_only(
                        message=message,
                    )
                )

            logger.info(
                "Facebook published successfully: "
                "post_id=%s",
                post_id,
            )

            return post_id

        except Exception as error:
            logger.exception(
                "Facebook publish failed."
            )

            self.slack_notification_service.notify_publish_failure(
                channel_id=self.slack_channel_id,
                platform="Facebook",
                step="Facebook 게시",
                error=str(error),
            )

            raise

    def _build_message(
        self,
        body: str,
        hashtags: list[str],
    ) -> str:
        hashtag_text = " ".join(
            hashtags
        )

        if not hashtag_text:
            return body.strip()

        return (
            f"{body.strip()}\n\n"
            f"{hashtag_text}"
        )

    async def _publish_text_only(
        self,
        message: str,
    ) -> str:
        url = (
            f"{FACEBOOK_GRAPH_API_BASE_URL}/"
            f"{self.page_id}/feed"
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={
                    "message": message,
                    "access_token": (
                        self.access_token
                    ),
                },
                timeout=30.0,
            )

        if response.is_error:
            raise RuntimeError(
                "Facebook text post failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        data = response.json()

        post_id = data.get(
            "id"
        )

        if not post_id:
            raise RuntimeError(
                "Facebook post id was not returned."
            )

        return post_id

    async def _publish_with_images(
        self,
        message: str,
        image_urls: list[str],
    ) -> str:
        media_ids = []

        for image_url in image_urls:
            media_id = (
                await self._upload_unpublished_photo(
                    image_url=image_url,
                )
            )

            media_ids.append(
                media_id
            )

        return await self._create_feed_post(
            message=message,
            media_ids=media_ids,
        )

    async def _upload_unpublished_photo(
        self,
        image_url: str,
    ) -> str:
        url = (
            f"{FACEBOOK_GRAPH_API_BASE_URL}/"
            f"{self.page_id}/photos"
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={
                    "url": image_url,
                    "published": "false",
                    "access_token": (
                        self.access_token
                    ),
                },
                timeout=60.0,
            )

        if response.is_error:
            raise RuntimeError(
                "Facebook photo upload failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        data = response.json()

        media_id = data.get(
            "id"
        )

        if not media_id:
            raise RuntimeError(
                "Facebook photo id "
                "was not returned."
            )

        logger.info(
            "Facebook unpublished photo "
            "uploaded: media_id=%s",
            media_id,
        )

        return media_id

    async def _create_feed_post(
        self,
        message: str,
        media_ids: list[str],
    ) -> str:
        url = (
            f"{FACEBOOK_GRAPH_API_BASE_URL}/"
            f"{self.page_id}/feed"
        )

        data = {
            "message": message,
            "access_token": (
                self.access_token
            ),
        }

        for index, media_id in enumerate(
            media_ids
        ):
            data[
                f"attached_media[{index}]"
            ] = json.dumps(
                {
                    "media_fbid": media_id,
                }
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data=data,
                timeout=60.0,
            )

        if response.is_error:
            raise RuntimeError(
                "Facebook feed post failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        result = response.json()

        post_id = result.get(
            "id"
        )

        if not post_id:
            raise RuntimeError(
                "Facebook feed post id "
                "was not returned."
            )

        return post_id