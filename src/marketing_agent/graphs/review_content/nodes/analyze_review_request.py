import json

from marketing_agent.graphs.review_content.state import (
    ReviewContentState,
)
from marketing_agent.services.llm_service import (
    LLMService,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


def analyze_review_request_node(
    state: ReviewContentState,
) -> dict:
    logger.info(
        "Analyzing review request."
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
        "Review request analyzed: "
        "revisions=%s approvals=%s",
        len(result["revisions"]),
        result["approvals"],
    )

    return {
        "revision_actions": (
            result["revisions"]
        ),
        "approval_platforms": (
            result["approvals"]
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
당신은 사용자의 콘텐츠 검토 요청을
구조화된 작업 목록으로 변환하는 분석기입니다.

실제 Draft를 수정하지 마세요.
승인 상태도 변경하지 마세요.

사용자가 요청한 작업이 무엇인지 분석해서
JSON으로만 반환하세요.


[현재 저장된 Draft]
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

[수정 가능한 필드]

title
body
hashtags


[분석 규칙]

1. 사용자가 명시적으로 수정 요청한 플랫폼만
revisions에 포함하세요.

2. 수정 요청하지 않은 플랫폼은
revisions에 넣지 마세요.

3. 사용자가 승인 의사를 표현한 플랫폼만
approvals에 포함하세요.

4. "모두 승인", "넷 다 승인" 등은
naver_blog, instagram, threads, facebook 모두를 의미합니다.

5. 승인 요청과 수정 요청은 동시에 존재할 수 있습니다.

6. "네이버 길이 줄여줘"처럼 필드가 명확하지 않지만
본문 길이를 의미하는 요청은 body로 판단할 수 있습니다.

7. "인스타 해시태그 2개 줄여줘"는
hashtags 필드 수정입니다.

8. 사용자의 요청을 확대 해석하지 마세요.

9. 게시 요청은 이 단계에서 처리하지 않습니다.

10. 반드시 JSON만 반환하세요.


반환 형식:

{{
  "revisions": [
    {{
      "platform": "naver_blog",
      "fields": [
        "body"
      ],
      "instruction": "본문 길이를 현재의 약 절반으로 줄인다."
    }}
  ],
  "approvals": [
    "threads"
  ]
}}

수정 요청이 없다면:

{{
  "revisions": [],
  "approvals": [
    "threads"
  ]
}}

승인 요청이 없다면:

{{
  "revisions": [
    {{
      "platform": "instagram",
      "fields": [
        "hashtags"
      ],
      "instruction": "현재 해시태그 수에서 2개 줄인다."
    }}
  ],
  "approvals": []
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
        logger.error(
            "Failed to parse review analysis "
            "response as JSON: %s",
            response_text,
        )

        raise RuntimeError(
            "Review analyzer returned invalid JSON."
        ) from error

    revisions = data.get(
        "revisions"
    )

    approvals = data.get(
        "approvals"
    )

    if not isinstance(
        revisions,
        list,
    ):
        raise RuntimeError(
            "Review analysis response "
            "must contain list 'revisions'."
        )

    if not isinstance(
        approvals,
        list,
    ):
        raise RuntimeError(
            "Review analysis response "
            "must contain list 'approvals'."
        )

    allowed_platforms = {
        "naver_blog",
        "instagram",
        "threads",
        "facebook"
    }

    allowed_fields = {
        "title",
        "body",
        "hashtags",
    }

    for revision in revisions:
        if not isinstance(
            revision,
            dict,
        ):
            raise RuntimeError(
                "Each revision must be an object."
            )

        platform = revision.get(
            "platform"
        )

        fields = revision.get(
            "fields"
        )

        instruction = revision.get(
            "instruction"
        )

        if platform not in allowed_platforms:
            raise RuntimeError(
                "Invalid revision platform: "
                f"{platform}"
            )

        if not isinstance(
            fields,
            list,
        ):
            raise RuntimeError(
                "Revision fields must be a list."
            )

        if not fields:
            raise RuntimeError(
                "Revision fields cannot be empty."
            )

        if any(
            field not in allowed_fields
            for field in fields
        ):
            raise RuntimeError(
                "Invalid revision field."
            )

        if (
            not isinstance(
                instruction,
                str,
            )
            or not instruction.strip()
        ):
            raise RuntimeError(
                "Revision instruction is required."
            )

    for platform in approvals:
        if platform not in allowed_platforms:
            raise RuntimeError(
                "Invalid approval platform: "
                f"{platform}"
            )

    return {
        "revisions": revisions,
        "approvals": approvals,
    }