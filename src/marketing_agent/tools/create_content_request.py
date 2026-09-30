import json

from marketing_agent.models.platform_draft import (
    PlatformDraft,
)
from marketing_agent.services.content_request_service import (
    ContentRequestService,
)


def main() -> None:
    drafts = [
        PlatformDraft(
            platform="naver_blog",
            title="OO대학교 설명회 후기",
            body=(
                "OO대학교에서 진행한 "
                "교육 설명회 현장을 소개합니다."
            ),
        ),
        PlatformDraft(
            platform="instagram",
            body=(
                "OO대학교에서 Adobe와 Autodesk "
                "교육 과정을 소개했습니다."
            ),
            hashtags=[
                "#Adobe",
                "#Autodesk",
                "#교육",
            ],
        ),
        PlatformDraft(
            platform="threads",
            body=(
                "오늘 OO대학교에서 "
                "교육 설명회를 진행했습니다."
            ),
        ),
    ]

    service = ContentRequestService()

    request = service.create_request(
        source_text=(
            "OO대학교 설명회 출장. "
            "Adobe와 Autodesk 과정을 소개했습니다."
        ),
        drafts=drafts,
        image_paths=[
            "apple.jpg"
        ]
    )

    print(
        json.dumps(
            request.model_dump(
                mode="json"
            ),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()