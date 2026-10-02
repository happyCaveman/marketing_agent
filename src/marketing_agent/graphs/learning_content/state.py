from typing import (
    Any,
    NotRequired,
    TypedDict,
)


class LearningContentState(TypedDict):
    # 사용자 입력
    source_text: str

    # Slack 정보
    slack_channel_id: str
    slack_message_ts: str
    slack_file_ids: list[str]

    # Workflow 진행 중 채워지는 값
    prompt_config: NotRequired[
        dict[str, Any]
    ]

    knowledge: NotRequired[
        list[dict[str, Any]]
    ]

    drafts: NotRequired[
        list[dict[str, Any]]
    ]

    validation_errors: NotRequired[
        list[str]
    ]

    retry_count: NotRequired[
        int
    ]

    # 최종 저장 후 생성
    request_id: NotRequired[
        str | None
    ]