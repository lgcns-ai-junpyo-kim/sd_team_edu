# secondsession

이 프로젝트는 LangGraph/LangChain 초급자를 대상으로 한 **서비스 레이어 중심 실전형 교육 코스**입니다.  
폴백 패턴, 라우팅, 병렬 그래프, 스트리밍, Redis 캐시, 체크포인터까지 단계적으로 학습합니다.

## 교육 방향성

- **폴백 패턴을 설계 규칙으로** 먼저 정의하고 Enum 기반 에러 코드로 통일한다.
- **상태 전이/라우팅을 정책화**해서 조건/정책/점수/동적 전이를 명확히 분리한다.
- **병렬 실행을 그래프 수준에서 이해**하고 팬아웃/팬인을 안정적으로 합류한다.
- **요청/스트리밍 엔드포인트를 분리**해 비동기 실행 구조를 만든다.
- **Redis rpush/lpop 캐시**로 스트리밍 이벤트를 생산/소비한다.
- **체크포인터로 대화 복구**를 보장하고 메타데이터를 남긴다.

## 학습 콘텐츠

- 교재 문서: `docs/`
  - 01_langgraph_to_service: 폴백 패턴/병렬/상태 전이
  - 02_backend_service_layer: 토큰·메타데이터 스트리밍, Redis 큐, 엔드포인트 분리
  - 03_langgraph_checkpoint: 체크포인터 개요/원리/인메모리 구현
- 코드 템플릿: `src/secondsession/`
- 워커/큐 템플릿: `src/secondsession/core/worker/`, `src/secondsession/core/common/queue/`
- 대화 API 엔드포인트: `/chat/*`

## 구현해야 하는 과제(핵심)

아래 항목은 코드의 `TODO`/`NotImplementedError`를 기준으로 정리했습니다.  
학습자는 각 항목을 구현해 **스트리밍 대화 서비스 + 체크포인터 복구 흐름**을 완성합니다.

### 1) API/서비스 레이어 구현

- `src/secondsession/api/chat/service/chat_service.py`
  - `create_job`: job_id/trace_id/thread_id 생성, 큐 적재, 체크포인터 연결
  - `stream_events`: Redis 이벤트 소비 → SSE(`data: {...}`) 전송 → `done` 종료
  - `get_status`: 상태 조회 및 진행률 반환
  - `cancel`: 취소 플래그 기록
  - error/metadata/done 전송 순서와 seq 단조 증가 규칙 정의

### 2) 스트리밍/큐/워커 실행 흐름

- 워커가 **큐에서 작업을 꺼내 LangGraph 실행**
- 실행 중 **token/metadata/error/done 이벤트를 Redis에 rpush**
- API는 Redis에서 lpop으로 이벤트 소비 후 SSE 전송
- 폴백/에러 발생 시에도 `done` 이벤트로 정상 종료
- `src/secondsession/core/common/queue/chat_job_queue.py`
  - 작업 적재/소비 규칙(rpush/lpop, key 정책, 직렬화) 구현
- `src/secondsession/core/common/queue/chat_stream_event_queue.py`
  - 스트리밍 이벤트 적재/소비 규칙(rpush/lpop, done 보장) 구현
- `src/secondsession/core/worker/chat_worker.py`
  - 큐 소비 → 그래프 실행 → 이벤트 적재까지의 워커 실행 흐름 구현

#### 2-1) Redis 키/페이로드 규칙(고정)

- 작업 큐 키: `chat:jobs`
  - 적재 페이로드 예시(필수 필드 기준)
    - `job_id`, `trace_id`, `thread_id`, `query`
    - `history`, `turn_count`, `user_id`, `metadata`(선택)
- 스트리밍 이벤트 키: `chat:stream:{job_id}`
  - `job_id`별로 리스트를 분리해 순서를 보장한다.
- 취소 플래그 키(권장): `chat:cancel:{job_id}`
  - `cancel` 구현 시 워커가 주기적으로 확인한다.

#### 2-2) 스트리밍 이벤트 스키마(고정)

`ChatStreamEvent` 기준으로 타입별 필수 필드를 고정한다.

- 공통 필드: `type`, `trace_id`, `seq`
- `token` 이벤트
  - 필수: `content`(토큰 문자열)
  - 선택: `node`
- `metadata` 이벤트
  - 필수: `content`(JSON 문자열)
  - 선택: `node`, `error_code`, `safeguard_label`
- `error` 이벤트
  - 필수: `content`(에러 메시지), `error_code`
  - 선택: `node`, `safeguard_label`
- `done` 이벤트
  - 필수: `content=null`
  - 선택: `node=null`

추가 규칙:
- `seq`는 `job_id`별로 1부터 단조 증가한다.
- `error`가 발생하면 `error` → `done` 순서로 전송한다.
- SSE 라인은 `data: {json}\n\n` 형식을 고정한다.

### 3) 그래프 구성/라우팅 정책

