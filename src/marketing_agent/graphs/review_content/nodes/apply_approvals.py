from marketing_agent.graphs.review_content.state import (
    ReviewContentState,
)
from marketing_agent.services.content_request_service import (
    ContentRequestService,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


def apply_approvals_node(
    state: ReviewContentState,
) -> dict:
    approval_platforms = state.get(
        "approval_platforms",
        [],
    )

    request_id = state[
        "request_id"
    ]

    service = ContentRequestService()

    if not approval_platforms:
        logger.info(
            "No draft approvals requested: "
            "request_id=%s",
            request_id,
        )

        request = service.get_request(
            request_id=request_id
        )

        request_data = request.model_dump(
            mode="json"
        )

        return {
            "content_request": request_data,
            "updated_drafts": request_data[
                "drafts"
            ],
        }

    logger.info(
        "Applying draft approvals: "
        "request_id=%s platforms=%s",
        request_id,
        approval_platforms,
    )

    for platform in approval_platforms:
        service.approve_draft(
            request_id=request_id,
            platform=platform,
        )

        logger.info(
            "Draft approval applied: "
            "request_id=%s platform=%s",
            request_id,
            platform,
        )

    saved_request = service.get_request(
        request_id=request_id
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