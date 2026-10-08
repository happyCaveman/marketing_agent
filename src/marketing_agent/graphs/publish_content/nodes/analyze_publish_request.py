import json

from marketing_agent.graphs.publish_content.state import (
    PublishContentState,
)
from marketing_agent.services.llm_service import (
    LLMService,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


def analyze_publish_request_node(
    state: PublishContentState,
) -> dict:
    logger.info(
        "Analyzing publish request."
    )

    instruction = state[
        "instruction"
    ]

    content_request = state[
        "content_request"
    ]

    prompt = _build_analysis_prompt(
        instruction=instruction,
        content_request=content_request,
    )

    llm_service = LLMService()

    response_text = (
        llm_service.generate_text(
            prompt=prompt
        )
    )

    result = _parse_analysis_result(
        response_text=response_text
    )

    logger.info(
        "Publish request analyzed: "
        "approvals=%s publish=%s",
        result["approvals"],
        result["publish"],
    )

    return {
        "approval_platforms": (
            result["approvals"]
        ),
        "publish_platforms": (
            result["publish"]
        ),
    }


def _build_analysis_prompt(
    instruction: str,
    content_request: dict,
) -> str:
    drafts_json = json.dumps(
        content_request.get(
            "drafts",
            [],
        ),
        ensure_ascii=False,
        indent=2,
    )

    return f"""
당신은 사용자의 콘텐츠 승인 및 게시 요청을
구조화된 작업 목록으로 변환하는 분석기입니다.

실제 승인이나 게시 작업을 수행하지 마세요.
사용자의 요청만 분석하세요.


[현재 Draft 상태]

{drafts_json}


[사용자 요청]

{instruction}


[플랫폼 이름]

Naver Blog:
naver_blog

Instagram:
instagram

Threads:
threads

Facebook:
facebook


[분석 규칙]

1. 사용자가 이번 메시지에서 명시적으로 승인한 플랫폼만
approvals에 포함하세요.

2. 사용자가 게시를 요청한 플랫폼만
publish에 포함하세요.

3. "모두 승인", "셋 다 승인"은
naver_blog, instagram, threads 모두를 의미합니다.

4. "다 게시해줘", "전부 올려줘",
"모두 게시해줘"는
naver_blog, instagram, threads, facebook 모두를 의미합니다.

5. "승인할게. 게시해줘."처럼
승인과 게시를 함께 요청할 수 있습니다.

6. 특정 플랫폼만 언급하면
그 플랫폼만 포함하세요.

7. 사용자가 요청하지 않은 플랫폼을
임의로 포함하지 마세요.

8. 기존 Draft의 status는
현재 상태를 이해하는 참고 정보일 뿐입니다.

9. 반드시 JSON만 반환하세요.


예시:

사용자:
"다 승인할게. 게시해줘."

반환:

{{
  "approvals": [
    "naver_blog",
    "instagram",
    "threads",
    "facebook"
  ],
  "publish": [
    "naver_blog",
    "instagram",
    "threads",
    "facebook"
  ]
}}


사용자:
"인스타만 게시해줘."

반환:

{{
  "approvals": [],
  "publish": [
    "instagram"
  ]
}}


사용자:
"네이버랑 Threads 승인하고 둘 다 게시해줘."

반환:

{{
  "approvals": [
    "naver_blog",
    "threads"
  ],
  "publish": [
    "naver_blog",
    "threads"
  ]
}}
""".strip()


def _parse_analysis_result(
    response_text: str,
) -> dict:
    cleaned_text = (
        response_text
        .strip()
    )

    if cleaned_text.startswith(
        "```json"
    ):
        cleaned_text = (
            cleaned_text
            .removeprefix("```json")
            .removesuffix("```")
            .strip()
        )

    elif cleaned_text.startswith(
        "```"
    ):
        cleaned_text = (
            cleaned_text
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )

    try:
        data = json.loads(
            cleaned_text
        )

    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Publish analyzer returned invalid JSON."
        ) from error

    approvals = data.get(
        "approvals"
    )

    publish = data.get(
        "publish"
    )

    if not isinstance(
        approvals,
        list,
    ):
        raise RuntimeError(
            "Publish analysis response "
            "must contain list 'approvals'."
        )

    if not isinstance(
        publish,
        list,
    ):
        raise RuntimeError(
            "Publish analysis response "
            "must contain list 'publish'."
        )

    allowed_platforms = {
        "naver_blog",
        "instagram",
        "threads",
        "facebook"
    }

    for platform in approvals:
        if platform not in allowed_platforms:
            raise RuntimeError(
                "Invalid approval platform: "
                f"{platform}"
            )

    for platform in publish:
        if platform not in allowed_platforms:
            raise RuntimeError(
                "Invalid publish platform: "
                f"{platform}"
            )

    return {
        "approvals": approvals,
        "publish": publish,
    }