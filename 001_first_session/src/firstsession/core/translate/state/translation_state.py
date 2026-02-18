# 목적: 번역 그래프에서 사용하는 상태 구조를 정의한다.
# 설명: 노드 간 전달할 필드를 명확히 관리한다.
# 디자인 패턴: 상태 패턴(State) 데이터 구조
# 참조: firstsession/core/translate/graphs/translate_graph.py

"""번역 그래프 상태 모듈."""

from typing import TypedDict


class TranslationState(TypedDict):
    """번역 처리에 필요한 상태 데이터."""

    # 언어설정
    source_language: str
    target_language: str
    # 입력
    text: str
    normalized_text: str
    translated_text: str
    prompt: str
    # 분기 처리
    safeguard_label: str
    safeguard_error: str
    qc_passed: str
    can_retry: bool
    retry_count: int
    # 설정
    max_input_length: int
    max_retry_count: int
    error: str
