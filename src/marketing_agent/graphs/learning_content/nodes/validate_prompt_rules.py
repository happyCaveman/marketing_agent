import json

from marketing_agent.graphs.learning_content.state import (
    LearningContentState,
)
from marketing_agent.services.llm_service import (
    LLMService,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


MAX_RETRIES = 2


def validate_prompt_rules_node(
    state: LearningContentState,
) -> dict:
    logger.info(
        "Validating drafts against prompt rules."
    )

    source_text = state["source_text"]

    prompt_config = state.get(
        "prompt_config",
        {},
    )

    knowledge = state.get(
        "knowledge",
        [],
    )

    drafts = state.get(
        "drafts",
        [],
    )

    prompt = _build_validation_prompt(
        source_text=source_text,
        prompt_config=prompt_config,
        knowledge=knowledge,
        drafts=drafts,
    )

    llm_service = LLMService()

    response_text = (
        llm_service.generate_text(
            prompt=prompt
        )
    )

    validation_result = (
        _parse_validation_result(
            response_text=response_text
        )
    )

    errors = validation_result[
        "errors"
    ]

    retry_count = state.get(
        "retry_count",
        0,
    )

    if errors:
        retry_count += 1

        logger.warning(
            "Prompt rule validation failed: "
            "retry=%s errors=%s",
            retry_count,
            errors,
        )

    else:
        logger.info(
            "Prompt rule validation succeeded."
        )

    return {
        "validation_errors": errors,
        "retry_count": retry_count,
    }


def _build_validation_prompt(
    source_text: str,
    prompt_config: dict,
    knowledge: list[dict],
    drafts: list[dict],
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

    knowledge_text = (
        _build_knowledge_text(
            knowledge=knowledge
        )
    )

    drafts_json = json.dumps(
        drafts,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
당신은 마케팅 콘텐츠의 작성 규칙 준수 여부를 검사하는 검증기입니다.

콘텐츠를 새로 작성하거나 수정하지 마세요.
아래 Google Sheet Prompt를 기준으로
생성된 Draft가 규칙을 준수하는지만 판단하세요.


[Google Sheet - 역할]
{role}


[Google Sheet - 작성 방식]
{tone}


[Google Sheet - 작성 규칙]
{rules}


[사용자가 직접 제공한 사실]
{source_text}


[Knowledge Base에서 확인된 정보]
{knowledge_text}


[검증할 Draft]
{drafts_json}


[검증 원칙]

1. Google Sheet의 role, tone, rule 전체를 검사 기준으로 사용하세요.

2. 사용자가 직접 제공한 사실과
Knowledge Base에서 확인된 사실 외에
새로운 사실이 Draft에 추가되어 있는지 확인하세요.

3. 플랫폼별 길이, 구성, 문체, 해시태그 등은
코드에 정해진 기준이 아니라
오직 위 Google Sheet 규칙을 기준으로 판단하세요.

4. Google Sheet에 명시되지 않은 새로운 규칙을
임의로 만들어 적용하지 마세요.

5. 사소한 표현 차이만으로 실패 처리하지 마세요.
명확하게 규칙을 위반한 경우에만 errors에 추가하세요.

6. 모든 Draft가 규칙을 준수하면
valid는 true이고 errors는 빈 배열이어야 합니다.


반드시 아래 JSON 형식만 반환하세요.

{{
  "valid": true,
  "errors": []
}}

규칙 위반이 있다면:

{{
  "valid": false,
  "errors": [
    "구체적인 위반 내용",
    "구체적인 위반 내용"
  ]
}}

JSON 외의 설명이나 Markdown 코드블록은 출력하지 마세요.
""".strip()


def _build_knowledge_text(
    knowledge: list[dict],
) -> str:
    if not knowledge:
        return (
            "관련 Knowledge Base 검색 결과가 없습니다."
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


def _parse_validation_result(
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
            "Failed to parse prompt validation "
            "response as JSON: %s",
            response_text,
        )

        raise RuntimeError(
            "Prompt validator returned invalid JSON."
        ) from error

    valid = data.get(
        "valid"
    )

    errors = data.get(
        "errors"
    )

    if not isinstance(
        valid,
        bool,
    ):
        raise RuntimeError(
            "Prompt validation response "
            "must contain boolean 'valid'."
        )

    if not isinstance(
        errors,
        list,
    ):
        raise RuntimeError(
            "Prompt validation response "
            "must contain list 'errors'."
        )

    errors = [
        str(error).strip()
        for error in errors
        if str(error).strip()
    ]

    if valid and errors:
        raise RuntimeError(
            "Prompt validation response is "
            "inconsistent: valid=true "
            "but errors are present."
        )

    if not valid and not errors:
        raise RuntimeError(
            "Prompt validation response is "
            "inconsistent: valid=false "
            "but no errors were returned."
        )

    return {
        "valid": valid,
        "errors": errors,
    }


def route_after_prompt_validation(
    state: LearningContentState,
) -> str:
    errors = state.get(
        "validation_errors",
        [],
    )

    retry_count = state.get(
        "retry_count",
        0,
    )

    if not errors:
        return "success"

    if retry_count >= MAX_RETRIES:
        return "failed"

    return "retry"