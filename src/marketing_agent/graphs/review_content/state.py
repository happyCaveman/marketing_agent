from typing import (
    Any,
    NotRequired,
    TypedDict,
)


class ReviewContentState(TypedDict):
    # 사용자의 수정 / 승인 요청 원문
    instruction: str

    # 기존 ContentRequest
    request_id: str

    # Slack 정보
    slack_channel_id: str
    slack_message_ts: str

    # 기존 ContentRequest 전체
    content_request: NotRequired[
        dict[str, Any]
    ]

    # 추후 LLM이 분석한 작업 목록
    revision_actions: NotRequired[
        list[dict[str, Any]]
    ]

    approval_platforms: NotRequired[
        list[str]
    ]

    # 수정 결과
    updated_drafts: NotRequired[
        list[dict[str, Any]]
    ]

    validation_errors: NotRequired[
        list[str]
    ]

    retry_count: NotRequired[
        int
    ]