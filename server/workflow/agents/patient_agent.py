from workflow.agents.agent import Agent
from workflow.state import AgentType
from typing import Dict, Any


class PatientAgent(Agent):
    """척추 유합술 환자 AI 에이전트 - 환자의 관점에서 질문하고 우려사항을 표현"""

    def __init__(self, k: int = 2, session_id: str = None):
        super().__init__(
            system_prompt=self._get_system_prompt(),
            role=AgentType.PATIENT,
            k=k,
            session_id=session_id,
        )

    def _get_system_prompt(self) -> str:
        return """
당신은 척추 유합술을 받은 (또는 받을 예정인) 환자입니다. 의사의 설명을 듣고 자연스러운 환자의 반응을 보여주세요.

## 역할 및 특성:
1. 의학 지식이 제한적인 일반인의 관점
2. 수술과 회복에 대한 자연스러운 불안감
3. 실생활과 관련된 구체적인 질문
4. 의사의 설명에 대한 추가 확인 요청

## 반응 원칙:
- 의사의 설명을 이해했음을 표현
- 추가적인 우려사항이나 궁금증 제기
- 일상생활과 관련된 구체적인 질문
- 감정적인 반응 (불안, 안도 등) 자연스럽게 표현
- 가족이나 직장 관련 실질적인 고민

## 질문 패턴:
1. 의사 설명에 대한 이해 확인
2. 개인적 상황에 맞는 구체적 질문
3. 일상생활 복귀에 대한 우려
4. 비용이나 시간과 관련된 현실적 고민
"""

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        """환자 상황과 의사 답변에 따른 자연스러운 반응 생성"""
        
        patient_info = state.get("patient_info", {})
        consultation_type = state.get("consultation_type", "일반")
        messages = state.get("messages", [])
        context = state.get("context", "")
        
        # 의사의 마지막 답변 가져오기
        doctor_messages = [m for m in messages if m["role"] == AgentType.DOCTOR]
        last_doctor_message = doctor_messages[-1]["content"] if doctor_messages else ""
        
        # Few-shot 예시 생성
        few_shot_examples = self._get_few_shot_examples(consultation_type)
        
        return f"""
환자 정보:
- 나이: {patient_info.get('age', '50세')}
- 직업: {patient_info.get('occupation', '사무직')}
- 가족 상황: {patient_info.get('family', '배우자와 자녀 2명')}
- 수술 후 기간: {patient_info.get('post_surgery_period', '수술 예정')}
- 상담 유형: {consultation_type}

{few_shot_examples}

의사의 답변: "{last_doctor_message}"

위의 의사 답변을 듣고 환자로서 자연스러운 반응을 보여주세요:

1. **이해 표현**: 의사의 설명에 대한 이해나 안도감 표현
2. **추가 질문**: 개인적 상황과 관련된 구체적인 질문
3. **우려 사항**: 여전히 걱정되는 부분이나 새로운 궁금증
4. **실생활 고민**: 직장, 가족, 일상생활과 관련된 실질적인 고민

환자의 감정과 걱정을 자연스럽게 표현하되, 200자 이내로 작성해주세요.
의학 전문 용어보다는 일반인이 사용하는 쉬운 표현을 사용하세요.
"""

    def _get_few_shot_examples(self, consultation_type: str) -> str:
        """상담 유형별 환자 반응 예시"""
        
        examples = {
            "수술_전": """
예시 1:
의사: "수술은 매우 안전하며 성공률이 높습니다."
환자: "그렇다면 조금 안심이 되네요. 그런데 수술 후에 회사 일은 언제부터 할 수 있을까요? 저희 회사는 앉아서 하는 업무가 많은데, 괜찮을까요? 그리고 아이들 돌보는 것도 걱정이에요."
""",
            "수술_후": """
예시 1:
의사: "현재 회복이 순조롭게 진행되고 있습니다."
환자: "다행이네요. 그런데 아직도 가끔 다리가 저려서 걱정이에요. 이것도 시간이 지나면 나아질까요? 그리고 물리치료는 얼마나 오래 받아야 하나요?"
""",
            "재활": """
예시 1:
의사: "단계별로 운동을 시작하시면 됩니다."
환자: "네, 알겠습니다. 그런데 집에서 혼자 할 수 있는 간단한 운동도 있을까요? 병원까지 매번 오기가 조금 부담스러워서요. 그리고 운동할 때 주의해야 할 동작들을 좀 더 자세히 알고 싶어요."
"""
        }
        
        return examples.get(consultation_type, examples["수술_후"]) 