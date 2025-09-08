# LangGraph 상태 정의 - 척추 유합술 상담 시스템
from typing import Dict, List, TypedDict


class AgentType:
    DOCTOR = "DOCTOR_AGENT"
    PATIENT = "PATIENT_AGENT"
    COORDINATOR = "COORDINATOR_AGENT"

    @classmethod
    def to_korean(cls, role: str) -> str:
        if role == cls.DOCTOR:
            return "의사"
        elif role == cls.PATIENT:
            return "환자"
        elif role == cls.COORDINATOR:
            return "상담 조정자"
        else:
            return role


class ConsultationState(TypedDict):
    patient_query: str  # 환자의 질문/상담 내용
    patient_info: Dict  # 환자 정보 (나이, 증상, 수술 후 기간 등)
    messages: List[Dict]  # 대화 내용
    current_turn: int  # 현재 대화 차례
    consultation_type: str  # 상담 유형 (수술 전, 수술 후, 재활 등)
    max_turns: int  # 최대 대화 차례
    docs: Dict[str, List]  # RAG 검색 결과
    contexts: Dict[str, str]  # RAG 검색 컨텍스트
    is_completed: bool  # 상담 완료 여부
    summary: str  # 상담 요약