- `src/secondsession/core/chat/graphs/chat_graph.py`
  - safeguard 라우팅 정책(`SafeguardLabel` 기준) 구현
  - answer 오류 → fallback 라우팅 경로 추가
  - thread_id 기반 복구 흐름 활성화(체크포인터 config)
  - 폴백 응답의 history 기록 여부 정책 확정

### 4) LangGraph 노드 구현

- `src/secondsession/core/chat/nodes/safeguard_node.py`
  - 안전 라벨 분류, PASS 외 라우팅 및 error_code 설정
- `src/secondsession/core/chat/nodes/answer_node.py`
  - 답변 생성, 스키마 검증 실패/타임아웃 처리, error_code 설정
- `src/secondsession/core/chat/nodes/append_history_node.py`
  - 대화 내역 누적(history/turn_count) 및 스키마 검증
- `src/secondsession/core/chat/nodes/decide_summary_node.py`
  - 5턴 초과 요약 분기, error_code 기반 폴백 분기
- `src/secondsession/core/chat/nodes/summary_node.py`
  - 대화 내역 요약 생성
- `src/secondsession/core/chat/nodes/fallback_node.py`
  - error_code/safeguard_label 기반 폴백 메시지 정책 적용

### 5) 병렬 그래프 예제 구현

- `src/secondsession/core/chat/graphs/parallel_chat_graph.py`
  - 팬아웃/팬인 구조 설계(예: 답변 후보 2개 병렬 생성)
  - 합류(배리어/쿼럼) 정책 정의(최소 1개 성공, 2개 실패 시 폴백)
  - 부분 실패 허용 기준 및 에러 코드 전파 규칙 확정
  - 합류 노드에서 최종 결과 선택 기준(점수/길이/정합성)을 정의

### 6) 상태/스키마/프롬프트 규약 정리

- `src/secondsession/core/chat/state/chat_state.py`
  - history 스키마, 최근 N턴 유지 정책, 폴백 연결 규칙
- `src/secondsession/core/chat/const/chat_history_item.py`
  - role 제한, content 길이 정책
- `src/secondsession/core/chat/const/error_code.py`
  - 도메인별 에러 코드 추가 및 공통 매핑 규칙
- `src/secondsession/core/chat/const/safeguard_label.py`
  - 라벨별 차단/완화/리다이렉트 정책 문서화
- `src/secondsession/api/chat/const/stream_event_type.py`
  - 타입별 필수 필드 정의
- `src/secondsession/api/chat/model/chat_stream_event.py`
  - 이벤트 스키마 규약 확정
- `src/secondsession/api/chat/model/chat_stream_metadata.py`
  - 메타데이터 payload JSON 스키마 고정
- `src/secondsession/core/chat/prompts/answer_prompt.py`
  - 서비스 톤/정책 반영
- `src/secondsession/core/chat/prompts/summary_prompt.py`
  - 요약 길이/규칙 보강

### 7) 체크포인터 연결

- `src/secondsession/core/common/checkpointer/redis_checkpointer.py`
  - Redis 체크포인터 생성 로직 구현
  - metadata(node/route/error_code/safeguard_label) 저장 규칙 정의
- `src/secondsession/core/common/checkpointer/redis_async_checkpointer.py`
  - 비동기 체크포인터 사용 시 연결/저장 규칙 점검
- `src/secondsession/core/common/checkpointer/inmemory_checkpointer.py`
  - 인메모리 체크포인터 구현(버전/정리 정책 포함)

### 8) 선택 과제: 테스트 코드 작성

- `pytest` 기반으로 핵심 흐름 테스트 작성
- **모킹 없이** 실제 로직 검증

---

## 목표 플로우

1) `POST /chat/jobs`로 job_id/trace_id 발급  
2) 워커가 큐에서 작업을 꺼내 LangGraph 실행  
3) token/metadata/error/done 이벤트를 Redis에 적재  
4) `GET /chat/stream/{job_id}`에서 SSE로 이벤트 전송  
5) 5턴 초과 시 요약 경로로 분기  
6) thread_id로 대화 내역 복구  

---

## 실행 방법

### 1) uvicorn CLI 방식 (권장)

```bash
uv run uvicorn secondsession.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2) 모듈 직접 실행 방식

```bash
uv run python -m secondsession.main
```

---

## 기본 엔드포인트

- 헬스 체크: `GET /health`
- 대화 작업 생성: `POST /chat/jobs`
- 대화 스트리밍: `GET /chat/stream/{job_id}`
- 대화 상태 조회: `GET /chat/status/{job_id}`
- 대화 취소: `POST /chat/cancel/{job_id}`

---

## 주요 위치

- 애플리케이션 진입점: `src/secondsession/main.py`
- API 영역: `src/secondsession/api`
- Core 영역: `src/secondsession/core`
- 문서: `docs/`

---

## 환경 설정

프로젝트 루트에서 아래 순서로 실행하세요.

```bash
uv venv .venv
uv sync
```
