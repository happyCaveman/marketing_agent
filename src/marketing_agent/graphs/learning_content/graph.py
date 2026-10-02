from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from marketing_agent.graphs.learning_content.nodes.load_prompt_config import (
    load_prompt_config_node,
)

from marketing_agent.graphs.learning_content.nodes.search_knowledge import (
    search_knowledge_node,
)

from marketing_agent.graphs.learning_content.nodes.generate_drafts import (
    generate_drafts_node,
)

from marketing_agent.graphs.learning_content.nodes.validation_structure import (
    validate_structure_node,
    route_after_structure_validation
)

from marketing_agent.graphs.learning_content.nodes.validate_prompt_rules import (
    route_after_prompt_validation,
    validate_prompt_rules_node,
)

from marketing_agent.graphs.learning_content.nodes.save_content_request import(
    save_content_request_node,
)

from marketing_agent.graphs.learning_content.state import (
    LearningContentState,
)

from marketing_agent.utils.logger import (
    get_logger,
)

logger = get_logger(__name__)


def initialize_request(
    state: LearningContentState,
) -> dict:
    logger.info(
        "Learning content graph started: "
        "channel_id=%s message_ts=%s",
        state["slack_channel_id"],
        state["slack_message_ts"],
    )

    return {
        "prompt_config": {},
        "knowledge": [],
        "drafts": [],
        "validation_errors": [],
        "retry_count": 0,
        "request_id": None,
    }


def build_learning_content_graph():
    builder = StateGraph(
        LearningContentState
    )
    
    # node 등록 ---------------------------------------------
    builder.add_node(
        "initialize_request",
        initialize_request,
    )
    
    builder.add_node(
            "load_prompt_config",
            load_prompt_config_node,
        )
    
    builder.add_node(
        "search_knowledge",
        search_knowledge_node,
    )
    
    builder.add_node(
        "generate_drafts",
        generate_drafts_node
    )
    
    builder.add_node(
        "validate_structure",
        validate_structure_node
    )
    
    builder.add_node(
        "validate_prompt_rules",
        validate_prompt_rules_node
    )
    
    builder.add_node(
        "save_content_request",
        save_content_request_node
    )

    # edge 등록 ---------------------------------------------
    builder.add_edge(
        START,
        "initialize_request",
    )
    
    builder.add_edge(
        "initialize_request",
        "load_prompt_config",
    )

    builder.add_edge(
        "load_prompt_config",
        "search_knowledge",
    )
    
    builder.add_edge(
        "search_knowledge",
        "generate_drafts",
    )
    
    builder.add_edge(
        "generate_drafts",
        "validate_structure",
    )
    
    builder.add_conditional_edges(
        "validate_structure",
        route_after_structure_validation,
        {
            "retry" : "generate_drafts",
            "success" : "validate_prompt_rules",
            "failed" : END,
        }
    )
    
    builder.add_conditional_edges(
        "validate_prompt_rules",
        route_after_prompt_validation,
        {
            "retry" : "generate_drafts",
            "success" : "save_content_request",
            "failed": END,
        }
    )

    builder.add_edge(
        "save_content_request",
        END,
    )
    
    return builder.compile()


learning_content_graph = (
    build_learning_content_graph()
)