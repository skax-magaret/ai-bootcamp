from workflow.agents.agent import Agent
from workflow.state import AgentType
from typing import Dict, Any


class MediatorAgent(Agent):

    def __init__(self, k: int = 2, session_id: str = None):
        super().__init__(
            system_prompt="당신은 두 에이전트의 의견을 종합하고 핵심을 정리하여 가장 합리적인 결론을 내리는 중재자입니다. 앞선 두 에이전트의 대화를 요약하고 장단점을 명확하게 분석합니다. 사용자가 최종 결정을 내릴 수 있도록 객관적이고 균형 잡힌 정보를 제공합니다.",
            role=AgentType.MEDIATOR,
            k=k,
            session_id=session_id,
        )

    def _create_prompt(self, state: Dict[str, Any]) -> str:

        discussion_summary = self._build_discussion_summary(state)

        return f"""
            다음은 부동산 매물 추천에 대한 두 에이전트의 토론입니다. 각 에이전트의 의견을 분석하고 종합적인 조언을 해주세요.
            
            고객의 요구사항:
            - 예산: {state.get('budget', '')}
            - 매물 유형: {state.get('property_type', '')}
            - 선호 조건1: {state.get('preference1', '')}
            - 선호 조건2: {state.get('preference2', '')}
            
            다음은 관련 부동산 정보입니다:
                {state.get("context", "")}
                
            토론 내용:
            {discussion_summary}
            
            위 토론을 분석하여 다음을 포함하는 종합적인 조언을 해주세요:
            1. 두 에이전트 의견의 핵심 요약
            2. 각 의견의 장단점 분석
            3. 고객의 우선순위에 따른 추천 방향
            4. 구체적인 매물 추천 및 추가 옵션 제시
            
            고객이 최종 결정을 내릴 수 있도록 객관적이고 균형 잡힌 정보를 제공하세요.
            최대 500자 이내로 작성해주세요.
            """

    def _build_discussion_summary(self, state: Dict[str, Any]) -> str:

        summary = ""

        # 모든 메시지 순회
        for message in state["messages"]:
            role = message["role"]
            content = message["content"]

            # 역할에 따른 표시 이름
            role_name = (
                AgentType.to_korean(role) if hasattr(AgentType, "to_korean") else role
            )

            # 요약에 메시지 추가
            summary += f"\n\n{role_name}: {content}"

        return summary
