import argparse
import asyncio
import json

from marketing_agent.graphs.learning_content.graph import (
    learning_content_graph,
)


async def generate_learning_content(
    source_text: str,
    slack_channel_id: str,
    slack_message_ts: str,
    slack_file_ids: list[str] | None = None,
) -> dict:
    result = await learning_content_graph.ainvoke(
        {
            "source_text": source_text,
            "slack_channel_id": slack_channel_id,
            "slack_message_ts": slack_message_ts,
            "slack_file_ids": slack_file_ids or [],
        }
    )

    return result


async def async_main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate Learning marketing content "
            "with LangGraph"
        )
    )

    parser.add_argument(
        "--source-text",
        required=True,
        type=str,
    )

    parser.add_argument(
        "--slack-channel-id",
        required=True,
        type=str,
    )

    parser.add_argument(
        "--slack-message-ts",
        required=True,
        type=str,
    )

    parser.add_argument(
        "--slack-file-ids",
        type=str,
        default="",
        help=(
            "Comma-separated Slack file IDs"
        ),
    )

    args = parser.parse_args()

    slack_file_ids = [
        file_id.strip()
        for file_id in args.slack_file_ids.split(",")
        if file_id.strip()
    ]

    result = await generate_learning_content(
        source_text=args.source_text,
        slack_channel_id=args.slack_channel_id,
        slack_message_ts=args.slack_message_ts,
        slack_file_ids=slack_file_ids,
    )

    output = {
        "request_id": result.get(
            "request_id"
        ),
        "drafts": result.get(
            "drafts",
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

    print(
        json.dumps(
            output,
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