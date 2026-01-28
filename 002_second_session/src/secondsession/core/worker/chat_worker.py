# 목적: 대화 워커 실행 흐름을 정의한다.
# 설명: 큐 소비 → 그래프 실행 → 스트리밍 이벤트 적재를 담당한다.
# 디자인 패턴: Worker, Producer-Consumer
# 참조: docs/02_backend_service_layer/05_비동기_엔드포인트_분리_전략.md

"""대화 워커 모듈."""

from __future__ import annotations

import time
from typing import Any

from secondsession.core.chat.graphs import build_chat_graph
from secondsession.core.common.queue import ChatJobQueue, ChatStreamEventQueue


class ChatWorker:
    """대화 워커."""

    def __init__(
        self,
        job_queue: ChatJobQueue,
        event_queue: ChatStreamEventQueue,
        checkpointer: Any,
        poll_interval: float = 0.1,
    ) -> None:
        """워커를 초기화한다.

        Args:
            job_queue: 대화 작업 큐.
            event_queue: 스트리밍 이벤트 큐.
            checkpointer: LangGraph 체크포인터.
            poll_interval: 큐 폴링 간격(초).
        """
        self._job_queue = job_queue
        self._event_queue = event_queue
        self._checkpointer = checkpointer
        self._poll_interval = poll_interval

    def run_forever(self) -> None:
        """워커를 루프 형태로 실행한다.

        TODO:
            - 큐에서 작업을 가져와 처리한다.
            - 작업이 없으면 poll_interval 만큼 대기한다.
            - 종료/취소 정책을 정의한다(취소 키 확인).
        """
        while True:
            job = self._job_queue.dequeue()
            if job is None:
                time.sleep(self._poll_interval)
                continue
            self._process_job(job)

    def _process_job(self, job: dict) -> None:
        """단일 작업을 처리한다.

        TODO:
            - 그래프를 빌드하고 invoke/stream을 실행한다.
            - config에 thread_id를 넣어 체크포인터 복구를 활성화한다.
            - 실행 중 token/metadata/error 이벤트를 event_queue에 적재한다.
            - 메타데이터 content는 JSON 문자열(예: event, message, route, timestamp)을 사용한다.
            - error 발생 시 error → done 순서로 적재한다.
            - done 이벤트를 반드시 적재하고 종료한다.
        """
        _ = build_chat_graph(self._checkpointer)
        _ = job
        raise NotImplementedError("워커 실행 로직을 구현해야 합니다.")
