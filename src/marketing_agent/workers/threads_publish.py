import asyncio

import httpx

from marketing_agent.config.settings import settings
from marketing_agent.services.slack_notification_service import (
    SlackNotificationService,
)
from marketing_agent.utils.logger import get_logger


logger = get_logger(__name__)


THREADS_API_BASE_URL = "https://graph.threads.net/v1.0"


class ThreadsPublishWorker:
    def __init__(
        self,
        slack_channel_id: str,
    ):
        self.slack_channel_id = slack_channel_id
        self.slack_notification_service = (
            SlackNotificationService()
        )

        self.access_token = (
            settings.threads_access_token
        )

        self.user_id = (
            settings.threads_user_id
        )

    async def publish(
        self,
        body: str,
        image_urls: list[str] | None = None,
    ) -> str:
        image_urls = image_urls or []

        try:
            if not image_urls:
                creation_id = await self._create_text_container(
                    body=body,
                )

            elif len(image_urls) == 1:
                creation_id = await self._create_image_container(
                    body=body,
                    image_url=image_urls[0],
                )

            else:
                creation_id = await self._create_carousel_container(
                    body=body,
                    image_urls=image_urls,
                )

            media_id = await self._publish_container(
                creation_id=creation_id,
            )

            logger.info(
                "Threads published successfully: media_id=%s",
                media_id,
            )

            return media_id

        except Exception as error:
            logger.exception(
                "Threads publish failed."
            )

            self.slack_notification_service.notify_publish_failure(
                channel_id=self.slack_channel_id,
                platform="Threads",
                step="Threads 게시",
                error=str(error),
            )

            raise

    async def _create_container(
        self,
        body: str,
        image_url: str | None,
    ) -> str:
        url = (
            f"{THREADS_API_BASE_URL}/"
            f"{self.user_id}/threads"
        )

        data = {
            "text": body,
            "access_token": self.access_token,
        }

        if image_url:
            data["media_type"] = "IMAGE"
            data["image_url"] = image_url
        else:
            data["media_type"] = "TEXT"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data=data,
                timeout=30.0,
            )

        if response.is_error:
            raise RuntimeError(
                f"Threads container creation failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        creation_id = response.json().get("id")

        if not creation_id:
            raise RuntimeError(
                "Threads creation_id was not returned."
            )

        logger.info(
            "Threads container created: %s",
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
            f"{THREADS_API_BASE_URL}/"
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
                        "fields": "status",
                        "access_token": self.access_token,
                    },
                    timeout=30.0,
                )

                if response.is_error:
                    raise RuntimeError(
                        "Threads container status check failed: "
                        f"{response.status_code} "
                        f"{response.text}"
                    )

                status = response.json().get(
                    "status"
                )

                logger.info(
                    "Threads container status: "
                    "attempt=%s status=%s",
                    attempt,
                    status,
                )

                if status in {
                    "FINISHED",
                    "PUBLISHED",
                }:
                    return

                if status in {
                    "ERROR",
                    "EXPIRED",
                }:
                    raise RuntimeError(
                        f"Threads container failed: {status}"
                    )

                await asyncio.sleep(
                    interval_seconds
                )

        raise TimeoutError(
            "Threads container was not ready "
            "within the allowed time."
        )

    async def _publish_container(
        self,
        creation_id: str,
    ) -> str:
        url = (
            f"{THREADS_API_BASE_URL}/"
            f"{self.user_id}/threads_publish"
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
                f"Threads publish failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        media_id = response.json().get("id")

        if not media_id:
            raise RuntimeError(
                "Threads media_id was not returned."
            )

        return media_id
    
    async def _create_text_container(
        self,
        body: str,
    ) -> str:
        url = (
            f"{THREADS_API_BASE_URL}/"
            f"{self.user_id}/threads"
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={
                    "media_type": "TEXT",
                    "text": body,
                    "access_token": self.access_token,
                },
                timeout=30.0,
            )

        if response.is_error:
            raise RuntimeError(
                f"Threads text container creation failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        creation_id = response.json().get("id")

        if not creation_id:
            raise RuntimeError(
                "Threads creation_id was not returned."
            )

        return creation_id
    
    async def _create_image_container(
        self,
        body: str,
        image_url: str,
    ) -> str:
        url = (
            f"{THREADS_API_BASE_URL}/"
            f"{self.user_id}/threads"
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={
                    "media_type": "IMAGE",
                    "image_url": image_url,
                    "text": body,
                    "access_token": self.access_token,
                },
                timeout=30.0,
            )

        if response.is_error:
            raise RuntimeError(
                f"Threads image container creation failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        creation_id = response.json().get("id")

        if not creation_id:
            raise RuntimeError(
                "Threads creation_id was not returned."
            )

        return creation_id
    
    
    async def _create_carousel_item(
        self,
        image_url: str,
    ) -> str:
        url = (
            f"{THREADS_API_BASE_URL}/"
            f"{self.user_id}/threads"
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={
                    "media_type": "IMAGE",
                    "image_url": image_url,
                    "is_carousel_item": "true",
                    "access_token": self.access_token,
                },
                timeout=30.0,
            )

        if response.is_error:
            raise RuntimeError(
                "Threads carousel item creation failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        child_id = response.json().get("id")

        if not child_id:
            raise RuntimeError(
                "Threads carousel child id was not returned."
            )

        return child_id
    
    async def _create_carousel_container(
        self,
        body: str,
        image_urls: list[str],
    ) -> str:
        if len(image_urls) < 2:
            raise ValueError(
                "Threads carousel requires at least 2 images."
            )

        if len(image_urls) > 20:
            raise ValueError(
                "Threads carousel supports up to 20 media items."
            )

        child_ids = []

        for image_url in image_urls:
            child_id = await self._create_carousel_item(
                image_url=image_url,
            )

            child_ids.append(
                child_id
            )

        url = (
            f"{THREADS_API_BASE_URL}/"
            f"{self.user_id}/threads"
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={
                    "media_type": "CAROUSEL",
                    "children": ",".join(child_ids),
                    "text": body,
                    "access_token": self.access_token,
                },
                timeout=30.0,
            )

        if response.is_error:
            raise RuntimeError(
                "Threads carousel creation failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        creation_id = response.json().get("id")

        if not creation_id:
            raise RuntimeError(
                "Threads carousel creation_id was not returned."
            )

        return creation_id