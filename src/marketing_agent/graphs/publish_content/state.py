from typing import (
    Any,
    NotRequired,
    TypedDict,
)


class PublishContentState(TypedDict):
    # 사용자 게시 요청 원문
    instruction: str

    # 기존 ContentRequest
    request_id: str

    # Slack 정보
    slack_channel_id: str
    slack_message_ts: str

    # 현재 ContentRequest
    content_request: NotRequired[
        dict[str, Any]
    ]

    # 사용자가 이번 요청에서 승인한 플랫폼
    approval_platforms: NotRequired[
        list[str]
    ]

    # 실제 게시 대상
    publish_platforms: NotRequired[
        list[str]
    ]

    # 플랫폼별 게시 결과
    publish_results: NotRequired[
        list[dict[str, Any]]
    ]

    # 전체 게시 성공 여부
    publish_completed: NotRequired[
        bool
    ]

    # cleanup 여부
    cleanup_completed: NotRequired[
        bool
    ]