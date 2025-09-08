from workflow.agents.agent import Agent
from workflow.state import AgentType
from typing import Dict, Any


class DoctorAgent(Agent):
    """척추 유합술 전문의 AI 에이전트"""

    def __init__(self, k: int = 2, session_id: str = None):
        super().__init__(
            system_prompt=self._get_system_prompt(),
            role=AgentType.DOCTOR,
            k=k,
            session_id=session_id,
        )

    def _get_system_prompt(self) -> str:
        return """
당신은 척추 유합술 전문의입니다. 환자의 질문에 대해 의학적으로 정확하고 이해하기 쉽게 답변해주세요.

## 역할 및 책임:
1. 척추 유합술에 대한 전문적인 의학 지식 제공
2. 환자의 불안감 해소 및 정확한 정보 전달
3. 수술 전후 관리 지침 제공
4. 개별 환자 상황에 맞는 맞춤형 조언

## 답변 원칙:
- 의학적으로 정확한 정보만 제공
- 전문 용어는 쉽게 풀어서 설명
- 환자의 감정에 공감하며 안심시키기
- 구체적이고 실용적인 조언 제공
- 응급상황 시 즉시 병원 방문 권유

## 답변 구조:
1. 환자 질문에 대한 공감과 이해
2. 의학적 설명 (Chain-of-Thought 방식)
3. 구체적인 조치 방법
4. 추가 주의사항 및 격려
"""

    def _create_prompt(self, state: Dict[str, Any]) -> str:
        """환자 상황에 맞는 맞춤형 프롬프트 생성"""
        
        patient_query = state.get("patient_query", "")
        patient_info = state.get("patient_info", {})
        consultation_type = state.get("consultation_type", "일반")
        context = state.get("context", "")
        
        # Few-shot 예시 생성
        few_shot_examples = self._get_few_shot_examples(consultation_type)
        
        return f"""
환자 정보:
- 나이: {patient_info.get('age', '정보 없음')}
- 수술 후 기간: {patient_info.get('post_surgery_period', '정보 없음')}
- 주요 증상: {patient_info.get('symptoms', '정보 없음')}
- 상담 유형: {consultation_type}

관련 의학 정보:
{context}

{few_shot_examples}

환자 질문: "{patient_query}"

위의 정보를 바탕으로 다음 단계에 따라 답변해주세요:

1. **환자 상황 분석**: 환자의 질문과 상태를 의학적으로 분석
2. **의학적 설명**: 관련 의학 지식을 환자가 이해하기 쉽게 설명
3. **구체적 조치**: 환자가 실행할 수 있는 구체적인 방법 제시
4. **주의사항**: 중요한 주의사항과 응급상황 대처법
5. **격려 메시지**: 환자를 안심시키고 격려하는 메시지

답변은 300자 이내로 작성하되, 의학적 정확성을 유지하면서 따뜻하고 이해하기 쉽게 작성해주세요.
"""

    def _get_few_shot_examples(self, consultation_type: str) -> str:
        """상담 유형별 Few-shot 예시 제공"""
        
        examples = {
            "수술_전": """
예시 1:
환자: "수술이 무서워요. 정말 안전한가요?"
의사: "수술에 대한 두려움은 자연스러운 감정입니다. 척추 유합술은 현재 매우 안전하고 성공률이 높은 수술입니다. 우리 병원의 성공률은 95% 이상이며, 수술 전 철저한 검사를 통해 위험을 최소화합니다. 수술 과정을 자세히 설명드리겠습니다..."
""",
            "수술_후": """
예시 1:
환자: "수술 후 3주인데 아직도 아파요. 정상인가요?"
의사: "수술 후 3주 차에 통증이 있는 것은 정상적인 회복 과정입니다. 뼈가 유합되는 데는 3-6개월이 걸리므로, 현재는 회복 초기 단계입니다. 통증이 점진적으로 감소하고 있다면 순조로운 회복 중입니다. 처방된 진통제를 규칙적으로 복용하시고..."
""",
            "재활": """
예시 1:
환자: "언제부터 운동을 시작해도 될까요?"
의사: "수술 후 시기에 따라 단계별로 운동을 시작해야 합니다. 현재 수술 후 6주차라면 가벼운 걷기와 스트레칭부터 시작하세요. 허리를 굽히거나 비트는 동작은 아직 피해야 합니다. 물리치료사와 함께 체계적인 운동 계획을 세우는 것이 좋습니다..."
"""
        }
        
        return examples.get(consultation_type, examples["수술_후"]) 