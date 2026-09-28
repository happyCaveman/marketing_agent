from marketing_agent.agents.learning_agent import LearningAgent
from marketing_agent.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    logger.info("Marketing Agent started")

    learning_agent = LearningAgent()

    user_request = input("요청을 입력하세요: ")

    response = learning_agent.run(user_request)

    print("\n--- 결과 ---")
    print(response)


if __name__ == "__main__":
    main()