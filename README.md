# Learning Marketing Automation Agent

Slack에서 요청을 받으면 OpenClaw 기반 **Learning Agent**가 Google Sheets 프롬프트와 Qdrant RAG 검색을 활용해 Gemini로 마케팅 콘텐츠 초안을 생성하고, Supabase 공개 URL로 이미지를 준비한 뒤 플랫폼별 Worker가 네이버 블로그 · Instagram · Facebook · Threads에 게시합니다. 게시 결과는 다시 Slack으로 회신됩니다.

**Stack** - Slack · OpenClaw Gateway · LangGraph · GeminiAPI · Google Sheets / Drive · Qdrant · Supabase Storage · Publish Workers ×4

## 1. 전체 시스템 구성도

![Learning Marketing Automation Architecture](docs/architecture.png)

| 레이어 | 구성 요소 |
|---|---|
| ① Channel | 사용자, Slack |
| ② Agent Runtime | OpenClaw Gateway, Learning Agent (Prompt Tool · RAG Search Tool · Publish Tool), Gemini, Other Agent(확장 슬롯) |
| ③ Knowledge · Data | Google Sheets(프롬프트 · 작성 규칙), Google Drive(배경지식 문서), Drive Sync / Embedding, Qdrant(Vector DB), Supabase Storage(이미지 · 공개 URL) |
| ④ Publish | Naver / Instagram / Facebook / Threads Worker |

- Slack 첨부 이미지는 Supabase Storage에 업로드되고, Publish Tool이 업로드를 실행해 공개 URL을 받아 Worker에 넘깁니다.
- 게시 결과와 오류 메시지는 Slack으로 회신됩니다.

## 2. 요청 유형별 처리 흐름

Learning Agent는 Slack 요청을 아래 네 가지 workflow 중 하나로 분기합니다.

### A. 콘텐츠 생성

새 마케팅 콘텐츠 초안을 만듭니다.

```mermaid
flowchart LR
  A1[Slack 요청] --> A2[OpenClaw Gateway] --> A3[Learning Agent]
  A3 --> A4[Sheets 프롬프트 로드] --> A5[Qdrant RAG 검색] --> A6[Gemini 초안 생성] --> A7[Slack 초안 반환]
```

### B. 수정 · 승인

기존 요청에서 필요한 Draft만 갱신합니다.

```mermaid
flowchart LR
  B1[Slack 수정/승인 요청] --> B2[Learning Agent] --> B3[ContentRequest 조회] --> B4[Draft 수정 또는 승인] --> B5[Slack 최신 초안 · 상태 반환]
```

### C. 게시

승인된 콘텐츠를 4개 플랫폼에 배포합니다.

```mermaid
flowchart LR
  C1[Slack 게시 요청] --> C2[Publish Tool] --> C3[Slack 첨부 이미지 수신] --> C4[Supabase 업로드 · 공개 URL]
  C4 --> C5[Naver Worker] & C6[Instagram Worker] & C7[Facebook Worker] & C8[Threads Worker]
  C5 & C6 & C7 & C8 --> C9[게시 결과 수집] --> C10[Slack 성공/실패 보고]
```

### D. 지식 동기화 (백그라운드)

배경지식 문서를 벡터DB에 반영합니다.

```mermaid
flowchart LR
  D1[Drive 문서 변경 감지] --> D2[문서 다운로드] --> D3[텍스트 추출 · 청킹] --> D4[임베딩 생성] --> D5[Qdrant 업데이트] --> D6[이후 RAG 검색에 반영]
```
