# 목적: 번역 품질을 검사하는 노드를 정의한다.
# 설명: 원문과 번역문을 비교해 YES/NO로 통과 여부를 판단한다.
# 디자인 패턴: 전략 패턴 + 파이프라인 노드
# 참조: docs/04_string_tricks/01_yes_no_파서.md

"""번역 품질 검사 노드 모듈."""
import re
from enum import Enum

from firstsession.core.translate.state.translation_state import TranslationState
from firstsession.core.translate.prompts.quality_check_prompt import QUALITY_CHECK_PROMPT
from firstsession.core.translate.nodes.call_model_node import CallModelNode

class YesNoRoute(Enum):
    """Yes/No 라우팅 값"""
    YES = "YES"
    NO = "NO"
    UNKNOWN = "UNKNOWN"

class QualityCheckNode:
    """번역 품질 검사를 담당하는 노드."""
    def __init__(self) -> None:
        self.call_model_node = CallModelNode()

    def _parse_yes_no(self, raw_text: str) -> YesNoRoute:
        if raw_text is None:
            return YesNoRoute.UNKNOWN
        text = str(raw_text).strip().upper()
        if text == "YES":
            return YesNoRoute.YES
        if text == "NO":
            return YesNoRoute.NO
        first = re.split(r"\s+", text)[0] if text else ""
        if first.startswith("YES"):
            return YesNoRoute.YES
        if first.startswith("NO"):
            return YesNoRoute.NO
        return YesNoRoute.UNKNOWN

    def run(self, state: TranslationState) -> TranslationState:
        """번역 품질을 검사한다.

        Args:
            state: 현재 번역 상태.

        Returns:
            TranslationState: 품질 검사 결과가 포함된 상태.
        """
        # TODO: 품질 검사 프롬프트로 YES/NO를 판정한다.
        # TODO: 결과를 qc_passed 필드에 기록하는 규칙을 정의한다.
        normalized_text = state.get("normalized_text", "")
        translated_text = state.get("translated_text","")
        if not normalized_text or not translated_text:
            state["error"] = "품질 검사를 할 텍스트가 비어 있습니다."
            state["qc_passed"] = "NO"
            return state

        prompt = QUALITY_CHECK_PROMPT.format(source_text=str(normalized_text), translated_text=str(translated_text))
        output = self.call_model_node(prompt)
        route = self._parse_yes_no(output)
        if route == YesNoRoute.YES:
            state["qc_passed"] = "YES"
        elif route == YesNoRoute.NO:
            state["error"] = "품질 검사를 통과하지 못했습니다."
            state["qc_passed"] = "NO"
        else:
            state["error"] = "품질 검사 결과를 확인할 수 없습니다."
            state["qc_passed"] = "NO"
        return state
