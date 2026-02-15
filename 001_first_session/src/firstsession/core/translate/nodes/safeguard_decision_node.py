# 목적: 안전 분류 결과를 바탕으로 진행/차단 결정을 기록한다.
# 설명: PASS 여부를 판단하고 차단 시 오류 메시지를 설정한다.
# 디자인 패턴: 파이프라인 노드
# 참조: firstsession/core/translate/const/safeguard_messages.py

"""안전 분류 결정 노드 모듈."""

from firstsession.core.translate.state.translation_state import TranslationState
from enum import Enum

class SafeguardMessage(Enum):
    """안전 분류 파싱 오류 메시지."""

    PII = "개인정보가 포함된 요청으로 차단되었습니다."
    HARMFUL = "유해한 콘텐츠 요청으로 차단되었습니다."
    PROMPT_INJECTION = "프롬프트 인젝션 시도로 차단되었습니다."
    UNKNOWN = "안전 정책에 의해 요청이 차단되었습니다."

class SafeguardDecisionNode:
    """안전 분류 결정을 담당하는 노드."""

    def run(self, state: TranslationState) -> TranslationState:
        """PASS 여부와 오류 메시지를 기록한다.

        Args:
            state: 현재 번역 상태.

        Returns:
            TranslationState: 결정 결과가 포함된 상태.
        """
        # TODO: PASS 여부를 확인하고 error_message를 설정한다.
        # TODO: SafeguardMessage Enum과의 매핑 규칙을 정의한다.
        label = state.get("safeguard_label", "UNKNOWN")

        if label == "SAFE":
            return state
        
        try:
            error_enum = SafeguardMessage[label]
            state["error"] = error_enum.value
        except KeyError:
            # 정의되지 않은 라벨일 경우
            state["error"] = SafeguardMessage.UNKNOWN.value

        return state