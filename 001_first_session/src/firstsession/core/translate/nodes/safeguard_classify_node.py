# 목적: 입력 문장을 안전 분류로 라우팅한다.
# 설명: PASS/PII/HARMFUL/PROMPT_INJECTION 라벨로 안전 여부를 판정한다.
# 디자인 패턴: 전략 패턴 + 파이프라인 노드
# 참조: docs/04_string_tricks/02_single_choice_파서.md

"""안전 분류 노드 모듈."""

from firstsession.core.translate.state.translation_state import TranslationState
from enum import Enum
from dataclasses import dataclass
import re

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
        cleaned = raw_text.strip()
        if not cleaned:
            return SafeguardRoute.UNKNOWN, SafeguardError.EMPTY_OUTPUT
        letter = cleaned.upper()[:1]
        mapping = {
            "A": SafeguardRoute.SAFE,
            "B": SafeguardRoute.PII,
            "C": SafeguardRoute.HARMFUL,
            "D": SafeguardRoute.PROMPT_INJECTION,
        }
        if letter not in mapping:
            return SafeguardRoute.UNKNOWN, SafeguardError.INVALID_LABEL
        return mapping[letter], SafeguardError.NONE

class SafeguardClassifyNode:
    """안전 분류를 담당하는 노드."""
    def __init__(self) -> None:
        self.router = SafeguardRouter()
        self.pii_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # 주민번호 형태 예시
            r"\b\d{2,3}-\d{3,4}-\d{4}\b",  # 전화번호
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",  # 이메일
            r"\b\d{10,16}\b",  # 계좌/카드번호 추정
            r"(주소|계좌|주민번호|전화번호|이메일)",
        ]
        self.harmful_patterns = [
            r"(자해|자살|죽고 싶|kill myself)",
            r"(폭탄|총기|칼로 찌르)",
            r"(마약 제조|폭발물 제조)",
            r"(혐오|인종차별|차별해)",
        ]
        self.prompt_injection_patterns = [
            r"(ignore previous instructions)",
            r"(시스템 지침을 무시)",
            r"(규칙을 무시하고)",
            r"(관리자 권한으로)",
            r"(비밀 키를 출력)",
            r"(시스템 프롬프트를 보여줘)",
        ]
    
    def _classification(self, text: str) -> str:
        text = text.lower()

        for pattern in self.pii_patterns:
            if re.search(pattern, text):
                return "B"
        for pattern in self.harmful_patterns:
            if re.search(pattern, text):
                return "C"
        for pattern in self.prompt_injection_patterns:
            if re.search(pattern, text):
                return "D"
        return "A"

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
        raw_output = self._classification(normalized_text)
        label, error = self.router.parse(raw_output)
        
        if error != SafeguardError.NONE:
            state["safeguard_label"] = "UNKNOWN"
            state["safeguard_error"] = error.value
            return state

        state["safeguard_label"] = label.value
        state["safeguard_error"] = SafeguardError.NONE.value
        return state
