import asyncio

from playwright.async_api import async_playwright

from marketing_agent.config.settings import (
    PROJECT_ROOT,
    settings,
)


AUTH_FILE = (
    PROJECT_ROOT
    / "data"
    / "auth"
    / "naver.json"
)


async def main() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False,
        )

        context = await browser.new_context(
            storage_state=str(AUTH_FILE)
        )

        page = await context.new_page()

        write_url = (
            f"{settings.naver_blog_url}"
            "?Redirect=Write&"
        )

        await page.goto(
            write_url
        )

        print(
            "현재 URL:",
            page.url,
        )

        input(
            "로그인 없이 글쓰기 화면이 열렸는지 확인 후 Enter: "
        )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())