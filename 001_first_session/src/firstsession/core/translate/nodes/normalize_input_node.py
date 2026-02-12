# 목적: 번역 입력을 정규화하는 노드를 정의한다.
# 설명: 언어 코드와 텍스트를 기본 규칙으로 정리한다.
# 디자인 패턴: 파이프라인 노드
# 참조: firstsession/core/translate/graphs/translate_graph.py

"""입력 정규화 노드 모듈."""

from firstsession.core.translate.state.translation_state import TranslationState
import re

class NormalizeInputNode:
    """입력 정규화를 담당하는 노드."""
    def __init__(self) -> None:
        self = self

    def _normalize_lang(self, lang: str) -> str:
        """언어 코드 표준화"""
        if not lang:
            return ""

        lang = lang.strip().lower()

        if "-" in lang:
            lang = lang.split("-")[0]

        return lang

    def _normalize_text(self, text: str) -> str:
        """공백 및 줄바꿈 정리"""
        if not text:
            return ""
        
        text = text.strip()
        text = re.sub(r"\n{2,}", "\n", text) # 줄바꿈 정리
        text = re.sub(r"\s+", " ", text) # 공백 정리
    
        return text

    def _limit_length(self, max_input_length: int, text: str) -> str:
        if len(text) <= max_input_length:
            return text
        return text[:max_input_length]

    def run(self, max_input_length: int, state: TranslationState) -> TranslationState:
        """입력 데이터를 정규화한다.

        Args:
            state: 현재 번역 상태.

        Returns:
            TranslationState: 정규화된 상태.
        """
        # TODO: 언어 코드 표준화, 공백 정리, 길이 제한 규칙을 구현한다.
        # TODO: 금칙어/민감 정보 처리 기준을 정의한다.
        # 언어 코드 표준화
        state["source_language"] = self._normalize_lang(state.get("source_language", ""))
        state["target_language"] = self._normalize_lang(state.get("target_language", ""))
        # 입력 text 표준화
        raw_text = state.get("text", "")
        normalized_text = self._normalize_text(raw_text)
        # 입력 text 길이 제한
        max_input_length = int(state['max_input_length'])
        normalized_text = self._limit_length(max_input_length=max_input_length, text=normalized_text)

        state["normalized_text"] = normalized_text
        return state
