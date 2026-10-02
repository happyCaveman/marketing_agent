from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from marketing_agent.models.platform_draft import (
    PlatformDraft,
)


RequestStatus = Literal[
    "created",
    "pending_review",
    "partially_approved",
    "approved",
    "publishing",
    "completed",
    "failed",
]


class ContentImage(BaseModel):
    slack_file_id: str | None = None
    local_path: str


class ContentRequest(BaseModel):
    request_id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    team: str = "learning"
    
    slack_channel_id: str | None = None
    slack_message_ts: str | None = None

    source_text: str

    images: list[ContentImage] = Field(
        default_factory=list
    )

    drafts: list[PlatformDraft] = Field(
        default_factory=list
    )

    status: RequestStatus = "created"

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )
