from marketing_agent.graphs.learning_content.state import (
    LearningContentState,
)
from marketing_agent.models.platform_draft import (
    PlatformDraft,
)
from marketing_agent.services.content_request_service import (
    ContentRequestService,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


def save_content_request_node(
    state: LearningContentState,
) -> dict:
    logger.info(
        "Saving validated drafts as ContentRequest."
    )

    existing_request_id = state.get(
        "request_id"
    )

    if existing_request_id:
        logger.info(
            "ContentRequest already exists: "
            "request_id=%s",
            existing_request_id,
        )

        return {
            "request_id": existing_request_id,
        }

    validation_errors = state.get(
        "validation_errors",
        [],
    )

    if validation_errors:
        raise RuntimeError(
            "Cannot save ContentRequest because "
            "draft validation errors remain."
        )

    raw_drafts = state.get(
        "drafts",
        [],
    )

    if not raw_drafts:
        raise RuntimeError(
            "Cannot save ContentRequest because "
            "no drafts were generated."
        )

    drafts = [
        PlatformDraft.model_validate(
            draft
        )
        for draft in raw_drafts
    ]

    source_text = state[
        "source_text"
    ]

    slack_file_ids = state.get(
        "slack_file_ids",
        [],
    )

    service = ContentRequestService()

    request = (
        service.create_request_from_slack(
            source_text=source_text,
            drafts=drafts,
            slack_file_ids=slack_file_ids,
        )
    )

    logger.info(
        "ContentRequest saved: "
        "request_id=%s drafts=%s images=%s",
        request.request_id,
        len(request.drafts),
        len(request.images),
    )

    return {
        "request_id": request.request_id,
    }