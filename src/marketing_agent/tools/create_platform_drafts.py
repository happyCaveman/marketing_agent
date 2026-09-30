import argparse
import json

from marketing_agent.models.platform_draft import (
    PlatformDraft,
)
from marketing_agent.services.content_request_service import (
    ContentRequestService,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--source-text",
        required=True,
        type=str,
    )

    parser.add_argument(
        "--naver-title",
        type=str,
        default=None,
    )

    parser.add_argument(
        "--naver-body",
        required=True,
        type=str,
    )

    parser.add_argument(
        "--instagram-body",
        required=True,
        type=str,
    )

    parser.add_argument(
        "--instagram-hashtags",
        type=str,
        required=True,
        help="Comma-separated Instagram hashtags",
    )

    parser.add_argument(
        "--threads-body",
        required=True,
        type=str,
    )

    parser.add_argument(
        "--slack-file-ids",
        type=str,
        default="",
    )

    args = parser.parse_args()

    hashtags = [
        tag.strip()
        for tag in args.instagram_hashtags.split(",")
        if tag.strip()
    ]

    slack_file_ids = [
        file_id.strip()
        for file_id in args.slack_file_ids.split(",")
        if file_id.strip()
    ]

    drafts = [
        PlatformDraft(
            platform="naver_blog",
            title=args.naver_title,
            body=args.naver_body,
        ),
        PlatformDraft(
            platform="instagram",
            body=args.instagram_body,
            hashtags=hashtags,
        ),
        PlatformDraft(
            platform="threads",
            body=args.threads_body,
        ),
    ]

    service = ContentRequestService()

    request = service.create_request_from_slack(
        source_text=args.source_text,
        drafts=drafts,
        slack_file_ids=slack_file_ids,
    )

    print(
        json.dumps(
            request.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()