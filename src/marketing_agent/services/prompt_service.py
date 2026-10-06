from marketing_agent.config.settings import settings
from marketing_agent.services.google_sheets_service import GoogleSheetsService
from marketing_agent.utils.logger import get_logger

logger = get_logger(__name__)


class PromptService:
    def __init__(self):
        self.google_sheets_service = GoogleSheetsService()
        
    def load_prompts(
        self,
        team: str,
        prompt_names: list[str],
    ) -> dict[str, list[str]]:
        rows = self.google_sheets_service.get_rows(
            settings.google_prompt_sheet_name
        )

        if not rows:
            return {}

        header = rows[0]
        data_rows = rows[1:]

        prompt = {
            "role": [],
            "tone": [],
            "rule": [],
        }

        for row in data_rows:
            row_data = dict(
                zip(
                    header,
                    row,
                )
            )

            if row_data.get("team") != team:
                continue

            if (
                row_data.get("prompt_name")
                not in prompt_names
            ):
                continue

            if (
                row_data.get(
                    "enabled",
                    "",
                ).upper()
                != "TRUE"
            ):
                continue

            section = row_data.get(
                "section"
            )

            content = row_data.get(
                "content"
            )

            if (
                section in prompt
                and content
            ):
                prompt[
                    section
                ].append(
                    content
                )

        logger.info(
            "Loaded prompt configs: "
            "team=%s prompts=%s",
            team,
            prompt_names,
        )

        return prompt

    def load_prompt(
        self,
        team: str,
        prompt_name: str,
    ) -> dict[str, list[str]]:
        rows = self.google_sheets_service.get_rows(
            settings.google_prompt_sheet_name
        )

        if not rows:
            return {}

        header = rows[0]
        data_rows = rows[1:]

        prompt = {
            "role": [],
            "tone": [],
            "rule": [],
        }

        for row in data_rows:
            row_data = dict(zip(header, row))

            if row_data.get("team") != team:
                continue

            if row_data.get("prompt_name") != prompt_name:
                continue

            if row_data.get("enabled", "").upper() != "TRUE":
                continue

            section = row_data.get("section")
            content = row_data.get("content")

            if section in prompt and content:
                prompt[section].append(content)

        logger.info(
            "Loaded prompt config: team=%s, prompt=%s",
            team,
            prompt_name,
        )

        return prompt