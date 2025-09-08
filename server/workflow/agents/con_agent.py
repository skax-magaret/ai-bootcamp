from workflow.agents.agent import Agent
from workflow.state import AgentType
from typing import Dict, Any


class EmotionalAgent(Agent):

    def __init__(self, k: int = 2, session_id: str = None):
        super().__init__(
            system_prompt="당신은 고객의 낭만과 로망을 존중하는 감성적인 부동산 전문가입니다. 비현실적이지 않은 범위 내에서 고객이 원하는 가치를 실현하도록 돕습니다. 고객의 감정적인 만족도와 삶의 질을 중시하며, 무언가를 얻기 위해 다른 부분을 희생할 수도 있음을 부드럽게 설득합니다.",
            role=AgentType.EMOTIONAL,
            k=k,
            session_id=session_id,
        )

    def _create_prompt(self, state: Dict[str, Any]) -> str:

        if state["current_round"] == 1:
            return self._create_first_round_prompt(state)
        else:
            return self._create_rebuttal_prompt(state)

    def _create_first_round_prompt(self, state: Dict[str, Any]) -> str:

        # 이성적 조언자의 마지막 메시지를 가져옴
        previous_messages = [m for m in state["messages"] if m["role"] == AgentType.RATIONAL]
        last_rational_message = previous_messages[-1]["content"] if previous_messages else ""

        return f"""
            당신은 감성적이고 로맨틱한 부동산 조언자입니다.
            
            고객의 요구사항:
            - 예산: {state.get('budget', '')}
            - 매물 유형: {state.get('property_type', '')}
            - 선호 조건1: {state.get('preference1', '')}
            - 선호 조건2: {state.get('preference2', '')}
            
            다음은 관련 부동산 정보입니다:
                {state.get("context", "")}
            
            이성적 조언자의 다음 의견에 대해 감성적인 관점에서 반박하고, 고객의 로망과 감정적 만족도를 중시하는 조언을 제시해주세요:
            이성적 조언자 의견: "{last_rational_message}"
            
            고객의 감정적인 만족도와 삶의 질을 중시하며, 무언가를 얻기 위해 다른 부분을 희생할 수도 있음을 부드럽게 설득하세요.
            2 ~ 3문단, 각 문단은 100자내로 작성해주세요.
            """

    def _create_rebuttal_prompt(self, state: Dict[str, Any]) -> str:

        # 이성적 조언자의 마지막 메시지를 가져옴
        rational_messages = [m for m in state["messages"] if m["role"] == AgentType.RATIONAL]
        last_rational_message = rational_messages[-1]["content"] if rational_messages else ""

        return f"""
            당신은 감성적이고 로맨틱한 부동산 조언자입니다.
            
            고객의 요구사항:
            - 예산: {state.get('budget', '')}
            - 매물 유형: {state.get('property_type', '')}
            - 선호 조건1: {state.get('preference1', '')}
            - 선호 조건2: {state.get('preference2', '')}
            
            다음은 관련 부동산 정보입니다:
                {state.get("context", "")}
            
            이성적 조언자의 최근 의견에 대해 감성적인 관점에서 반박하고, 고객의 로망과 감정적 만족도를 더 강화해주세요:
            이성적 조언자 의견: "{last_rational_message}"
            
            고객의 감정적인 만족도와 삶의 질을 중시하며, 무언가를 얻기 위해 다른 부분을 희생할 수도 있음을 부드럽게 설득하세요.
            2 ~ 3문단, 각 문단은 100자내로 작성해주세요.
            """
