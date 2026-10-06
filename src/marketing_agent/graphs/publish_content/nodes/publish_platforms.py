from marketing_agent.graphs.publish_content.state import (
    PublishContentState,
)
from marketing_agent.services.content_request_service import (
    ContentRequestService,
)
from marketing_agent.tools.publish_instagram_draft import (
    publish as publish_instagram,
)
from marketing_agent.tools.publish_naver_draft import (
    publish as publish_naver,
)
from marketing_agent.tools.publish_threads_draft import (
    publish as publish_threads,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


async def publish_platforms_node(
    state: PublishContentState,
) -> dict:
    request_id = state[
        "request_id"
    ]

    slack_channel_id = state[
        "slack_channel_id"
    ]

    publish_platforms = state.get(
        "publish_platforms",
        [],
    )

    if not publish_platforms:
        logger.info(
            "No platforms requested for publish: "
            "request_id=%s",
            request_id,
        )

        return {
            "publish_results": [],
            "publish_completed": False,
        }

    logger.info(
        "Publishing platforms: "
        "request_id=%s platforms=%s",
        request_id,
        publish_platforms,
    )

    service = ContentRequestService()

    results: list[dict] = []

    for platform in publish_platforms:
        try:
            request, draft = (
                service.get_draft(
                    request_id=request_id,
                    platform=platform,
                )
            )

            if draft.status == "published":
                logger.info(
                    "Draft already published: "
                    "request_id=%s platform=%s",
                    request_id,
                    platform,
                )

                results.append(
                    {
                        "platform": platform,
                        "status": "already_published",
                        "error": None,
                    }
                )

                continue

            if draft.status != "approved":
                results.append(
                    {
                        "platform": platform,
                        "status": "skipped",
                        "error": (
                            "Draft is not approved."
                        ),
                    }
                )

                logger.warning(
                    "Publish skipped because "
                    "draft is not approved: "
                    "request_id=%s "
                    "platform=%s "
                    "status=%s",
                    request_id,
                    platform,
                    draft.status,
                )

                continue

            result = await _publish_platform(
                platform=platform,
                request_id=request_id,
                slack_channel_id=slack_channel_id,
            )

            results.append(
                {
                    "platform": platform,
                    "status": "published",
                    "error": None,
                    "result": result,
                }
            )

            logger.info(
                "Platform publish succeeded: "
                "request_id=%s platform=%s",
                request_id,
                platform,
            )

        except Exception as error:
            logger.exception(
                "Platform publish failed: "
                "request_id=%s platform=%s",
                request_id,
                platform,
            )

            results.append(
                {
                    "platform": platform,
                    "status": "failed",
                    "error": str(error),
                }
            )

    publish_completed = all(
        result["status"]
        in {
            "published",
            "already_published",
        }
        for result in results
    )

    logger.info(
        "Platform publishing finished: "
        "request_id=%s completed=%s "
        "results=%s",
        request_id,
        publish_completed,
        [
            (
                result["platform"],
                result["status"],
            )
            for result in results
        ],
    )

    return {
        "publish_results": results,
        "publish_completed": publish_completed,
    }


async def _publish_platform(
    platform: str,
    request_id: str,
    slack_channel_id: str,
) -> dict:
    if platform == "naver_blog":
        return await publish_naver(
            request_id=request_id,
            slack_channel_id=slack_channel_id,
            cleanup=False,
        )

    if platform == "instagram":
        return await publish_instagram(
            request_id=request_id,
            slack_channel_id=slack_channel_id,
            cleanup=False,
        )

    if platform == "threads":
        return await publish_threads(
            request_id=request_id,
            slack_channel_id=slack_channel_id,
            cleanup=False,
        )

    raise ValueError(
        f"Unsupported publish platform: {platform}"
    )