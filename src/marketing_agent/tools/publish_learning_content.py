import argparse
import asyncio
import json

from marketing_agent.graphs.publish_content.graph import (
    publish_content_graph,
)


async def publish_learning_content(
    instruction: str,
    request_id: str,
    slack_channel_id: str,
    slack_message_ts: str,
) -> dict:
    result = await publish_content_graph.ainvoke(
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
        "approval_platforms": result.get(
            "approval_platforms",
            [],
        ),
        "publish_platforms": result.get(
            "publish_platforms",
            [],
        ),
        "publish_results": result.get(
            "publish_results",
            [],
        ),
        "publish_completed": result.get(
            "publish_completed",
            False,
        ),
        "cleanup_completed": result.get(
            "cleanup_completed",
            False,
        ),
    }


async def async_main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Approve and publish Learning "
            "marketing content with LangGraph"
        )
    )

    parser.add_argument(
        "--instruction",
        required=True,
        type=str,
        help=(
            "User approval or publish instruction"
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

    result = await publish_learning_content(
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