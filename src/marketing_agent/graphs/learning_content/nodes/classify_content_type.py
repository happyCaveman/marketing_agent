from marketing_agent.graphs.learning_content.state import (
    LearningContentState,
)
from marketing_agent.services.llm_service import (
    LLMService,
)
from marketing_agent.utils.logger import (
    get_logger,
)


logger = get_logger(__name__)


ALLOWED_CONTENT_TYPES = {
    "event_review",
    "certification_info",
}


def classify_content_type_node(
    state: LearningContentState,
) -> dict:
    return {"content_type": classify_content_type(state["source_text"])}


def classify_content_type(source_text: str) -> str:

    logger.info(
        "Classifying learning content type."
    )

    prompt = f"""
다음 사용자 요청을 아래 두 종류 중 정확히 하나로 분류하세요.

event_review:
사용자가 실제로 다녀온 시험 감독, 교육, 설명회, 세미나,
출장, 행사 등의 경험을 바탕으로 후기를 작성하려는 요청.

certification_info:
특정 자격증 자체의 소개, 신규 출시, 변경, 종료,
시험 특징, 취득 대상, 활용 분야 등을 설명하려는 요청.

중요:
사용자가 실제로 "다녀왔다", "진행했다", "감독했다",
"교육을 갔다", "세미나에 참석했다" 등 자신의 현장 경험을 말하면
관련 자격증 정보가 포함되어 있더라도 event_review를 우선합니다.

예시:

"오늘 한양대에서 AutoCAD 시험 감독 다녀왔어"
→ event_review

"오늘 기업 임직원 대상으로 AI-900 설명회 다녀왔어"
→ event_review

"AI-901 자격증이 새로 출시되는데 소개글 작성해줘"
→ certification_info

"AI-900과 AI-901 차이를 설명하는 게시글 작성해줘"
→ certification_info

사용자 요청:

{source_text}

반드시 아래 두 문자열 중 하나만 출력하세요.

event_review
certification_info
""".strip()

    llm_service = LLMService()

    response = (
        llm_service.generate_text(
            prompt=prompt
        )
        .strip()
        .lower()
    )

    if response not in ALLOWED_CONTENT_TYPES:
        raise RuntimeError(
            "Invalid content type returned "
            f"by LLM: {response}"
        )

    logger.info(
        "Learning content type classified: %s",
        response,
    )

    return response
