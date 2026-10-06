from marketing_agent.graphs.publish_content.state import (
    PublishContentState,
)
from marketing_agent.services.content_request_service import (
    ContentRequestService,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


def apply_publish_approvals_node(
    state: PublishContentState,
) -> dict:
    request_id = state[
        "request_id"
    ]

    approval_platforms = state.get(
        "approval_platforms",
        [],
    )

    service = ContentRequestService()

    if not approval_platforms:
        logger.info(
            "No publish approvals requested: "
            "request_id=%s",
            request_id,
        )

        request = service.get_request(
            request_id=request_id
        )

        return {
            "content_request": (
                request.model_dump(
                    mode="json"
                )
            )
        }

    logger.info(
        "Applying publish approvals: "
        "request_id=%s platforms=%s",
        request_id,
        approval_platforms,
    )

    for platform in approval_platforms:
        request, draft = (
            service.get_draft(
                request_id=request_id,
                platform=platform,
            )
        )

        if draft.status == "published":
            raise RuntimeError(
                "Cannot approve an already "
                "published draft: "
                f"platform={platform}"
            )

        if draft.status == "approved":
            logger.info(
                "Draft already approved: "
                "request_id=%s platform=%s",
                request_id,
                platform,
            )

            continue

        service.approve_draft(
            request_id=request_id,
            platform=platform,
        )

        logger.info(
            "Draft approved for publishing: "
            "request_id=%s platform=%s",
            request_id,
            platform,
        )

    saved_request = service.get_request(
        request_id=request_id
    )

    return {
        "content_request": (
            saved_request.model_dump(
                mode="json"
            )
        )
    }