# 목적: 번역 모델 호출 노드를 정의한다.
# 설명: 실제 LLM/외부 번역 API 호출을 이 위치에서 수행한다.
# 디자인 패턴: 파이프라인 노드
# 참조: firstsession/core/translate/graphs/translate_graph.py

"""모델 호출 노드 모듈."""

from dataclasses import dataclass
from google import genai
import os

from firstsession.core.translate.state.translation_state import TranslationState

@dataclass(frozen=True)
class CallModelConfig:
    """모델 설정 담당"""
    model_name: str = "gemini-3-flash-preview"
    temperature: float = 0.2
    timeout: int = 10

class CallModelNode:
    """모델 호출을 담당하는 노드."""
    def __init__(self) -> None:
        self.config = CallModelConfig()
        self.client = None

    def _get_client(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API KEY 환경변수가 설정되지 않았습니다.")
        
        if self.client is None:
            self.client = genai.Client(api_key=api_key)
        return self.client

    def _call_model(self, prompt: str) -> str:
        client = self._get_client()
        response = client.models.generate_content(
            model  = self.config.model_name,
            contents = str(prompt),
            config = {
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
        prompt = state.get("prompt")
        if not prompt or not str(prompt).strip():
            state["error"] = "모델에 전달할 텍스트가 비어 있습니다."
            state["model_output"] = ""
            return state
    
        try:
            model_output = self._call_model(str(prompt))
            if not model_output:
                state["error"] = "모델 응답이 비어있습니다."
                state["model_output"] = ""
                return state
            
            state["model_output"] = model_output
            state.pop("error", None)
            return state

        except Exception as e:
            state["error"] = f"모델 호출 실패: {e}"
            state["model_output"] = ""
            return state
