import asyncio

from marketing_agent.workers.naver_publish import (
    NaverPublishWorker,
)


async def main() -> None:
    worker = NaverPublishWorker(
        slack_channel_id="C0C4WD4HDQS",
    )

    await worker.publish(
        title="Playwright 네이버 자동화 테스트",
        body=(
            "Playwright를 사용한 네이버 블로그 "
            "자동 게시 테스트입니다.\n\n"
            "이미지 업로드와 실제 발행까지 확인합니다."
        ),
        image_paths=[
            "apple.jpg",
        ],
    )


if __name__ == "__main__":
    asyncio.run(main())