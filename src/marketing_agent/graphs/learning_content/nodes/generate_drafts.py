import json

from marketing_agent.graphs.learning_content.state import (
    LearningContentState,
)
from marketing_agent.models.platform_draft import (
    PlatformDraft,
)
from marketing_agent.services.llm_service import (
    LLMService,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


def generate_drafts_node(
    state: LearningContentState,
) -> dict:
    logger.info(
        "Generating platform drafts."
    )

    source_text = state["source_text"]
    prompt_config = state["prompt_config"]

    knowledge = state.get(
        "knowledge",
        [],
    )

    validation_errors = state.get(
        "validation_errors",
        [],
    )

    prompt = _build_generation_prompt(
        source_text=source_text,
        prompt_config=prompt_config,
        knowledge=knowledge,
        validation_errors=validation_errors,
    )

    llm_service = LLMService()

    response_text = (
        llm_service.generate_text(
            prompt=prompt
        )
    )

    drafts = _parse_drafts(
        response_text=response_text
    )

    logger.info(
        "Platform drafts generated: "
        "platforms=%s",
        [
            draft.platform
            for draft in drafts
        ],
    )

    return {
        "drafts": [
            draft.model_dump()
            for draft in drafts
        ]
    }


def _build_generation_prompt(
    source_text: str,
    prompt_config: dict,
    knowledge: list[dict],
    validation_errors: list[str],
) -> str:
    role = "\n".join(
        prompt_config.get(
            "role",
            [],
        )
    )

    tone = "\n".join(
        f"- {item}"
        for item in prompt_config.get(
            "tone",
            [],
        )
    )

    rules = "\n".join(
        f"- {item}"
        for item in prompt_config.get(
            "rule",
            [],
        )
    )

    knowledge_text = _build_knowledge_text(
        knowledge=knowledge
    )

    validation_feedback = (
        "\n".join(
            f"- {error}"
            for error in validation_errors
        )
        if validation_errors
        else "없음"
    )

    return f"""
[역할]
{role}

[작성 방식]
{tone}

[작성 규칙]
{rules}

[사용자 제공 정보]
{source_text}

[Knowledge Base]
{knowledge_text}

[이전 생성 결과의 검증 오류]
{validation_feedback}

이전 생성 결과의 검증 오류가 있다면
해당 오류를 반드시 수정하여 다시 작성하세요.

[작업]
사용자 제공 정보와 Knowledge Base에서 확인된 사실만 사용하여
다음 네개 플랫폼의 마케팅 콘텐츠 초안을 작성하세요.

- Naver Blog
- Instagram
- Threads
- Facebook

사용자가 제공하지 않은 사실을 추측하지 마세요.

반드시 아래 JSON 형식만 반환하세요.
JSON 외의 설명, Markdown 코드블록, 추가 문장은 출력하지 마세요.

{{
  "drafts": [
    {{
      "platform": "naver_blog",
      "title": "네이버 블로그 제목",
      "body": "네이버 블로그 본문",
      "hashtags": [
        "#해시태그1",
        "#해시태그2"
      ]
    }},
    {{
      "platform": "instagram",
      "title": null,
      "body": "Instagram 본문",
      "hashtags": [
        "#해시태그1",
        "#해시태그2"
      ]
    }},
    {{
      "platform": "threads",
      "title": null,
      "body": "Threads 본문",
      "hashtags": [
        "#해시태그1",
        "#해시태그2"
      ]
    }}
    {{
      "platform": "facebook",
      "title": null,
      "body": "Facebook 본문",
      "hashtags": [
        "#해시태그1",
        "#해시태그2"
      ]
    }}
  ]
}}
""".strip()


def _build_knowledge_text(
    knowledge: list[dict],
) -> str:
    if not knowledge:
        return (
            "관련 Knowledge Base 검색 결과가 없습니다. "
            "사용자가 제공한 사실만 사용하세요."
        )

    sections = []

    for index, item in enumerate(
        knowledge,
        start=1,
    ):
        text = item.get(
            "text",
            "",
        )

        source = item.get(
            "source",
            {},
        )

        file_name = source.get(
            "file_name",
            "unknown",
        )

        sections.append(
            (
                f"[{index}] "
                f"source={file_name}\n"
                f"{text}"
            )
        )

    return "\n\n".join(
        sections
    )


def _parse_drafts(
    response_text: str,
) -> list[PlatformDraft]:
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
            "Failed to parse Gemini response "
            "as JSON: %s",
            response_text,
        )

        raise RuntimeError(
            "Gemini returned invalid JSON."
        ) from error

    raw_drafts = data.get(
        "drafts"
    )

    if not isinstance(
        raw_drafts,
        list,
    ):
        raise RuntimeError(
            "Gemini response does not contain "
            "a drafts list."
        )

    drafts = [
        PlatformDraft.model_validate(
            draft
        )
        for draft in raw_drafts
    ]

    expected_platforms = {
        "naver_blog",
        "instagram",
        "threads",
        "facebook",
    }

    actual_platforms = {
        draft.platform
        for draft in drafts
    }

    if (
        actual_platforms
        != expected_platforms
    ):
        raise RuntimeError(
            "Gemini response must contain "
            "exactly three platform drafts."
        )

    return drafts