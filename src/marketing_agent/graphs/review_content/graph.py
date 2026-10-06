from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from marketing_agent.graphs.review_content.nodes.load_content_request import (
    load_content_request_node,
)

from marketing_agent.graphs.review_content.nodes.analyze_review_request import (
    analyze_review_request_node,
)

from marketing_agent.graphs.review_content.nodes.apply_revisions import (
    apply_revisions_node
)

from marketing_agent.graphs.review_content.nodes.apply_approvals import (
    apply_approvals_node
)
from marketing_agent.graphs.review_content.state import (
    ReviewContentState,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


def initialize_review(
    state: ReviewContentState,
) -> dict:
    logger.info(
        "Review content graph started: "
        "request_id=%s",
        state["request_id"],
    )

    return {
        "content_request": {},
        "revision_actions": [],
        "approval_platforms": [],
        "updated_drafts": [],
        "validation_errors": [],
        "retry_count": 0,
    }


def build_review_content_graph():
    builder = StateGraph(
        ReviewContentState
    )

    # node 등록 ---------------------------------------------


    builder.add_node(
        "initialize_review",
        initialize_review,
    )

    builder.add_node(
        "load_content_request",
        load_content_request_node,
    )
    
    builder.add_node(
        "analyze_review_request",
        analyze_review_request_node,
    )
    
    builder.add_node(
        "apply_revisions",
        apply_revisions_node,
    )
    
    builder.add_node(
        "apply_approvals",
        apply_approvals_node,
    )
    
    # edge 등록 ---------------------------------------------


    builder.add_edge(
        START,
        "initialize_review",
    )

    builder.add_edge(
        "initialize_review",
        "load_content_request",
    )

    builder.add_edge(
        "load_content_request",
        "analyze_review_request",
    )
    
    builder.add_edge(
        "analyze_review_request",
        "apply_revisions",
    )
    
    builder.add_edge(
        "apply_revisions",
        "apply_approvals",
    )
    
    builder.add_edge(
        "apply_approvals",
        END,
    )

    return builder.compile()


review_content_graph = (
    build_review_content_graph()
)