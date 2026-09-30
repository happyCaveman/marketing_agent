from typing import Literal

from pydantic import BaseModel, Field, model_validator


PlatformName = Literal[
    "naver_blog",
    "instagram",
    "threads",
]

DraftStatus = Literal[
    "pending_review",
    "revision_requested",
    "approved",
    "published",
    "failed",
]


class PlatformDraft(BaseModel):
    platform: PlatformName

    title: str | None = None
    body: str

    hashtags: list[str] = Field(
        default_factory=list
    )

    image_indexes: list[int] = Field(
        default_factory=list
    )

    status: DraftStatus = "pending_review"

    @model_validator(mode="after")
    def validate_platform_fields(self):
        if (
            self.platform == "instagram"
            and not self.hashtags
        ):
            raise ValueError(
                "Instagram draft requires hashtags."
            )

        return self