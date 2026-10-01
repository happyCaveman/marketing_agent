import httpx

from marketing_agent.config.settings import settings
from marketing_agent.utils.logger import get_logger


logger = get_logger(__name__)


class SlackNotificationService:
    def __init__(self):
        self.bot_token = settings.slack_bot_token

        self.headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json",
        }

    def send_message(
        self,
        channel_id: str,
        text: str,
    ) -> None:
        response = httpx.post(
            "https://slack.com/api/chat.postMessage",
            headers=self.headers,
            json={
                "channel": channel_id,
                "text": text,
            },
            timeout=30.0,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("ok"):
            raise RuntimeError(
                f"Slack message failed: {data.get('error')}"
            )

    def notify_publish_failure(
        self,
        channel_id: str,
        platform: str,
        step: str,
        error: str,
    ) -> None:
        message = (
            f"🚨 {platform} 자동 게시에 실패했습니다.\n"
            f"- 실패 단계: {step}\n"
            f"- 오류: {error}\n"
            f"게시 작업을 중단했습니다. 자동화 코드를 확인해 주세요."
        )

        self.send_message(
            channel_id=channel_id,
            text=message,
        )