from marketing_agent.services.llm_service import LLMService
from marketing_agent.services.prompt_service import PromptService
from marketing_agent.utils.logger import get_logger


logger = get_logger(__name__)


class LearningAgent:
    def __init__(self):
        self.llm_service = LLMService()
        self.prompt_service = PromptService()

    def run(self, user_request: str) -> str:
        logger.info("Learning Agent started")

        prompt_config = self.prompt_service.load_prompt(
            team="learning",
            prompt_name="system",
        )

        prompt = self._build_prompt(
            prompt_config=prompt_config,
            user_request=user_request,
        )

        response = self.llm_service.generate_text(prompt)

        logger.info("Learning Agent finished")

        return response

    def _build_prompt(
        self,
        prompt_config: dict[str, list[str]],
        user_request: str,
    ) -> str:
        role = "\n".join(prompt_config.get("role", []))

        tone = "\n".join(
            f"- {item}"
            for item in prompt_config.get("tone", [])
        )

        rules = "\n".join(
            f"- {item}"
            for item in prompt_config.get("rule", [])
        )

        return f"""
[역할]
{role}

[작성 방식]
{tone}

[규칙]
{rules}

[사용자 요청]
{user_request}
""".strip()