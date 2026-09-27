from marketing_agent.utils.logger import get_logger
from marketing_agent.services.llm_service import LLMService

logger = get_logger(__name__)


def main() -> None:
    logger.info("Marketing Agent started")
    llm_service = LLMService()
    response = llm_service.generate_text(
        "기업 대상 AI 교육 홍보 문구 3문장 작성해줘"
    )
    
    print(response)


if __name__ == "__main__":
    main()