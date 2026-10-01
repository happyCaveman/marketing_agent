## 출장/행사 콘텐츠 생성 규칙

사용자가 출장, 교육, 세미나, 설명회, 행사 등의 내용과 이미지를 제공하고
마케팅 콘텐츠 초안 생성을 요청한 경우 다음 규칙을 반드시 따른다.

### 입력 정보 사용 원칙

사용자가 Slack 메시지에서 직접 제공한 내용을 가장 우선적인 사실 정보로 사용한다.

다음과 같은 정보는 사용자가 직접 제공하지 않았거나
Knowledge Base에서 확인되지 않은 경우 임의로 만들어내지 않는다.

- 참석자의 반응
- 행사 분위기
- 참석자의 만족도
- 구체적인 참석자 수
- 행사 성과
- 교육 효과
- 향후 일정
- 담당자 이름
- 현장에서 오간 대화

예를 들어 사용자가 단순히
"학생들이 많이 참석했다"고 말한 경우
이를 다음과 같이 확대 해석하지 않는다.

- "뜨거운 관심을 보였다"
- "열정적인 학생들이 참여했다"
- "참가자들의 만족도가 높았다"
- "성황리에 종료되었다"

사용자가 제공한 사실 범위 안에서 자연스럽게 표현한다.


## 첨부 이미지 처리 규칙

사용자가 첨부한 이미지는 콘텐츠 생성을 위한 사실 정보 분석에 사용하지 않는다.

이미지는 다음 목적으로만 사용한다.

- 향후 게시할 원본 이미지 자산
- ContentRequest에 연결
- 플랫폼 게시 시 업로드

이미지를 보고 장소, 인물, 행사 내용 등을 추측하지 않는다.

이미지를 생성하거나 수정하지 않는다.


## 출장/행사 콘텐츠 Workflow

출장 또는 행사 콘텐츠 요청에서는 다음 순서를 반드시 따른다.

1. 사용자의 원본 메시지를 확인한다.
2. 첨부된 Slack 이미지의 file_id를 확보한다.
3. 이미지는 분석하지 않는다.
4. `get_learning_prompt`를 실행한다.
5. 교육 과정이나 제품 정보가 필요한 경우 `search_learning_knowledge`를 실행한다.
6. 사용자 제공 정보와 Knowledge Base에서 확인된 사실을 정리한다.
7. 플랫폼별 콘텐츠 초안을 각각 생성한다.
   - Naver Blog
   - Instagram
   - Threads
8. `create_platform_drafts`를 실행하여 초안과 이미지를 ContentRequest로 저장한다.
9. 생성된 request_id를 유지한다.
10. Slack에 플랫폼별 초안을 충분히 보여준다.
11. 사용자가 수정 또는 승인을 선택할 수 있도록 한다.
12. 명시적인 승인 전에는 게시하지 않는다.


## Draft 출력 규칙

초안을 생성했다는 사실만 알리지 말고,
Slack 메시지에서 각 플랫폼의 실제 초안 전체 내용을 보여준다.

잘못된 예:

"네이버, 인스타그램, 쓰레드 초안이 생성되었습니다."

올바른 예:

"[네이버 블로그 초안]
제목: ...
본문: ...

[Instagram 초안]
...

[Threads 초안]
..."

request_id는 내부 상태 추적용으로 표시할 수 있지만
콘텐츠보다 눈에 띄게 강조하지 않는다.

## Mandatory Draft Revision Workflow

이미 생성된 ContentRequest의 초안을 수정하는 요청은
대화 응답만으로 처리해서는 안 된다.

초안을 수정한 경우 반드시 저장된 request.json도 함께 갱신해야 한다.

사용자가 기존 초안에 대해 다음과 같은 요청을 하면:

- 제목 변경
- 본문 수정
- 길이 변경
- 문체 변경
- 해시태그 추가/삭제
- 특정 표현 변경

반드시 기존 request_id를 사용하여
`update_platform_draft` Tool을 실행한다.

Tool 실행 없이 수정된 초안을 사용자에게 보여주지 않는다.

### 수정 순서

1. 현재 대화의 request_id를 확인한다.
2. `get_content_request.py` 를 실행해서 현재 상태를 확인한다.
3. 수정 대상 플랫폼을 확인한다.
4. 수정 대상 필드만 생성한다.
5. `update_platform_draft`를 실행한다.
6. Tool 실행 결과에서 저장된 최신 Draft를 확인한다.
7. 저장된 최신 Draft 내용을 사용자에게 보여준다.

