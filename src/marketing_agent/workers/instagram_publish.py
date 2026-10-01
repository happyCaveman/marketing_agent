import asyncio

import httpx

from marketing_agent.config.settings import settings
from marketing_agent.services.slack_notification_service import (
    SlackNotificationService,
)
from marketing_agent.utils.logger import get_logger


logger = get_logger(__name__)


INSTAGRAM_API_BASE_URL = "https://graph.instagram.com"


class InstagramPublishWorker:
    def __init__(
        self,
        slack_channel_id: str,
    ):
        self.slack_channel_id = slack_channel_id

        self.slack_notification_service = (
            SlackNotificationService()
        )

        self.access_token = (
            settings.instagram_access_token
        )

        self.account_id = (
            settings.instagram_account_id
        )

    async def publish(
        self,
        body: str,
        hashtags: list[str],
        image_urls: list[str],
    ) -> str:
        caption = self._build_caption(
            body=body,
            hashtags=hashtags,
        )

        try:
            if not image_urls:
                raise RuntimeError(
                    "Instagram post requires at least one image."
                )

            if len(image_urls) == 1:
                media_id = await self._publish_single_image(
                    image_url=image_urls[0],
                    caption=caption,
                )

            else:
                media_id = await self._publish_carousel(
                    image_urls=image_urls,
                    caption=caption,
                )

            logger.info(
                "Instagram published successfully: media_id=%s",
                media_id,
            )

            return media_id

        except Exception as error:
            logger.exception(
                "Instagram publish failed."
            )

            self.slack_notification_service.notify_publish_failure(
                channel_id=self.slack_channel_id,
                platform="Instagram",
                step="Instagram 게시",
                error=str(error),
            )

            raise

    def _build_caption(
        self,
        body: str,
        hashtags: list[str],
    ) -> str:
        hashtag_text = " ".join(
            hashtags
        )

        if not hashtag_text:
            return body

        return (
            f"{body}\n\n"
            f"{hashtag_text}"
        )

    async def _create_media(
        self,
        image_url: str,
        caption: str,
    ) -> str:
        url = (
            f"{INSTAGRAM_API_BASE_URL}/"
            f"{self.account_id}/media"
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": self.access_token,
                },
                timeout=30.0,
            )

        if response.is_error:
            raise RuntimeError(
                f"Instagram media creation failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        data = response.json()

        creation_id = data.get("id")

        if not creation_id:
            raise RuntimeError(
                "Instagram creation_id was not returned."
            )

        logger.info(
            "Instagram media container created: %s",
            creation_id,
        )

        return creation_id

    async def _wait_until_container_ready(
        self,
        creation_id: str,
        max_attempts: int = 10,
        interval_seconds: int = 2,
    ) -> None:
        url = (
            f"{INSTAGRAM_API_BASE_URL}/"
            f"{creation_id}"
        )

        async with httpx.AsyncClient() as client:
            for attempt in range(
                1,
                max_attempts + 1,
            ):
                response = await client.get(
                    url,
                    params={
                        "fields": "status_code",
                        "access_token": self.access_token,
                    },
                    timeout=30.0,
                )

                if response.is_error:
                    raise RuntimeError(
                        "Instagram container status check failed: "
                        f"{response.status_code} "
                        f"{response.text}"
                    )

                data = response.json()

                status_code = data.get(
                    "status_code"
                )

                logger.info(
                    "Instagram container status: "
                    "attempt=%s status=%s",
                    attempt,
                    status_code,
                )

                if status_code == "FINISHED":
                    return

                if status_code in {
                    "ERROR",
                    "EXPIRED",
                }:
                    raise RuntimeError(
                        "Instagram media container failed: "
                        f"{status_code}"
                    )

                await asyncio.sleep(
                    interval_seconds
                )

        raise TimeoutError(
            "Instagram media container was not ready "
            "within the allowed time."
        )

    async def _publish_media(
        self,
        creation_id: str,
    ) -> str:
        url = (
            f"{INSTAGRAM_API_BASE_URL}/"
            f"{self.account_id}/media_publish"
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={
                    "creation_id": creation_id,
                    "access_token": self.access_token,
                },
                timeout=30.0,
            )

        if response.is_error:
            raise RuntimeError(
                f"Instagram media publish failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        data = response.json()

        media_id = data.get("id")

        if not media_id:
            raise RuntimeError(
                "Instagram media_id was not returned."
            )

        return media_id
    
    async def _publish_single_image(
        self,
        image_url: str,
        caption: str,
    ) -> str:
        creation_id = await self._create_media(
            image_url=image_url,
            caption=caption,
        )

        await self._wait_until_container_ready(
            creation_id=creation_id,
        )

        return await self._publish_media(
            creation_id=creation_id,
        )
        
    async def _create_carousel_child(
        self,
        image_url: str,
    ) -> str:
        url = (
            f"{INSTAGRAM_API_BASE_URL}/"
            f"{self.account_id}/media"
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={
                    "image_url": image_url,
                    "is_carousel_item": "true",
                    "access_token": self.access_token,
                },
                timeout=30.0,
            )

        if response.is_error:
            raise RuntimeError(
                "Instagram carousel child creation failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        child_id = response.json().get("id")

        if not child_id:
            raise RuntimeError(
                "Instagram carousel child id was not returned."
            )

        return child_id
    
    async def _create_carousel(
        self,
        child_ids: list[str],
        caption: str,
    ) -> str:
        url = (
            f"{INSTAGRAM_API_BASE_URL}/"
            f"{self.account_id}/media"
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={
                    "media_type": "CAROUSEL",
                    "children": ",".join(child_ids),
                    "caption": caption,
                    "access_token": self.access_token,
                },
                timeout=30.0,
            )

        if response.is_error:
            raise RuntimeError(
                "Instagram carousel creation failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        creation_id = response.json().get("id")

        if not creation_id:
            raise RuntimeError(
                "Instagram carousel creation_id was not returned."
            )

        return creation_id
    
    async def _publish_carousel(
        self,
        image_urls: list[str],
        caption: str,
    ) -> str:
        child_ids = []

        for image_url in image_urls:
            child_id = await self._create_carousel_child(
                image_url=image_url,
            )

            await self._wait_until_container_ready(
                creation_id=child_id,
            )

            child_ids.append(
                child_id
            )

        carousel_id = await self._create_carousel(
            child_ids=child_ids,
            caption=caption,
        )

        await self._wait_until_container_ready(
            creation_id=carousel_id,
        )

        return await self._publish_media(
            creation_id=carousel_id,
        )