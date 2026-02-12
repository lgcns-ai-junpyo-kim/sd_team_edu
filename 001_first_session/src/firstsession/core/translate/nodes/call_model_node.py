# 목적: 번역 모델 호출 노드를 정의한다.
# 설명: 실제 LLM/외부 번역 API 호출을 이 위치에서 수행한다.
# 디자인 패턴: 파이프라인 노드
# 참조: firstsession/core/translate/graphs/translate_graph.py

"""모델 호출 노드 모듈."""

from __future__ import annotations
from dataclasses import dataclass
from firstsession.core.translate.state.translation_state import TranslationState
import google.generativeai as genai

@dataclass(frozen=True)
class CallModelConfig:
    """모델 설정 담당"""
    model_name: str = "gemini-3-pro-preview"
    temperature: float = 0.2
    timeout: int = 10

class CallModelNode:
    """모델 호출을 담당하는 노드."""
    def __init__(self, config: CallModelConfig, api_key: str) -> None:
        self.config = config
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.config.model_name)

    def _call_model(self, text: str) -> str:
        response = self.model.generate_content(
            text,
            generation_config={
                "temperature": self.config.temperature,
            },
        )

        return response.text
    
    def run(self, state: TranslationState) -> TranslationState:
        """프롬프트를 기반으로 번역 결과를 생성한다.

        Args:
            state: 현재 번역 상태.

        Returns:
            TranslationState: 번역 결과가 포함된 상태.
        """
        # TODO: 모델 호출 인터페이스와 에러 처리 규칙을 구현한다.
        # TODO: 응답 텍스트 파싱 및 정규화 규칙을 정의한다.
        text = state.get("normalized_text").strip() or state.get("text").strip() or ""
        
        if not text:
            state["error"] = "번역할 텍스트가 비어 있습니다."
            state["translated_text"] = ""
            return state
    
        try:
            translated_text = self._call_model(
                text=text,
                model_name=self.config.model_name,
                temperature=self.config.temperature,
                timeout=self.config.timeout,
            )

            state["translated_text"] = translated_text.strip()
            return state

        except Exception as e:
            state["error"] = f"모델 호출 실패: {e}"
            state["translated_text"] = ""
            return state

