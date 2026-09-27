from google import genai

from marketing_agent.config.settings import settings
from marketing_agent.utils.logger import get_logger


logger = get_logger(__name__)


class LLMService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    def generate_text(self, prompt: str) -> str:
        logger.info("Sending request to Gemini")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        logger.info("Received response from Gemini")

        return response.text