---
name: learning-marketing
description: 러닝사업부 마케팅 콘텐츠 생성, 수정, 승인 및 게시
---

# Learning Marketing

러닝사업부의 교육, 설명회, 세미나, 출장,
시험 감독 및 행사 관련 마케팅 콘텐츠를 작성한다.


## 콘텐츠 생성 규칙

사용자가 제공한 사실만 사용한다.

사용자가 말하지 않은 다음 내용은 임의로 만들지 않는다.

- 참석자의 반응
- 열정
- 만족도
- 행사 분위기
- 성과
- 교육 효과
- 감정

예를 들어 사용자가 단순히
"학생 35명이 시험을 봤다"고 말한 경우

- 열정적으로 시험에 참여했다
- 뜨거운 관심을 보였다
- 모습이 인상적이었다
- 좋은 결과가 있기를 바란다

등의 내용을 임의로 추가하지 않는다.

첨부 이미지는 내용 분석에 사용하지 않고
게시용 원본 이미지로만 사용한다.


## 플랫폼별 작성 방식

### Naver Blog

- 제목을 작성한다.
- 세 플랫폼 중 가장 상세하게 작성한다.
- 기본 3~5개 문단으로 작성한다.
- 사용자가 제공한 사실을 자연스럽게 풀어서 작성한다.
- 마지막에 관련 해시태그 4~8개를 작성한다.

### Instagram

- Naver보다 짧고 읽기 쉽게 작성한다.
- 2~4개의 짧은 문장 또는 문단을 작성한다.
- 마지막에 해시태그 5~10개를 작성한다.

### Threads

- 업무 현장을 가볍게 공유하는 문체로 작성한다.
- 3~6개의 짧은 문장을 작성한다.
- 마지막에 해시태그 2~5개를 작성한다.


# Workflow


## 새 초안

사용자가 초안 작성을 요청하면:

1. Naver Blog, Instagram, Threads 초안을 작성한다.
2. 모든 첨부 이미지와 세 Draft를
   `create_platform_drafts`로 저장한다.
3. 반환된 request_id를 유지한다.
4. 실제 Draft 내용을 사용자에게 보여준다.
5. 여기서 종료한다.

초안 요청에서는 승인하거나 게시하지 않는다.


## 수정

기존 Draft 수정 요청이면:

1. 기존 request_id를 사용한다.
2. `get_content_request`로 현재 내용을 확인한다.
3. 요청받은 내용만 수정한다.
4. `update_platform_draft`로 저장한다.
5. 수정된 내용을 보여준다.
6. 종료한다.


## 승인

승인 요청이면:

1. 기존 request_id를 사용한다.
2. 요청받은 플랫폼에 대해
   `approve_platform_draft`를 실행한다.
3. 승인 결과를 안내한다.
4. 종료한다.

승인만 요청받은 경우 게시하지 않는다.


## 게시

게시 요청이면:

- Naver Blog → `publish_naver_draft`
- Instagram → `publish_instagram_draft`
- Threads → `publish_threads_draft`

요청받은 플랫폼의 게시 Tool을 실행하고
실제 결과를 사용자에게 알려준다.


## 중요

새 콘텐츠 요청 하나에는
ContentRequest 하나만 만든다.

이미지가 여러 장이어도
하나의 ContentRequest에 모두 저장한다.

기존 Draft 수정 시
새 ContentRequest를 만들지 않는다.

Slack timestamp를 request_id로 사용하지 않는다.