import asyncio

from slack_bolt import App
from slack_bolt.adapter.socket_mode import (
    SocketModeHandler,
)

from marketing_agent.config.settings import (
    settings,
)
from marketing_agent.tools.generate_learning_content import (
    generate_learning_content,
)
from marketing_agent.tools.publish_learning_content import (
    publish_learning_content,
)
from marketing_agent.tools.review_learning_content import (
    review_learning_content,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


app = App(
    token=settings.slack_bot_token,
)


@app.event("app_mention")
def handle_app_mention(
    event: dict,
    say,
) -> None:
    try:
        asyncio.run(
            _handle_message(
                event=event,
                say=say,
            )
        )

    except Exception:
        logger.exception(
            "Slack message handling failed."
        )

        say(
            text=(
                "요청 처리 중 오류가 발생했습니다. "
                "로그를 확인해 주세요."
            ),
            thread_ts=_get_reply_thread_ts(
                event
            ),
        )

@app.event("message")
def handle_thread_message(
        event: dict,
        say,
    ) -> None:
        if event.get("bot_id"):
            return

        if not event.get("thread_ts"):
            return

        text = event.get(
            "text",
            "",
        )

        # app_mention handler가 처리하도록 넘김
        if "<@" in text:
            return

        try:
            asyncio.run(
                _handle_message(
                    event=event,
                    say=say,
                )
            )

        except Exception:
            logger.exception(
                "Slack thread message handling failed."
            )

            say(
                text=(
                    "요청 처리 중 오류가 발생했습니다. "
                    "로그를 확인해 주세요."
                ),
                thread_ts=event["thread_ts"],
            )

async def _handle_message(
    event: dict,
    say,
) -> None:
    text = _clean_message_text(
        event.get(
            "text",
            "",
        )
    )

    channel_id = event[
        "channel"
    ]

    message_ts = event[
        "ts"
    ]

    thread_ts = event.get(
        "thread_ts"
    )

    files = event.get(
        "files",
        [],
    )

    slack_file_ids = [
        file["id"]
        for file in files
        if file.get("id")
    ]

    logger.info(
        "Slack message received: "
        "channel=%s ts=%s thread_ts=%s "
        "files=%s text=%s",
        channel_id,
        message_ts,
        thread_ts,
        slack_file_ids,
        text,
    )

    intent = _detect_intent(
        text=text,
        thread_ts=thread_ts,
    )

    logger.info(
        "Slack intent detected: %s",
        intent,
    )

    if intent == "generate":
        await _handle_generate(
            text=text,
            channel_id=channel_id,
            message_ts=message_ts,
            slack_file_ids=slack_file_ids,
            say=say,
        )

        return

    if intent == "review":
        await _handle_review(
            text=text,
            channel_id=channel_id,
            message_ts=message_ts,
            thread_ts=thread_ts,
            say=say,
        )

        return

    if intent == "publish":
        await _handle_publish(
            text=text,
            channel_id=channel_id,
            message_ts=message_ts,
            thread_ts=thread_ts,
            say=say,
        )

        return

    say(
        text=(
            "요청 유형을 확인하지 못했습니다. "
            "초안 작성, 수정/승인 또는 게시 요청으로 "
            "말씀해 주세요."
        ),
        thread_ts=_get_reply_thread_ts(
            event
        ),
    )


def _detect_intent(
    text: str,
    thread_ts: str | None,
) -> str:
    normalized = text.lower()

    publish_keywords = [
        "게시",
        "업로드",
        "올려줘",
        "발행",
    ]

    if any(
        keyword in normalized
        for keyword in publish_keywords
    ):
        return "publish"

    review_keywords = [
        "수정",
        "바꿔",
        "줄여",
        "늘려",
        "승인",
        "이대로 좋아",
    ]

    if thread_ts and any(
        keyword in normalized
        for keyword in review_keywords
    ):
        return "review"

    generate_keywords = [
        "초안",
        "작성",
        "콘텐츠",
        "게시글",
    ]

    if any(
        keyword in normalized
        for keyword in generate_keywords
    ):
        return "generate"

    if thread_ts:
        return "review"

    return "generate"


async def _handle_generate(
    text: str,
    channel_id: str,
    message_ts: str,
    slack_file_ids: list[str],
    say,
) -> None:
    result = await generate_learning_content(
        source_text=text,
        slack_channel_id=channel_id,
        slack_message_ts=message_ts,
        slack_file_ids=slack_file_ids,
    )

    request_id = result[
        "request_id"
    ]

    drafts = result.get(
        "drafts",
        [],
    )

    message = _format_drafts(
        request_id=request_id,
        drafts=drafts,
    )

    say(
        text=message,
        thread_ts=message_ts,
    )


async def _handle_review(
    text: str,
    channel_id: str,
    message_ts: str,
    thread_ts: str | None,
    say,
) -> None:
    if not thread_ts:
        raise RuntimeError(
            "Review request must be sent "
            "inside an existing thread."
        )

    request_id = _resolve_request_id(
        channel_id=channel_id,
        root_message_ts=thread_ts,
    )

    result = await review_learning_content(
        instruction=text,
        request_id=request_id,
        slack_channel_id=channel_id,
        slack_message_ts=message_ts,
    )

    message = _format_review_result(
        result
    )

    say(
        text=message,
        thread_ts=thread_ts,
    )


async def _handle_publish(
    text: str,
    channel_id: str,
    message_ts: str,
    thread_ts: str | None,
    say,
) -> None:
    if not thread_ts:
        raise RuntimeError(
            "Publish request must be sent "
            "inside an existing thread."
        )

    request_id = _resolve_request_id(
        channel_id=channel_id,
        root_message_ts=thread_ts,
    )

    result = await publish_learning_content(
        instruction=text,
        request_id=request_id,
        slack_channel_id=channel_id,
        slack_message_ts=message_ts,
    )

    message = _format_publish_result(
        result
    )

    say(
        text=message,
        thread_ts=thread_ts,
    )


def _resolve_request_id(
    channel_id: str,
    root_message_ts: str,
) -> str:
    from marketing_agent.services.content_request_service import (
        ContentRequestService,
    )

    service = ContentRequestService()

    return service.resolve_request_id(
        slack_channel_id=channel_id,
        slack_message_ts=root_message_ts,
    )


def _clean_message_text(
    text: str,
) -> str:
    parts = text.split(
        ">",
        maxsplit=1,
    )

    if len(parts) == 2:
        return parts[1].strip()

    return text.strip()


def _get_reply_thread_ts(
    event: dict,
) -> str:
    return event.get(
        "thread_ts"
    ) or event[
        "ts"
    ]


def _format_drafts(
    request_id: str,
    drafts: list[dict],
) -> str:
    draft_map = {
        draft["platform"]: draft
        for draft in drafts
    }

    naver = draft_map[
        "naver_blog"
    ]

    instagram = draft_map[
        "instagram"
    ]

    threads = draft_map[
        "threads"
    ]

    return (
        f"요청 ID: `{request_id}`\n\n"
        "[네이버 블로그 초안]\n"
        f"제목: {naver.get('title', '')}\n\n"
        f"{naver.get('body', '')}\n\n"
        f"{' '.join(naver.get('hashtags', []))}\n\n"
        "[Instagram 초안]\n"
        f"{instagram.get('body', '')}\n\n"
        f"{' '.join(instagram.get('hashtags', []))}\n\n"
        "[Threads 초안]\n"
        f"{threads.get('body', '')}\n\n"
        f"{' '.join(threads.get('hashtags', []))}"
    )


def _format_review_result(
    result: dict,
) -> str:
    drafts = result.get(
        "updated_drafts",
        [],
    )

    return _format_drafts(
        request_id=result[
            "request_id"
        ],
        drafts=drafts,
    )


def _format_publish_result(
    result: dict,
) -> str:
    lines = []

    for item in result.get(
        "publish_results",
        [],
    ):
        platform = item[
            "platform"
        ]

        status = item[
            "status"
        ]

        if status in {
            "published",
            "already_published",
        }:
            lines.append(
                f"- {platform}: 게시 완료"
            )

        else:
            error = item.get(
                "error",
                "알 수 없는 오류",
            )

            lines.append(
                f"- {platform}: 게시 실패 ({error})"
            )

    if result.get(
        "publish_completed"
    ):
        lines.append(
            "\n모든 요청된 게시 작업이 완료되었습니다."
        )

    return "\n".join(
        lines
    )


def main() -> None:
    logger.info(
        "Starting Slack Bolt app."
    )

    handler = SocketModeHandler(
        app,
        settings.slack_app_token,
    )

    handler.start()


if __name__ == "__main__":
    main()