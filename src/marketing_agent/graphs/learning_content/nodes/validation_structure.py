from marketing_agent.graphs.learning_content.state import (
    LearningContentState,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


MAX_RETRIES = 2


def validate_structure_node(
    state: LearningContentState,
) -> dict:
    logger.info(
        "Validating generated platform drafts."
    )

    drafts = state.get(
        "drafts",
        [],
    )

    errors: list[str] = []

    _validate_structure(
        drafts=drafts,
        errors=errors,
    )

    retry_count = state.get(
        "retry_count",
        0,
    )

    if errors:
        retry_count += 1

        logger.warning(
            "Draft validation failed: "
            "retry=%s errors=%s",
            retry_count,
            errors,
        )

    else:
        logger.info(
            "Draft validation succeeded."
        )

    return {
        "validation_errors": errors,
        "retry_count": retry_count,
    }


def _validate_structure(
    drafts: list[dict],
    errors: list[str],
) -> None:
    if not drafts:
        errors.append(
            "No drafts were generated."
        )
        return

    draft_map = {
        draft.get("platform"): draft
        for draft in drafts
    }

    required_platforms = {
        "naver_blog",
        "instagram",
        "threads",
    }

    actual_platforms = set(
        draft_map.keys()
    )

    if actual_platforms != required_platforms:
        errors.append(
            "Drafts must contain exactly "
            "naver_blog, instagram, threads."
        )

    for platform in required_platforms:
        draft = draft_map.get(
            platform
        )

        if draft is None:
            continue

        body = (
            draft.get("body")
            or ""
        ).strip()

        if not body:
            errors.append(
                f"{platform} body is empty."
            )

        hashtags = draft.get(
            "hashtags"
        )

        if not isinstance(
            hashtags,
            list,
        ):
            errors.append(
                f"{platform} hashtags must be a list."
            )

    naver = draft_map.get(
        "naver_blog"
    )

    if naver is not None:
        title = (
            naver.get("title")
            or ""
        ).strip()

        if not title:
            errors.append(
                "Naver Blog requires a title."
            )


def route_after_structure_validation(
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