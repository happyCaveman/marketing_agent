import asyncio

from playwright.async_api import async_playwright

from marketing_agent.config.settings import (
    PROJECT_ROOT,
    settings,
)


AUTH_DIR = PROJECT_ROOT / "data" / "auth"
AUTH_FILE = AUTH_DIR / "naver.json"


async def main() -> None:
    AUTH_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False,
        )

        context = await browser.new_context()

        page = await context.new_page()

        await page.goto(
            "https://nid.naver.com/nidlogin.login"
        )

        print()
        print("네이버 로그인을 직접 완료해 주세요.")
        print("로그인 완료 후 네이버 메인 화면이 보이면")
        print("터미널로 돌아와 Enter를 눌러주세요.")
        print()

        input("로그인 완료 후 Enter: ")

        await page.goto(
            settings.naver_blog_url
        )

        input(
            "블로그가 로그인 상태인지 확인 후 Enter: "
        )

        write_url = (
            f"{settings.naver_blog_url}"
            "?Redirect=Write&"
        )

        await page.goto(
            write_url
        )

        input(
            "글쓰기 화면이 정상적으로 열렸는지 확인 후 Enter: "
        )

        await context.storage_state(
            path=str(AUTH_FILE)
        )

        print()
        print(
            f"네이버 로그인 상태 저장 완료: {AUTH_FILE}"
        )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())