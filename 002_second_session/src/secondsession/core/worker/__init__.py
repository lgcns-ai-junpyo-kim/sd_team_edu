# 목적: 워커 모듈을 외부에 노출한다.
# 설명: 대화 워커 클래스를 집계한다.
# 디자인 패턴: 파사드
# 참조: secondsession/core/worker/chat_worker.py

"""워커 패키지."""

from secondsession.core.worker.chat_worker import ChatWorker

__all__ = ["ChatWorker"]
