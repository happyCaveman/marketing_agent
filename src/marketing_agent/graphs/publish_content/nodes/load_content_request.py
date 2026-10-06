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


def load_content_request_node(
    state: PublishContentState,
) -> dict:
    request_id = state[
        "request_id"
    ]

    logger.info(
        "Loading ContentRequest for publish: "
        "request_id=%s",
        request_id,
    )

    service = ContentRequestService()

    request = service.get_request(
        request_id=request_id
    )

    request_data = request.model_dump(
        mode="json"
    )

    logger.info(
        "ContentRequest loaded for publish: "
        "request_id=%s drafts=%s",
        request.request_id,
        len(request.drafts),
    )

    return {
        "content_request": request_data,
    }