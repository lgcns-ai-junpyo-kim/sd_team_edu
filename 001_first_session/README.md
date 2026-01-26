# firstsession

이 프로젝트는 LangChain/LangGraph 입문자를 대상으로 한 **실전형 교육 코스**입니다.
"LLM은 텍스트를 반환하는 도구"라는 관점을 중심으로, 프롬프트 설계부터 그래프 기반 처리까지 단계적으로 학습합니다.

## 교육 방향성

- **한 작업-한 프롬프트** 원칙을 기반으로 설계를 분리한다.
- LLM 출력은 **파싱 → 검증 → 정규화**로 안정화한다.
- LangGraph를 사용해 **태스크 분리와 흐름 제어**를 구현한다.
- 실패 응답은 **재시도 전략**으로 복구한다.

## 학습 콘텐츠

- 교재 문서: `docs/`
- 코드 템플릿: `src/firstsession/`
- 번역 API 엔드포인트: `/api/v1/translate`

## 작성해야 하는 과제

1. **그래프 노드 구현**
   - `core/translate/nodes`의 모든 `NotImplementedError` 메서드 구현
   - PASS/차단 분기, QC, 재번역 흐름을 완성

2. **프롬프트 적용**
   - `core/translate/prompts`의 템플릿을 실제 호출 로직에 연결
   - 출력 형식 검증 및 오류 처리 규칙 설계

3. **API 연결**
   - `api/translate`에서 그래프 실행 결과를 응답 스키마로 반환
   - 차단 메시지와 성공 응답을 구분하여 구성

4. **테스트 코드 작성(선택)**
   - `pytest` 기반으로 핵심 흐름 테스트 작성
   - **모킹 없이** 실제 로직을 검증하는 테스트 설계

## 실행 방법

```bash
uv run uvicorn firstsession.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 기본 엔드포인트

- 헬스 체크: `GET /health`
- 번역 요청: `POST /api/v1/translate`

## 주요 위치

- 애플리케이션 진입점: `src/firstsession/api/main.py`
- API 영역: `src/firstsession/api`
- Core 영역: `src/firstsession/core`

## 환경 설정

프로젝트 루트에서 아래 순서로 실행하세요.

```txt
uv venv .venv
uv sync
```
