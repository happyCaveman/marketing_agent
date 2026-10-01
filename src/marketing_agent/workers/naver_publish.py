import re
from pathlib import Path

from playwright.async_api import (
    FrameLocator,
    Page,
    async_playwright,
)

from marketing_agent.config.settings import (
    PROJECT_ROOT,
    settings,
)
from marketing_agent.services.slack_notification_service import (
    SlackNotificationService,
)
from marketing_agent.utils.logger import get_logger


logger = get_logger(__name__)


AUTH_FILE = (
    PROJECT_ROOT
    / "data"
    / "auth"
    / "naver.json"
)


MAIN_FRAME_SELECTOR = 'iframe[name="mainFrame"]'

EDITOR_FRAME_SELECTOR = (
    'iframe[title=" 스마트 에디터, 접근성 도움말은 alt + 0 "]'
)

HELP_CLOSE_SELECTOR = (
    "button.se-help-panel-close-button"
)


class NaverPublishWorker:
    def __init__(
        self,
        slack_channel_id: str,
    ):
        self.slack_channel_id = slack_channel_id
        self.slack_notification_service = (
            SlackNotificationService()
        )

    async def publish(
        self,
        title: str,
        body: str,
        image_paths: list[str] | None = None,
    ) -> None:
        image_paths = image_paths or []

        if not AUTH_FILE.exists():
            raise RuntimeError(
                "Naver auth file does not exist. "
                "Run setup_naver_auth first."
            )

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=False,
            )

            context = await browser.new_context(
                storage_state=str(AUTH_FILE)
            )

            page = await context.new_page()

            try:
                await self._run_step(
                    step="글쓰기 화면 이동",
                    action=lambda: self._open_write_page(
                        page
                    ),
                )

                await self._run_step(
                    step="로그인 상태 확인",
                    action=lambda: self._ensure_logged_in(
                        page
                    ),
                )

                main_frame = self._get_main_frame(
                    page
                )

                await self._close_help_panel_if_visible(
                    main_frame
                )

                await self._run_step(
                    step="제목 입력",
                    action=lambda: self._fill_title(
                        main_frame=main_frame,
                        title=title,
                    ),
                )

                await self._run_step(
                    step="본문 입력",
                    action=lambda: self._fill_body(
                        main_frame=main_frame,
                        body=body,
                    ),
                )

                if image_paths:
                    await self._run_step(
                        step="이미지 업로드",
                        action=lambda: self._upload_images(
                            page=page,
                            main_frame=main_frame,
                            image_paths=image_paths,
                        ),
                    )

                await self._run_step(
                    step="1차 발행",
                    action=lambda: self._click_publish(
                        main_frame
                    ),
                )

                await self._run_step(
                    step="최종 발행",
                    action=lambda: self._click_final_publish(
                        main_frame
                    ),
                )
                
                await page.wait_for_timeout(5000)

                logger.info(
                    "URL after final publish: %s",
                    page.url,
                )
                

                logger.info(
                    "Naver Blog published successfully."
                )

            finally:
                await context.close()
                await browser.close()

    async def _run_step(
        self,
        step: str,
        action,
    ) -> None:
        try:
            await action()

            logger.info(
                "Naver publish step succeeded: %s",
                step,
            )

        except Exception as error:
            logger.exception(
                "Naver publish step failed: %s",
                step,
            )

            self.slack_notification_service.notify_publish_failure(
                channel_id=self.slack_channel_id,
                platform="Naver Blog",
                step=step,
                error=str(error),
            )

            raise

    async def _open_write_page(
        self,
        page: Page,
    ) -> None:
        write_url = (
            f"{settings.naver_blog_url}"
            "?Redirect=Write&"
        )

        await page.goto(
            write_url,
            wait_until="domcontentloaded",
        )

        logger.info(
            "Opened Naver write page: %s",
            write_url,
        )

    async def _ensure_logged_in(
        self,
        page: Page,
    ) -> None:
        current_url = page.url

        logger.info(
            "Current Naver URL: %s",
            current_url,
        )

        if (
            "nid.naver.com" in current_url
            or "nidlogin" in current_url
        ):
            raise RuntimeError(
                "Naver login session has expired."
            )

    def _get_main_frame(
        self,
        page: Page,
    ) -> FrameLocator:
        return page.frame_locator(
            MAIN_FRAME_SELECTOR
        )

    def _get_editor_frame(
        self,
        main_frame: FrameLocator,
    ) -> FrameLocator:
        return main_frame.frame_locator(
            EDITOR_FRAME_SELECTOR
        )

    async def _close_help_panel_if_visible(
        self,
        main_frame: FrameLocator,
    ) -> None:
        close_button = main_frame.locator(
            HELP_CLOSE_SELECTOR
        )

        if (
            await close_button.count() > 0
            and await close_button.is_visible()
        ):
            await close_button.click()

            logger.info(
                "Closed Naver help panel."
            )

    async def _fill_title(
        self,
        main_frame: FrameLocator,
        title: str,
    ) -> None:
        title_paragraph = (
            main_frame
            .get_by_role("paragraph")
            .filter(
                has_text=re.compile(r"^제목$")
            )
        )

        await title_paragraph.click()

        editor_frame = self._get_editor_frame(
            main_frame
        )

        editor_body = editor_frame.locator(
            "body"
        )

        await editor_body.fill(
            title,
            force=True,
        )

    async def _fill_body(
        self,
        main_frame: FrameLocator,
        body: str,
    ) -> None:
        body_paragraph = (
            main_frame
            .get_by_role("paragraph")
            .filter(
                has_text=(
                    "글감과 함께 나의 일상을 기록해보세요!"
                )
            )
        )

        await body_paragraph.click()

        editor_frame = self._get_editor_frame(
            main_frame
        )

        editor_body = editor_frame.locator(
            "body"
        )

        await editor_body.fill(
            body,
            force=True,
        )

    async def _upload_images(
        self,
        page: Page,
        main_frame: FrameLocator,
        image_paths: list[str],
    ) -> None:
        normalized_paths = []

        for image_path in image_paths:
            path = Path(image_path)

            if not path.is_absolute():
                path = (
                    PROJECT_ROOT / path
                )

            if not path.exists():
                raise FileNotFoundError(
                    f"Image file not found: {path}"
                )

            normalized_paths.append(
                str(path)
            )

        photo_button = main_frame.get_by_role(
            "button",
            name="사진 추가",
        )

        await photo_button.click()

        file_input = main_frame.locator(
            "#hidden-file"
        )

        await file_input.set_input_files(
            normalized_paths
        )
        
        if len(normalized_paths) > 1:
            await self._select_multi_image_layout_if_visible(
                main_frame
            )
        
        await page.wait_for_timeout(3000)

        logger.info(
            "Uploaded %s image(s).",
            len(normalized_paths),
        )
        
        
        

    async def _click_publish(
        self,
        main_frame: FrameLocator,
    ) -> None:
        publish_button = main_frame.get_by_role(
            "button",
            name="발행",
        )

        await publish_button.click()

    async def _click_final_publish(
        self,
        main_frame: FrameLocator,
    ) -> None:
        final_publish_button = (
            main_frame.get_by_test_id(
                "seOnePublishBtn"
            )
        )

        await final_publish_button.click()
        
    async def _select_multi_image_layout_if_visible(
        self,
        main_frame: FrameLocator,
    ) -> None:
        option = main_frame.get_by_text(
            "개별사진",
            exact=True,
        )

        try:
            await option.wait_for(
                state="visible",
                timeout=3000,
            )
        except Exception:
            return

        await option.click()

        logger.info(
            "Selected Naver multi-image layout: 개별사진"
        )