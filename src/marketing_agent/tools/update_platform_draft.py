import argparse
import json
import re

from marketing_agent.services.content_request_service import (
    ContentRequestService,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--request-id",
        required=True,
        type=str,
    )

    parser.add_argument(
        "--platform",
        required=True,
        choices=[
            "naver_blog",
            "instagram",
            "threads",
        ],
    )

    parser.add_argument(
        "--title",
        type=str,
        default=None,
    )

    parser.add_argument(
        "--body",
        type=str,
        default=None,
    )

    parser.add_argument(
        "--hashtags",
        type=str,
        default=None,
    )

    args = parser.parse_args()

    hashtags = None

    hashtags = None

    if args.hashtags is not None:
        hashtags = [
            tag
            for tag in re.split(
                r"[,\s]+",
                args.hashtags.strip(),
            )
            if tag
        ]

    service = ContentRequestService()

    request = service.update_draft(
        request_id=args.request_id,
        platform=args.platform,
        title=args.title,
        body=args.body,
        hashtags=hashtags,
    )

    print(
        json.dumps(
            request.model_dump(
                mode="json"
            ),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()