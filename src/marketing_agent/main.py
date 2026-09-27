from marketing_agent.config.settings import settings
from marketing_agent.utils.logger import get_logger


logger = get_logger(__name__)


def main() -> None:
    logger.info("Marketing Agent started")
    logger.info("Environment: %s", settings.app_env)


if __name__ == "__main__":
    main()