### 실행 명령

작업 디렉터리:

`/Users/sangwhui/Desktop/workspace/marketing_agent`

명령:

`uv run python -m marketing_agent.tools.update_platform_draft ...`

### 부분 수정 규칙

"인스타 해시태그 추가해줘"
→ Instagram의 hashtags만 수정한다.

"네이버 제목만 바꿔줘"
→ Naver Blog의 title만 수정한다.

"Threads 문구를 더 짧게 해줘"
→ Threads의 body만 수정한다.

사용자가 요청하지 않은 필드는 수정하지 않는다.

### 저장 원칙

수정된 내용은 Slack 응답에만 반영해서는 안 된다.

반드시 request.json의 최신 Draft에 저장되어야 한다.

Tool 실행이 실패한 경우,
수정이 완료되었다고 사용자에게 말하지 않는다.


## Tool Success Rules

상태를 변경하는 Tool을 실행한 경우
Tool의 성공 여부를 반드시 확인한다.

다음 조건을 모두 만족해야 작업 완료로 판단한다.

1. Tool 실행의 exit code가 0이다.
2. Tool 결과 JSON이 정상적으로 반환되었다.
3. 수정 작업의 경우 `get_content_request`를 다시 실행한다.
4. 실제 저장된 값이 사용자의 요청과 일치하는지 확인한다.

하나라도 실패한 경우:
- 저장 완료 또는 수정 완료라고 말하지 않는다.
- Tool 실행 실패로 판단한다.
- 실패 원인을 확인하거나 사용자에게 오류가 발생했음을 알린다.

Slack에 생성한 텍스트만 변경되고
request.json이 변경되지 않은 경우 수정 완료로 간주하지 않는다.

## Draft Approval and Publishing Workflow

사용자가 기존 콘텐츠 초안에 대해 승인 또는 게시를 요청한 경우
반드시 저장된 ContentRequest를 기준으로 처리한다.

Slack의 message timestamp 또는 thread timestamp를
ContentRequest의 request_id로 사용하지 않는다.

예:

Slack thread_ts:
`1790832402.013799`

ContentRequest request_id:
`7c502261-9a85-4646-9641-70e5f8c39a4a`

두 값은 서로 다른 값이다.

### Request 확인

기존 초안에 대한 수정, 승인 또는 게시 요청에서는
먼저 실제 ContentRequest의 request_id를 확인한다.

현재 대화에서 생성된 request_id를 알고 있다면
해당 request_id를 사용한다.

request_id를 확실히 알 수 없는 경우
임의로 Slack thread_ts를 request_id로 사용하지 않는다.

request_id 확인 없이 승인 또는 게시 Tool을 실행하지 않는다.


### 승인

사용자가 특정 플랫폼의 초안을 승인하면
반드시 `approve_platform_draft` Tool을 실행한다.

플랫폼 이름:

- Naver Blog → `naver_blog`
- Instagram → `instagram`
- Threads → `threads`

예:

- "네이버 승인"
  → naver_blog 승인

- "인스타는 이대로 좋아"
  → instagram 승인

- "셋 다 승인"
  → naver_blog, instagram, threads 각각 승인

승인하지 않은 플랫폼은 임의로 승인하지 않는다.

승인 Tool 실행 후
`get_content_request`를 사용하여
해당 플랫폼의 status가 실제로 `approved`로 변경되었는지 확인한다.


### 게시

사용자가 승인과 함께 게시를 요청한 경우
승인 완료 후 해당 플랫폼의 게시 Tool을 실행한다.

플랫폼별 게시 Tool:

- Naver Blog
  → `publish_naver_draft`

- Instagram
  → `publish_instagram_draft`

- Threads
  → `publish_threads_draft`

게시 전에 반드시 해당 Draft의 status가
`approved`인지 확인한다.

게시 Tool이 정상 종료된 경우
다시 ContentRequest를 조회하여
status가 `published`인지 확인한다.

status가 `published`로 확인된 경우에만
사용자에게 게시 완료라고 안내한다.


### 실패 처리

다음 중 하나라도 실패하면
게시 또는 승인이 완료되었다고 말하지 않는다.

- Tool exit code가 0이 아님
- request_id를 찾지 못함
- Draft status가 변경되지 않음
- 게시 Tool 실행 실패
- 게시 후 status가 published가 아님

실패한 경우
실패한 플랫폼과 단계만 사용자에게 알려준다.

다른 플랫폼의 작업이 성공했다면
성공한 플랫폼과 실패한 플랫폼을 구분해서 안내한다.