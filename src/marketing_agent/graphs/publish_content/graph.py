from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from marketing_agent.graphs.publish_content.nodes.analyze_publish_request import (
    analyze_publish_request_node,
)
from marketing_agent.graphs.publish_content.nodes.load_content_request import (
    load_content_request_node,
)

from marketing_agent.graphs.publish_content.nodes.apply_publish_approvals import (
    apply_publish_approvals_node
)

from marketing_agent.graphs.publish_content.nodes.publish_platforms import (
    publish_platforms_node
)

from marketing_agent.graphs.publish_content.nodes.finalize_publish import (
    finalize_publish_node
)

from marketing_agent.graphs.publish_content.state import (
    PublishContentState,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


def initialize_publish(
    state: PublishContentState,
) -> dict:
    logger.info(
        "Publish content graph started: "
        "request_id=%s",
        state["request_id"],
    )

    return {
        "content_request": {},
        "approval_platforms": [],
        "publish_platforms": [],
        "publish_results": [],
        "publish_completed": False,
        "cleanup_completed": False,
    }


def build_publish_content_graph():
    builder = StateGraph(
        PublishContentState
    )

    # node 등록 ---------------------------------------------

    builder.add_node(
        "initialize_publish",
        initialize_publish,
    )

    builder.add_node(
        "load_content_request",
        load_content_request_node,
    )

    builder.add_node(
        "analyze_publish_request",
        analyze_publish_request_node,
    )
    
    builder.add_node(
        "apply_publish_approvals",
        apply_publish_approvals_node
    )

    builder.add_node(
        "publish_platforms",
        publish_platforms_node,
    )
    
    builder.add_node(
        "finalize_publish",
        finalize_publish_node,
    )
    
    # edge 등록 ---------------------------------------------

    builder.add_edge(
        START,
        "initialize_publish",
    )

    builder.add_edge(
        "initialize_publish",
        "load_content_request",
    )

    builder.add_edge(
        "load_content_request",
        "analyze_publish_request",
    )

    builder.add_edge(
        "analyze_publish_request",
        "apply_publish_approvals",
    )

    builder.add_edge(
        "apply_publish_approvals",
        "publish_platforms",
    )
    
    builder.add_edge(
        "publish_platforms",
        "finalize_publish",
    )
    
    builder.add_edge(
        "finalize_publish",
        END
    )
    
    return builder.compile()


publish_content_graph = (
    build_publish_content_graph()
)