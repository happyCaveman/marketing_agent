from marketing_agent.graphs.learning_content.state import (
    LearningContentState,
)
from marketing_agent.services.prompt_service import (
    PromptService,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


def load_prompt_config_node(
    state: LearningContentState,
) -> dict:
    logger.info(
        "Loading learning marketing prompt config."
    )

    prompt_service = PromptService()

    prompt_config = prompt_service.load_prompt(
        team="learning",
        prompt_name="system",
    )

    if not prompt_config:
        raise RuntimeError(
            "Learning marketing prompt config is empty."
        )

    has_prompt_content = any(
        prompt_config.get(section)
        for section in (
            "role",
            "tone",
            "rule",
        )
    )

    if not has_prompt_content:
        raise RuntimeError(
            "Learning marketing prompt config "
            "contains no enabled prompt content."
        )

    logger.info(
        "Learning marketing prompt config loaded: "
        "role=%s tone=%s rule=%s",
        len(prompt_config.get("role", [])),
        len(prompt_config.get("tone", [])),
        len(prompt_config.get("rule", [])),
    )

    return {
        "prompt_config": prompt_config,
    }