# 목적: 입력 문장을 안전 분류로 라우팅한다.
# 설명: PASS/PII/HARMFUL/PROMPT_INJECTION 라벨로 안전 여부를 판정한다.
# 디자인 패턴: 전략 패턴 + 파이프라인 노드
# 참조: docs/04_string_tricks/02_single_choice_파서.md

"""안전 분류 노드 모듈."""

import re
from enum import Enum
from dataclasses import dataclass

from firstsession.core.translate.state.translation_state import TranslationState
from firstsession.core.translate.prompts.safeguard_prompt import SAFEGUARD_PROMPT
from firstsession.core.translate.nodes.call_model_node import CallModelNode

class SafeguardRoute(Enum):
    """안전 분류 라우팅 값."""
    SAFE = "SAFE"
    PII = "PII"
    HARMFUL = "HARMFUL"
    PROMPT_INJECTION = "PROMPT_INJECTION"
    UNKNOWN = "UNKNOWN"

class SafeguardError(Enum):
    """안전 분류 파싱 오류 메시지."""
    NONE = "오류 없음"
    EMPTY_OUTPUT = "응답이 비어 있습니다"
    INVALID_LABEL = "허용되지 않은 라벨입니다"


@dataclass(frozen=True)
class SafeguardRouter:
    """단일 선택 라벨을 라우팅 Enum으로 변환한다."""
    def parse(self, raw_text: str) -> tuple[SafeguardRoute, SafeguardError]:
        """원본 텍스트를 라우팅 값과 오류 메시지로 변환한다."""
        text = raw_text.strip()
        if not text:
            return SafeguardRoute.UNKNOWN, SafeguardError.EMPTY_OUTPUT
        text = text.upper()
        mapping = {
            "PASS": SafeguardRoute.SAFE,
            "PII": SafeguardRoute.PII,
            "HARMFUL": SafeguardRoute.HARMFUL,
            "PROMPT_INJECTION": SafeguardRoute.PROMPT_INJECTION,
        }
        if text not in mapping:
            return SafeguardRoute.UNKNOWN, SafeguardError.INVALID_LABEL
        return mapping[text], SafeguardError.NONE

class SafeguardClassifyNode:
    """안전 분류를 담당하는 노드."""
    def __init__(self) -> None:
        self.router = SafeguardRouter()
        self.call_model_node = CallModelNode()

    def run(self, state: TranslationState) -> TranslationState:
        """입력에 대한 안전 라벨을 판정한다.

        Args:
            state: 현재 번역 상태.

        Returns:
            TranslationState: 안전 라벨이 포함된 상태.
        """
        # TODO: 안전 분류 프롬프트를 호출하고 PASS/PII/HARMFUL/PROMPT_INJECTION을 산출한다.
        # TODO: 출력 검증 및 정규화 규칙을 정의한다.
        normalized_text = state.get("normalized_text", "")
        if not normalized_text:
            state['safeguard_label'] = SafeguardRoute.UNKNOWN.value
            state['safeguard_error'] = "입력 텍스트가 비어있습니다."
            return state
        
        prompt = SAFEGUARD_PROMPT.format(user_input=str(normalized_text))
        output = self.call_model_node(prompt)
        label, error = self.router.parse(output)
        
        if error != SafeguardError.NONE:
            state["safeguard_label"] = SafeguardRoute.UNKNOWN.value
            state["safeguard_error"] = error.value
            return state

        state["safeguard_label"] = label.value
        state["safeguard_error"] = SafeguardError.NONE.value
        return state
