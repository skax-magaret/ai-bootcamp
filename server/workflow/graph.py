from workflow.agents.con_agent import EmotionalAgent
from workflow.agents.judge_agent import MediatorAgent
from workflow.agents.pro_agent import RationalAgent
from workflow.agents.round_manager import RoundManager
from workflow.state import RealEstateState, AgentType
from langgraph.graph import StateGraph, END


def create_real_estate_graph(enable_rag: bool = True, session_id: str = ""):

    # 그래프 생성
    workflow = StateGraph(RealEstateState)

    # 에이전트 인스턴스 생성 - enable_rag에 따라 검색 문서 수 결정
    k_value = 2 if enable_rag else 0
    rational_agent = RationalAgent(k=k_value, session_id=session_id)
    emotional_agent = EmotionalAgent(k=k_value, session_id=session_id)
    mediator_agent = MediatorAgent(k=k_value, session_id=session_id)
    round_manager = RoundManager()

    # 노드 추가
    workflow.add_node(AgentType.RATIONAL, rational_agent.run)
    workflow.add_node(AgentType.EMOTIONAL, emotional_agent.run)
    workflow.add_node(AgentType.MEDIATOR, mediator_agent.run)
    workflow.add_node("INCREMENT_ROUND", round_manager.run)
    workflow.add_edge(AgentType.RATIONAL, AgentType.EMOTIONAL)  # 이성적 조언자 → 감성적 조언자
    workflow.add_edge(AgentType.EMOTIONAL, "INCREMENT_ROUND")  # 감성적 조언자 → 조건부 라우팅

    workflow.add_conditional_edges(
        "INCREMENT_ROUND",
        lambda s: (
            AgentType.MEDIATOR if s["current_round"] > s["max_rounds"] else AgentType.RATIONAL
        ),
        [AgentType.MEDIATOR, AgentType.RATIONAL],
    )

    workflow.set_entry_point(AgentType.RATIONAL)
    workflow.add_edge(AgentType.MEDIATOR, END)

    # 그래프 컴파일
    return workflow.compile()


if __name__ == "__main__":

    graph = create_real_estate_graph(True)

    graph_image = graph.get_graph().draw_mermaid_png()

    output_path = "real_estate_graph.png"
    with open(output_path, "wb") as f:
        f.write(graph_image)

    import subprocess

    subprocess.run(["open", output_path])
