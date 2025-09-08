from workflow.agents.agent import Agent
from workflow.state import AgentType
from typing import Dict, Any


class CoordinatorAgent(Agent):
    """상담 조정자 AI 에이전트 - 상담 흐름 관리 및 요약 제공"""

    def __init__(self, k: int = 1, session_id: str = None):
        super().__init__(
            system_prompt=self._get_system_prompt(),
            role=AgentType.COORDINATOR,
            k=k,
            session_id=session_id,
        )

    def _get_system_prompt(self) -> str:
        return """
당신은 척추 유합술 상담을 조정하는 의료진입니다. 의사와 환자 간의 상담을 정리하고 요약하는 역할을 합니다.

## 역할 및 책임:
1. 상담 내용의 핵심 포인트 정리
2. 환자가 받은 조언의 요약 제공
3. 추가로 필요한 상담 영역 식별
4. 다음 상담 또는 진료 일정 안내

## 요약 원칙:
- 의학적 조언의 핵심 내용 정리
- 환자가 실행해야 할 구체적인 행동 목록
- 주의사항 및 응급상황 대처법 강조
- 다음 단계 또는 추가 상담 필요성 안내
"""

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        """상담 내용을 바탕으로 종합적인 요약 생성"""
        
        messages = state.get("messages", [])
        consultation_type = state.get("consultation_type", "일반")
        patient_info = state.get("patient_info", {})
        
        # 대화 내용 정리
        conversation_summary = self._summarize_conversation(messages)
        
        return f"""
상담 정보:
- 환자: {patient_info.get('age', '정보 없음')}세, {patient_info.get('occupation', '정보 없음')}
- 상담 유형: {consultation_type}
- 수술 후 기간: {patient_info.get('post_surgery_period', '정보 없음')}

대화 내용:
{conversation_summary}

위의 상담 내용을 바탕으로 다음과 같이 정리해주세요:

## 📋 상담 요약
### 1. 주요 상담 내용
- 환자의 주요 질문과 우려사항
- 의사의 핵심 조언

### 2. 환자 실행 사항
- 즉시 실행해야 할 조치
- 지속적으로 관리해야 할 사항
- 금지해야 할 행동

### 3. 주의사항
- 응급상황 시 대처법
- 정기 검진 일정
- 추가 상담이 필요한 영역

### 4. 다음 단계
- 예상되는 회복 과정
- 다음 상담 권장 시기
- 추가로 준비해야 할 정보

요약은 환자가 쉽게 이해할 수 있도록 명확하고 구체적으로 작성해주세요.
"""

    def _summarize_conversation(self, messages: list) -> str:
        """대화 내용을 요약하여 반환"""
        
        if not messages:
            return "대화 내용이 없습니다."
        
        summary_parts = []
        for i, message in enumerate(messages, 1):
            role = "의사" if message["role"] == AgentType.DOCTOR else "환자"
            content = message["content"][:100] + "..." if len(message["content"]) > 100 else message["content"]
            summary_parts.append(f"{i}. {role}: {content}")
        
        return "\n".join(summary_parts)

    def should_end_consultation(self, state: Dict[str, Any]) -> bool:
        """상담 종료 여부 판단"""
        
        current_turn = state.get("current_turn", 0)
        max_turns = state.get("max_turns", 6)
        messages = state.get("messages", [])
        
        # 최대 턴 수 도달
        if current_turn >= max_turns:
            return True
        
        # 환자의 마지막 메시지에서 만족도 확인
        patient_messages = [m for m in messages if m["role"] == AgentType.PATIENT]
        if patient_messages:
            last_patient_msg = patient_messages[-1]["content"].lower()
            satisfaction_keywords = ["감사합니다", "도움이 되었습니다", "안심이 됩니다", "이해했습니다"]
            if any(keyword in last_patient_msg for keyword in satisfaction_keywords):
                return True
        
        return False 