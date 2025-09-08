from workflow.agents.agent import Agent
from workflow.state import AgentType
from typing import Dict, Any


class RationalAgent(Agent):

    def __init__(self, k: int = 2, session_id: str = None):
        super().__init__(
            system_prompt="당신은 현실적이고 냉철한 부동산 전문가입니다. 사용자의 출퇴근, 생활 환경, 재정적 리스크를 최우선으로 고려합니다. 통계 데이터나 객관적인 사실을 근거로 조언하며, 무리한 결정은 신중하게 만류합니다. 안전하고 안정적인 선택을 강조합니다.",
            role=AgentType.RATIONAL,
            k=k,
            session_id=session_id,
        )

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        if state["current_round"] == 1:
            return self._create_first_round_prompt(state)
        else:
            return self._create_rebuttal_prompt(state)

    def _create_first_round_prompt(self, state: Dict[str, Any]) -> str:
        return f"""
            당신은 이성적이고 현실적인 부동산 조언자입니다.
            
            고객의 요구사항:
            - 예산: {state.get('budget', '')}
            - 매물 유형: {state.get('property_type', '')}
            - 선호 조건1: {state.get('preference1', '')}
            - 선호 조건2: {state.get('preference2', '')}
            
            다음은 관련 부동산 정보입니다:
                {state.get("context", "")}
            
            현실적이고 냉철한 관점에서 고객의 요구사항을 분석하고 조언해주세요.
            출퇴근 편의성, 생활 환경, 재정적 리스크를 중점적으로 고려하여 안전하고 안정적인 선택을 강조하세요.
            통계 데이터나 객관적인 사실을 근거로 제시하세요.
            2 ~ 3문단, 각 문단은 100자내로 작성해주세요.
            """

    def _create_rebuttal_prompt(self, state: Dict[str, Any]) -> str:
        # 감성적 조언자의 마지막 메시지를 가져옴
        previous_messages = [m for m in state["messages"] if m["role"] == AgentType.EMOTIONAL]
        last_emotional_message = previous_messages[-1]["content"] if previous_messages else ""

        return f"""
            당신은 이성적이고 현실적인 부동산 조언자입니다.
            
            고객의 요구사항:
            - 예산: {state.get('budget', '')}
            - 매물 유형: {state.get('property_type', '')}
            - 선호 조건1: {state.get('preference1', '')}
            - 선호 조건2: {state.get('preference2', '')}
            
            다음은 관련 부동산 정보입니다:
                {state.get("context", "")}
            
            감성적 조언자의 다음 의견에 대해 현실적인 관점에서 반박하고, 이성적인 조언을 강화해주세요:
            감성적 조언자 의견: "{last_emotional_message}"
            
            출퇴근, 생활 환경, 재정적 리스크를 중점적으로 고려하여 안전하고 안정적인 선택의 중요성을 강조하세요.
            2 ~ 3문단, 각 문단은 100자내로 작성해주세요.
            """
