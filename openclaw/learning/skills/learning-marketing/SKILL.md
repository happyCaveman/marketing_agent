---
name: learning-marketing
description: 러닝사업부 교육, 자격증, 시험, 행사 관련 마케팅 콘텐츠 생성, 수정, 승인 및 게시 Workflow
---

# Learning Marketing Workflow

이 Skill은 러닝사업부의 마케팅 콘텐츠 생성, 수정, 승인 및 게시 Workflow를 실행합니다.

OpenClaw는 콘텐츠를 직접 작성하지 않습니다.

콘텐츠 작성 규칙과 콘텐츠 유형별 작성 방식은
Google Sheet Prompt와 LangGraph가 관리합니다.

게시 요청에서는 현재 thread의 기존 ContentRequest request_id를 사용한다.
request_id를 추측하거나 새로 만들지 않는다.

`publish_learning_content` 실행 전에 해당 request_id가 실제로 존재하는지 임의 추측하지 말고,
CLI를 그대로 실행한다.


# 1. 새 콘텐츠 생성

새로운 콘텐츠 작성 요청은
반드시 `generate_learning_content`를 사용합니다.

새 콘텐츠에는 다음과 같은 요청이 모두 포함됩니다.

## 현장 후기형

- 시험 감독 후기
- 교육 후기
- 출장 후기
- 설명회 후기
- 세미나 후기
- 행사 후기

## 자격증 정보형

- 자격증 소개
- 신규 자격증 안내
- 자격증 변경 또는 종료 안내
- 자격증 시험 특징 소개
- 자격증 취득 대상 소개
- 자격증 활용 분야 소개

OpenClaw는 두 콘텐츠 유형을 직접 작성하지 않습니다.

콘텐츠 유형 판단은 `generate_learning_content` 내부 LangGraph가 수행합니다.


## 새 콘텐츠 실행

반드시 프로젝트 루트에서 실행합니다.

`cd /Users/sangwhui/Desktop/workspace/marketing_agent && uv run python -m marketing_agent.tools.generate_learning_content --source-text "<현재 Slack 사용자 메시지 원문>" --slack-channel-id "<현재 Slack channel id>" --slack-message-ts "<현재 Slack 원본 message timestamp>" --slack-file-ids "<현재 메시지의 Slack file id 목록>"`


# 2. Raw Input Preservation

`--source-text`에는 사용자의 현재 Slack 메시지를
그대로 전달합니다.

다음을 하지 않습니다.

- 요약
- 문장 수정
- 정보 제거
- 정보 추가
- 홍보 방향 추가
- 사용자의 목적 재해석

예:

사용자 원문:

"오늘 명지대학교에 유니티 시험 교육을 갔어. 학생들 62명 정도 시험 봤어. 초안 작성해줘"

잘못된 전달:

"명지대학교 유니티 교육 콘텐츠 생성"

올바른 전달:

"오늘 명지대학교에 유니티 시험 교육을 갔어. 학생들 62명 정도 시험 봤어. 초안 작성해줘"


# 3. 첨부 파일

현재 Slack 메시지의 모든 file_id를 전달합니다.

예:

F0C6X1GLWQN
F0C72LCQALU

이면:

`--slack-file-ids "F0C6X1GLWQN,F0C72LCQALU"`

첨부 파일이 없으면:

`--slack-file-ids ""`

이전 메시지의 file_id를 사용하지 않습니다.

이미지를 분석하여 콘텐츠 정보를 만들지 않습니다.

이미지는 게시할 원본 미디어 자산으로만 전달합니다.


# 4. Generate Workflow 역할

`generate_learning_content`가 다음 작업을 수행합니다.

- 콘텐츠 유형 판단
- Google Sheet Prompt 조회
- Knowledge Base 검색
- 플랫폼별 Draft 생성
- 구조 검증
- Prompt 규칙 검증
- 필요한 경우 재생성
- ContentRequest 생성
- Slack 이미지 다운로드
- request.json 저장

OpenClaw가 위 작업을 개별적으로 다시 실행하지 않습니다.


# 5. 생성 결과

Tool이 반환한:

- request_id
- drafts

를 그대로 사용합니다.

Draft 내용을 OpenClaw가 다시 작성하지 않습니다.

Slack에서는 다음 내용을 사용자에게 보여줍니다.

[Naver Blog 초안]

제목: ...

본문:
...

해시태그:
...


[Instagram 초안]

본문:
...

해시태그:
...


[Threads 초안]

본문:
...

해시태그:
...

[Facebook 초안]

본문:
...

해시태그:
...


마지막에 자연스럽게 다음과 같이 안내할 수 있습니다.

"내용을 확인해 보시고 수정하거나 승인할 부분이 있으면 말씀해 주세요."


# 6. 기존 콘텐츠 수정 및 승인

기존 ContentRequest 수정 또는 승인 요청은
`review_learning_content`를 사용합니다.

예:

- "네이버 본문을 줄여줘"
- "인스타 해시태그 2개 빼줘"
- "Threads 승인할게"
- "네이버 수정하고 인스타 승인할게"
- "넷 다 승인할게"


## 실행

`cd /Users/sangwhui/Desktop/workspace/marketing_agent && uv run python -m marketing_agent.tools.review_learning_content --instruction "<현재 Slack 사용자 메시지 원문>" --request-id "<현재 ContentRequest request_id>" --slack-channel-id "<현재 Slack channel id>" --slack-message-ts "<현재 Slack 메시지 timestamp>"`

`--instruction`도 사용자의 원문을 그대로 전달합니다.

OpenClaw가 수정 방향을 추가하거나 변경하지 않습니다.


# 7. 콘텐츠 게시

사용자가 게시를 요청하면
`publish_learning_content`를 사용합니다.

예:

- "게시해줘"
- "넷 다 게시해줘"
- "다 승인하고 게시해줘"
- "인스타랑 Threads만 올려줘"


## 실행

`cd /Users/sangwhui/Desktop/workspace/marketing_agent && uv run python -m marketing_agent.tools.publish_learning_content --instruction "<현재 Slack 사용자 메시지 원문>" --request-id "<현재 ContentRequest request_id>" --slack-channel-id "<현재 Slack channel id>" --slack-message-ts "<현재 Slack 메시지 timestamp>"`


# 8. Workflow 우선순위

게시 요청 포함
→ `publish_learning_content`

게시 요청은 없고 수정 또는 승인
→ `review_learning_content`

새로운 콘텐츠 작성
→ `generate_learning_content`


# 9. Legacy Tool 금지

다음 Tool을 직접 사용하지 않습니다.

- create_platform_drafts
- get_learning_prompt
- search_learning_knowledge
- update_platform_draft
- approve_platform_draft
- publish_naver_draft
- publish_instagram_draft
- publish_threads_draft
- publish_facebook_draft

통합 Workflow만 사용합니다.

- generate_learning_content
- review_learning_content
- publish_learning_content


# 10. 실패 처리

Tool 실패 시 OpenClaw가 직접 작업을 대신하지 않습니다.

Tool 실행 결과 없이:

- 초안 생성 완료
- 수정 완료
- 승인 완료
- 게시 완료

라고 말하지 않습니다.


# 11. Source of Truth

OpenClaw의 이전 대화 기억은 Source of Truth가 아닙니다.

현재 사용자 메시지와 ContentRequest,
Google Sheet Prompt,
Knowledge Base가 Source of Truth입니다.