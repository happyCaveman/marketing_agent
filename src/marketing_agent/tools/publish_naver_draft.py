import argparse
import asyncio
import json

from marketing_agent.services.content_request_service import (
    ContentRequestService,
)
from marketing_agent.workers.naver_publish import (
    NaverPublishWorker,
)


async def publish(
    request_id: str,
    slack_channel_id: str,
) -> None:
    service = ContentRequestService()

    request, draft = service.get_draft(
        request_id=request_id,
        platform="naver_blog",
    )

    if draft.status != "approved":
        raise RuntimeError(
            "Naver draft must be approved before publishing."
        )

    image_paths = [
        request.images[index].local_path
        for index in draft.image_indexes
    ]

    worker = NaverPublishWorker(
        slack_channel_id=slack_channel_id,
    )

    try:
        await worker.publish(
            title=draft.title or "",
            body=draft.body,
            image_paths=image_paths,
        )

        request = service.mark_draft_published(
            request_id=request_id,
            platform="naver_blog",
        )
        
        service.cleanup_if_completed(
            request_id=request_id
        )

        print(
            json.dumps(
                request.model_dump(mode="json"),
                ensure_ascii=False,
                indent=2,
            )
        )

    except Exception:
        service.mark_draft_failed(
            request_id=request_id,
            platform="naver_blog",
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