# LangGraph 상태 정의 - 부동산 중개 관련 필드 추가
from typing import Dict, List, TypedDict


class AgentType:
    RATIONAL = "RATIONAL_AGENT"  # 이성적 조언자
    EMOTIONAL = "EMOTIONAL_AGENT"  # 감성적 조언자
    MEDIATOR = "MEDIATOR_AGENT"  # 중재자 및 최종 결정자

    @classmethod
    def to_korean(cls, role: str) -> str:
        if role == cls.RATIONAL:
            return "이성적 조언자"
        elif role == cls.EMOTIONAL:
            return "감성적 조언자"
        elif role == cls.MEDIATOR:
            return "중재자"
        else:
            return role


class RealEstateState(TypedDict):
    # 사용자 요구사항
    budget: str  # 예산
    property_type: str  # 매물 유형
    area_range: str  # 평형대
    preference1: str  # 선호 조건1
    preference2: str  # 선호 조건2
    
    # 대화 관련
    messages: List[Dict]
    current_round: int
    prev_node: str
    max_rounds: int
    
    # RAG 관련
    docs: Dict[str, List]  # RAG 검색 결과
    contexts: Dict[str, str]  # RAG 검색 컨텍스트
    
    # 매물 추천 결과
    recommended_properties: List[Dict]
    additional_options: List[str]  # 추가 옵션 조건들
