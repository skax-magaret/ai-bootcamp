from workflow.agents.doctor_agent import DoctorAgent
from workflow.agents.patient_agent import PatientAgent
from workflow.agents.coordinator_agent import CoordinatorAgent
from workflow.state import ConsultationState, AgentType
from langgraph.graph import StateGraph, END


class TurnManager:
    """대화 턴 관리자"""
    
    def run(self, state: ConsultationState) -> ConsultationState:
        new_state = state.copy()
        new_state["current_turn"] = new_state.get("current_turn", 0) + 1
        return new_state


def create_consultation_graph(enable_rag: bool = True, session_id: str = ""):
    """척추 유합술 상담 그래프 생성"""
    
    # 그래프 생성
    workflow = StateGraph(ConsultationState)
    
    # 에이전트 인스턴스 생성 - enable_rag에 따라 검색 문서 수 결정
    k_value = 2 if enable_rag else 0
    doctor_agent = DoctorAgent(k=k_value, session_id=session_id)
    patient_agent = PatientAgent(k=k_value, session_id=session_id)
    coordinator_agent = CoordinatorAgent(k=1, session_id=session_id)
    turn_manager = TurnManager()
    
    # 노드 추가
    workflow.add_node(AgentType.DOCTOR, doctor_agent.run)
    workflow.add_node(AgentType.PATIENT, patient_agent.run)
    workflow.add_node(AgentType.COORDINATOR, coordinator_agent.run)
    workflow.add_node("INCREMENT_TURN", turn_manager.run)
    
    # 엣지 설정
    workflow.add_edge(AgentType.DOCTOR, AgentType.PATIENT)  # 의사 → 환자
    workflow.add_edge(AgentType.PATIENT, "INCREMENT_TURN")  # 환자 → 턴 증가
    
    # 조건부 엣지 설정 - 상담 종료 여부 판단
    workflow.add_conditional_edges(
        "INCREMENT_TURN",
        lambda s: should_end_consultation(s),
        {
            True: AgentType.COORDINATOR,   # 상담 종료 → 조정자
            False: AgentType.DOCTOR        # 상담 계속 → 의사
        }
    )
    
    # 시작점과 종료점 설정
    workflow.set_entry_point(AgentType.DOCTOR)
    workflow.add_edge(AgentType.COORDINATOR, END)
    
    # 그래프 컴파일
    return workflow.compile()


def should_end_consultation(state: ConsultationState) -> bool:
    """상담 종료 여부 판단"""
    
    current_turn = state.get("current_turn", 0)
    max_turns = state.get("max_turns", 6)
    messages = state.get("messages", [])
    
    # 최대 턴 수 도달
    if current_turn >= max_turns:
        return True
    
    # 환자의 만족도나 상담 완료 신호 확인
    if messages:
        last_message = messages[-1]
        if last_message.get("role") == AgentType.PATIENT:
            content = last_message.get("content", "").lower()
            
            # 상담 완료를 나타내는 키워드들
            completion_keywords = [
                "감사합니다", "도움이 되었습니다", "안심이 됩니다", 
                "이해했습니다", "충분히 알겠습니다", "더 이상 질문 없습니다"
            ]
            
            if any(keyword in content for keyword in completion_keywords):
                return True
    
    return False


def initialize_consultation_state(
    patient_query: str,
    patient_info: dict = None,
    consultation_type: str = "일반",
    max_turns: int = 6
) -> ConsultationState:
    """상담 상태 초기화"""
    
    if patient_info is None:
        patient_info = {
            "age": "50",
            "occupation": "사무직",
            "family": "배우자와 자녀 2명",
            "post_surgery_period": "수술 예정",
            "symptoms": "허리 통증"
        }
    
    return ConsultationState(
        patient_query=patient_query,
        patient_info=patient_info,
        messages=[],
        current_turn=0,
        consultation_type=consultation_type,
        max_turns=max_turns,
        docs={},
        contexts={},
        is_completed=False,
        summary=""
    )


if __name__ == "__main__":
    # 테스트용 그래프 생성 및 시각화
    graph = create_consultation_graph(True)
    
    try:
        graph_image = graph.get_graph().draw_mermaid_png()
        
        output_path = "consultation_graph.png"
        with open(output_path, "wb") as f:
            f.write(graph_image)
        
        print(f"상담 그래프가 {output_path}에 저장되었습니다.")
        
    except Exception as e:
        print(f"그래프 시각화 중 오류 발생: {str(e)}") 