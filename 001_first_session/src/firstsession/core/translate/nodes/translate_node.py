# 목적: 번역을 수행하는 노드를 정의한다.
# 설명: 프롬프트 생성과 모델 호출을 포함할 수 있다.
# 디자인 패턴: 전략 패턴 + 파이프라인 노드
# 참조: docs/04_string_tricks/05_retry_logic.md

"""번역 수행 노드 모듈."""

from firstsession.core.translate.state.translation_state import TranslationState
from firstsession.core.translate.prompts.translation_prompt import TRANSLATION_PROMPT
from firstsession.core.translate.nodes.call_model_node import CallModelNode

class TranslateNode:
    """번역 수행을 담당하는 노드."""
    def __init__(self) -> None:
        self.call_model_node = CallModelNode()

    def run(self, state: TranslationState) -> TranslationState:
        """번역 결과를 생성한다.

        Args:
            state: 현재 번역 상태.

        Returns:
            TranslationState: 번역 결과가 포함된 상태.
        """
        # TODO: 번역 프롬프트를 구성하고 모델/외부 API를 호출한다.
        # TODO: 번역 결과를 상태에 기록하는 규칙을 정의한다.
        source_language = state.get("source_language", "")
        target_language = state.get("target_language", "")
        normalized_text = state.get("normalized_text", "")

        if not source_language or not target_language:
            state["error"] = "번역작업을 위한 언어가 설정되어있지 않습니다."
            state["translated_text"] = ""
            return state

        if not normalized_text:
            state["error"] = "번역작업을 수행 할 텍스트가 비어 있습니다."
            state["translated_text"] = ""
            return state
        
        prompt = TRANSLATION_PROMPT.format(
            source_language = str(source_language),
            target_language = str(target_language),
            text = str(normalized_text)
        )

        state["prompt"] = prompt
        state = self.call_model_node.run(state)
        output = state.get("model_output", "")
        if output is None:
            state["error"] = "번역 모델 응답이 비어있습니다."
            state["translated_text"] = ""
            return state

        translated_text = str(output).strip()
        if not translated_text:
            state["error"] = "번역 결과가 비어있습니다."
            state["translated_text"] = ""
            return state

        state["translated_text"] = translated_text
        state.pop("error", None)
        return state