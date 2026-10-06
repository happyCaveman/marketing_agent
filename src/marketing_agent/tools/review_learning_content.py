import argparse
import asyncio
import json

from marketing_agent.graphs.review_content.graph import (
    review_content_graph,
)


async def review_learning_content(
    instruction: str,
    request_id: str,
    slack_channel_id: str,
    slack_message_ts: str,
) -> dict:
    result = await review_content_graph.ainvoke(
        {
            "instruction": instruction,
            "request_id": request_id,
            "slack_channel_id": slack_channel_id,
            "slack_message_ts": slack_message_ts,
        }
    )

    return {
        "request_id": result.get(
            "request_id"
        ),
        "revision_actions": result.get(
            "revision_actions",
            [],
        ),
        "approval_platforms": result.get(
            "approval_platforms",
            [],
        ),
        "updated_drafts": result.get(
            "updated_drafts",
            [],
        ),
        "validation_errors": result.get(
            "validation_errors",
            [],
        ),
        "retry_count": result.get(
            "retry_count",
            0,
        ),
    }


async def async_main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Review and update Learning "
            "marketing content with LangGraph"
        )
    )

    parser.add_argument(
        "--instruction",
        required=True,
        type=str,
        help=(
            "User review instruction"
        ),
    )

    parser.add_argument(
        "--request-id",
        required=True,
        type=str,
        help=(
            "Existing ContentRequest ID"
        ),
    )

    parser.add_argument(
        "--slack-channel-id",
        required=True,
        type=str,
        help=(
            "Slack channel ID"
        ),
    )

    parser.add_argument(
        "--slack-message-ts",
        required=True,
        type=str,
        help=(
            "Slack message or thread timestamp"
        ),
    )

    args = parser.parse_args()

    result = await review_learning_content(
        instruction=args.instruction,
        request_id=args.request_id,
        slack_channel_id=args.slack_channel_id,
        slack_message_ts=args.slack_message_ts,
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )


def main() -> None:
    asyncio.run(
        async_main()
    )


if __name__ == "__main__":
    main()