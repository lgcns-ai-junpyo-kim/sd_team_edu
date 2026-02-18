# 목적: 번역 품질을 검사하는 노드를 정의한다.
# 설명: 원문과 번역문을 비교해 YES/NO로 통과 여부를 판단한다.
# 디자인 패턴: 전략 패턴 + 파이프라인 노드
# 참조: docs/04_string_tricks/01_yes_no_파서.md

"""번역 품질 검사 노드 모듈."""

from firstsession.core.translate.state.translation_state import TranslationState
import re

class QualityCheckNode:
    """번역 품질 검사를 담당하는 노드."""
    def __init__(self) -> None:
        self.prompt_patterns = [
            r"translation:",
            r"output:",
            r"result:"
        ]
        self.number_patterns = [
            r"\b\d+(?:\.\d+)?%?\b", # 숫자 패턴
            r"https?://[^\s]+", # URL 패턴
        ]

    def _check_prompt_patterns(self, translated: str) -> bool:
        """번역 결과에 시스템 프롬프트가 포함되는지 탐지"""
        translated = translated.lower()
        for pattern in self.prompt_patterns:
            if re.search(pattern, translated):
                return False
        return True

    def _check_number_patterns(self, source: str, translated: str) -> bool:
        """원문과 번역문의 숫자 정보 일치 여부 탐지"""
        for pattern in self.number_patterns:
            src_tokens = re.findall(pattern, source)
            tgt_tokens = re.findall(pattern, translated)
            # 숫자 데이터 총 수 일치 여부
            if len(src_tokens) != len(tgt_tokens):
                return False
            # 값 일치 여부
            if sorted(src_tokens) != sorted(tgt_tokens):
                return False
        return True        

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
        if normalized_text is None or translated_text is None:
            state["error"] = "품질 검사를 할 텍스트가 비어 있습니다."
            state["qc_passed"] = "NO"
            return state

        if self._check_prompt_patterns(translated_text) is False:
            state["error"] = "번역 결과에 프롬프트가 포함되어 있습니다."
            state["qc_passed"] = "NO"
            return state

        if self._check_number_patterns(normalized_text, translated_text) is False:
            state["error"] = "변역 결과에 누락된 숫자 데이터가 포함되어 있습니다."
            state["qc_passed"] = "NO"
            return state
        
        state["qc_passed"] = "YES"
        return state
