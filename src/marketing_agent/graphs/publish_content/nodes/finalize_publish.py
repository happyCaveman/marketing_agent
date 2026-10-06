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


def finalize_publish_node(
    state: PublishContentState,
) -> dict:
    request_id = state[
        "request_id"
    ]

    publish_results = state.get(
        "publish_results",
        [],
    )

    service = ContentRequestService()

    logger.info(
        "Finalizing publish workflow: "
        "request_id=%s",
        request_id,
    )

    request = service.get_request(
        request_id=request_id
    )

    draft_statuses = {
        draft.platform: draft.status
        for draft in request.drafts
    }

    all_published = all(
        draft.status == "published"
        for draft in request.drafts
    )

    cleanup_completed = False

    if all_published:
        cleanup_completed = (
            service.cleanup_if_completed(
                request_id=request_id
            )
        )

        logger.info(
            "Publish workflow completed and "
            "request cleaned up: "
            "request_id=%s",
            request_id,
        )

    else:
        logger.info(
            "Publish workflow not fully completed: "
            "request_id=%s statuses=%s",
            request_id,
            draft_statuses,
        )

    return {
        "publish_results": publish_results,
        "publish_completed": all_published,
        "cleanup_completed": (
            cleanup_completed
        ),
    }