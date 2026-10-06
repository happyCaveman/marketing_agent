import json

from marketing_agent.graphs.learning_content.nodes.classify_content_type import (
    classify_content_type,
)
from marketing_agent.graphs.review_content.state import (
    ReviewContentState,
)
from marketing_agent.services.content_request_service import (
    ContentRequestService,
)
from marketing_agent.services.llm_service import (
    LLMService,
)
from marketing_agent.services.prompt_service import (
    PromptService,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


def apply_revisions_node(
    state: ReviewContentState,
) -> dict:
    revision_actions = state.get(
        "revision_actions",
        [],
    )

    if not revision_actions:
        logger.info(
            "No draft revisions requested."
        )

        return {
            "updated_drafts": state[
                "content_request"
            ].get(
                "drafts",
                [],
            )
        }

    request_id = state[
        "request_id"
    ]

    content_request = state[
        "content_request"
    ]

    source_text = content_request.get(
        "source_text",
        "",
    )

    content_service = (
        ContentRequestService()
    )

    prompt_service = PromptService()

    current_request = content_service.get_request(request_id=request_id)
    content_type = current_request.content_type
    if content_type is None:
        content_type = classify_content_type(current_request.source_text)
        current_request.content_type = content_type
        content_service.storage.save_request(current_request)

    prompt_config = (
        prompt_service.load_prompts(
            team="learning",
            prompt_names=["common", content_type],
        )
    )

    llm_service = LLMService()

    logger.info(
        "Applying draft revisions: "
        "request_id=%s actions=%s",
        request_id,
        len(revision_actions),
    )

    for action in revision_actions:
        platform = action[
            "platform"
        ]

        fields = action[
            "fields"
        ]

        instruction = action[
            "instruction"
        ]

        current_draft = next(
            (
                draft
                for draft
                in current_request.drafts
                if draft.platform
                == platform
            ),
            None,
        )

        if current_draft is None:
            raise RuntimeError(
                "Draft not found for revision: "
                f"platform={platform}"
            )

        prompt = _build_revision_prompt(
            source_text=source_text,
            prompt_config=prompt_config,
            current_draft=(
                current_draft.model_dump(
                    mode="json"
                )
            ),
            platform=platform,
            fields=fields,
            instruction=instruction,
        )

        response_text = (
            llm_service.generate_text(
                prompt=prompt
            )
        )

        revision = (
            _parse_revision_result(
                response_text=response_text,
                allowed_fields=fields,
            )
        )

        update_kwargs = {}

        if "title" in fields:
            update_kwargs["title"] = (
                revision.get(
                    "title"
                )
            )

        if "body" in fields:
            update_kwargs["body"] = (
                revision.get(
                    "body"
                )
            )

        if "hashtags" in fields:
            update_kwargs["hashtags"] = (
                revision.get(
                    "hashtags"
                )
            )

        current_request = (
            content_service.update_draft(
                request_id=request_id,
                platform=platform,
                **update_kwargs,
            )
        )

        logger.info(
            "Draft revision applied: "
            "request_id=%s "
            "platform=%s "
            "fields=%s",
            request_id,
            platform,
            fields,
        )

    saved_request = (
        content_service.get_request(
            request_id=request_id
        )
    )

    logger.info(
        "All requested revisions saved: "
        "request_id=%s",
        request_id,
    )

    request_data = (
        saved_request.model_dump(
            mode="json"
        )
    )

    return {
        "content_request": request_data,
        "updated_drafts": (
            request_data[
                "drafts"
            ]
        ),
    }


def _build_revision_prompt(
    source_text: str,
    prompt_config: dict,
    current_draft: dict,
    platform: str,
    fields: list[str],
    instruction: str,
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

    current_draft_json = (
        json.dumps(
            current_draft,
            ensure_ascii=False,
            indent=2,
        )
    )

    fields_json = (
        json.dumps(
            fields,
            ensure_ascii=False,
        )
    )

    return f"""
당신은 기존 마케팅 콘텐츠의 특정 필드만 수정하는 편집기입니다.

새로운 콘텐츠를 처음부터 다시 작성하지 마세요.

사용자가 요청한 필드만 수정하고
요청하지 않은 필드는 변경하지 마세요.


[원본 사용자 정보]

{source_text}


[Google Sheet 역할]

{role}


[Google Sheet 문체]

{tone}


[Google Sheet 작성 규칙]

{rules}


[플랫폼]

{platform}


[현재 Draft]

{current_draft_json}


[수정할 필드]

{fields_json}


[사용자 수정 요청]

{instruction}


[중요 규칙]

1. 수정할 필드에 명시된 필드만 반환하세요.

2. 사용자가 요청하지 않은 필드는
새로 작성하거나 반환하지 마세요.

3. 기존 Draft와 원본 사용자 정보에 없는
새로운 사실을 추가하지 마세요.

4. Google Sheet의 작성 규칙을 유지하세요.

5. 사용자가 기존 내용을 줄이라고 요청하면
새로운 내용을 추가하지 말고
기존 내용을 중심으로 축약하세요.

6. 해시태그를 줄이라고 요청하면
기존 해시태그 중 적절한 항목을 제거하세요.
새로운 해시태그를 임의로 추가하지 마세요.

7. 반드시 JSON만 반환하세요.


예를 들어 body만 수정하는 경우:

{{
  "body": "수정된 본문"
}}


hashtags만 수정하는 경우:

{{
  "hashtags": [
    "#태그1",
    "#태그2"
  ]
}}


title과 body를 수정하는 경우:

{{
  "title": "수정된 제목",
  "body": "수정된 본문"
}}
""".strip()


def _parse_revision_result(
    response_text: str,
    allowed_fields: list[str],
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
            "Failed to parse revision "
            "response as JSON: %s",
            response_text,
        )

        raise RuntimeError(
            "Revision model returned "
            "invalid JSON."
        ) from error

    if not isinstance(
        data,
        dict,
    ):
        raise RuntimeError(
            "Revision response must "
            "be a JSON object."
        )

    unexpected_fields = (
        set(data.keys())
        - set(allowed_fields)
    )

    if unexpected_fields:
        raise RuntimeError(
            "Revision response contains "
            "unexpected fields: "
            f"{unexpected_fields}"
        )

    for field in allowed_fields:
        if field not in data:
            raise RuntimeError(
                "Revision response missing "
                f"requested field: {field}"
            )

    if "title" in data:
        if not isinstance(
            data["title"],
            str,
        ):
            raise RuntimeError(
                "Revised title must "
                "be a string."
            )

    if "body" in data:
        if not isinstance(
            data["body"],
            str,
        ):
            raise RuntimeError(
                "Revised body must "
                "be a string."
            )

    if "hashtags" in data:
        if not isinstance(
            data["hashtags"],
            list,
        ):
            raise RuntimeError(
                "Revised hashtags must "
                "be a list."
            )

        if not all(
            isinstance(tag, str)
            for tag in data[
                "hashtags"
            ]
        ):
            raise RuntimeError(
                "Every hashtag must "
                "be a string."
            )

    return data
