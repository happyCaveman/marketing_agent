from marketing_agent.graphs.learning_content.state import (
    LearningContentState,
)
from marketing_agent.tools.search_learning_knowledge import (
    search_learning_knowledge,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


def search_knowledge_node(
    state: LearningContentState,
) -> dict:
    source_text = state["source_text"]

    logger.info(
        "Searching Learning knowledge: query=%s",
        source_text,
    )

    results = search_learning_knowledge(
        query=source_text,
        limit=5,
        score_threshold=0.65,
    )

    if not results:
        logger.info(
            "No Learning knowledge found."
        )

        return {
            "knowledge": [],
        }

    logger.info(
        "Learning knowledge search completed: "
        "results=%s",
        len(results),
    )

    return {
        "knowledge": results,
    }