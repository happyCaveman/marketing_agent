---
name: learning-marketing
description: 러닝사업부의 교육, 출장, 시험 감독, 설명회, 세미나, 행사 관련 마케팅 콘텐츠 생성·수정·승인·게시 업무
---

# Learning Marketing

## New Draft

사용자가 새로운 마케팅 콘텐츠 초안을 요청하면
직접 Draft를 작성하지 않는다.

반드시 아래 Python Tool을 실행한다.

`cd /Users/sangwhui/Desktop/workspace/marketing_agent && uv run python -m marketing_agent.tools.generate_learning_content --source-text "<사용자 원문>" --slack-channel-id "<현재 Slack channel id>" --slack-message-ts "<현재 원본 Slack message ts>" --slack-file-ids "<첨부된 Slack file id 목록>"`

첨부 파일이 없으면:

`--slack-file-ids ""`

첨부 파일이 여러 개면 쉼표로 연결한다.

예:

`--slack-file-ids "F001,F002,F003"`

### 중요

새 콘텐츠 요청에서는 다음 Tool을 개별적으로 실행하지 않는다.

- get_learning_prompt
- search_learning_knowledge
- create_platform_drafts

위 작업은 모두 `generate_learning_content` 내부 LangGraph에서 수행한다.

`generate_learning_content`는 사용자 요청 하나당 한 번만 실행한다.

Tool이 반환한:

- request_id
- drafts

를 그대로 사용한다.

OpenClaw가 Draft의 내용을 다시 작성하거나 요약하거나 변경하지 않는다.

각 Draft의 다음 필드를 빠뜨리지 않고 출력한다.

Naver Blog:
- title
- body
- hashtags

Instagram:
- body
- hashtags

Threads:
- body
- hashtags

Tool 실행 전에 사용자에게 초안을 답변하지 않는다.

Tool 실행 없이 request_id를 임의로 만들지 않는다.

초안을 출력한 후 종료한다.
승인이나 게시를 자동으로 진행하지 않는다.


첨부 파일이 있는 경우 반드시 Slack file_id를 확인한 뒤
모든 file_id를 `--slack-file-ids` 인자에 전달한다.

예:

첨부 파일:
- F0C6H8PKJ87
- F0C6WM3HS2J

실행:

`uv run python -m marketing_agent.tools.generate_learning_content \
--source-text "<사용자 메시지>" \
--slack-channel-id "<channel_id>" \
--slack-message-ts "<message_ts>" \
--slack-file-ids "F0C6H8PKJ87,F0C6WM3HS2J"`

첨부 파일이 존재하는데
`--slack-file-ids ""`로 실행해서는 안 된다.

OpenClaw staging 디렉터리의 이미지 경로를
ContentRequest 이미지 경로로 사용하지 않는다.

이미지는 Slack file_id를 통해
generate_learning_content에 전달하고,
ContentRequestService가 data/temp/<request_id>/images에 저장하도록 한다.