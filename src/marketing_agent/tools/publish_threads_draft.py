import argparse
import asyncio
import json

from marketing_agent.services.content_request_service import (
    ContentRequestService,
)
from marketing_agent.services.media_url_service import (
    MediaUrlService,
)
from marketing_agent.workers.threads_publish import (
    ThreadsPublishWorker,
)


async def publish(
    request_id: str,
    slack_channel_id: str,
) -> None:
    content_request_service = (
        ContentRequestService()
    )

    media_url_service = (
        MediaUrlService()
    )

    request, draft = (
        content_request_service.get_draft(
            request_id=request_id,
            platform="threads",
        )
    )

    if draft.status != "approved":
        raise RuntimeError(
            "Threads draft must be approved "
            "before publishing."
        )

    image_urls = []

    for image_index in draft.image_indexes:
        if image_index >= len(request.images):
            raise RuntimeError(
                f"Invalid image index: {image_index}"
            )

        image = request.images[
            image_index
        ]

        image_url = (
            media_url_service.create_public_url(
                request_id=request_id,
                local_path=image.local_path,
            )
        )

        image_urls.append(
            image_url
        )
        
    worker = ThreadsPublishWorker(
        slack_channel_id=slack_channel_id,
    )

    try:
        media_id = await worker.publish(
            body=draft.body,
            image_urls=image_urls,
        )

        request = (
            content_request_service.mark_draft_published(
                request_id=request_id,
                platform="threads",
            )
        )
        
        content_request_service.cleanup_if_completed(
                            request_id=request_id
                        )

        print(
            json.dumps(
                {
                    "status": "published",
                    "platform": "threads",
                    "media_id": media_id,
                    "image_url": image_url,
                    "request": request.model_dump(
                        mode="json"
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )
        )

    except Exception:
        content_request_service.mark_draft_failed(
            request_id=request_id,
            platform="threads",
        )

        raise


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--request-id",
        required=True,
    )

    parser.add_argument(
        "--slack-channel-id",
        required=True,
    )

    args = parser.parse_args()

    asyncio.run(
        publish(
            request_id=args.request_id,
            slack_channel_id=args.slack_channel_id,
        )
    )


if __name__ == "__main__":
    main()