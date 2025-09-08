from langchain.schema import HumanMessage, SystemMessage, AIMessage
from retrieval.vector_store import search_spinal_fusion_topic
from utils.config import get_llm
from workflow.state import ConsultationState, AgentType
from abc import ABC, abstractmethod
from typing import List, Dict, Any, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langfuse.callback import CallbackHandler


# 에이전트 내부 상태 타입 정의
class AgentState(TypedDict):
    consultation_state: Dict[str, Any]  # 전체 상담 상태
    context: str  # 검색된 컨텍스트
    messages: List[BaseMessage]  # LLM에 전달할 메시지
    response: str  # LLM 응답


# 에이전트 추상 클래스 정의
class Agent(ABC):

    def __init__(
        self, system_prompt: str, role: str, k: int = 2, session_id: str = None
    ):
        self.system_prompt = system_prompt
        self.role = role
        self.k = k  # 검색할 문서 개수
        self._setup_graph()  # 그래프 설정
        self.session_id = session_id  # langfuse 세션 ID

    def _setup_graph(self):
        # 그래프 생성
        workflow = StateGraph(AgentState)

        # 노드 추가
        workflow.add_node("retrieve_context", self._retrieve_context)  # 자료 검색
        workflow.add_node("prepare_messages", self._prepare_messages)  # 메시지 준비
        workflow.add_node("generate_response", self._generate_response)  # 응답 생성
        workflow.add_node("update_state", self._update_state)  # 상태 업데이트

        # 엣지 추가 - 순차 실행 흐름
        workflow.add_edge("retrieve_context", "prepare_messages")
        workflow.add_edge("prepare_messages", "generate_response")
        workflow.add_edge("generate_response", "update_state")

        workflow.set_entry_point("retrieve_context")
        workflow.add_edge("update_state", END)

        # 그래프 컴파일
        self.graph = workflow.compile()

    # 자료 검색
    def _retrieve_context(self, state: AgentState) -> AgentState:

        # k=0이면 검색 비활성화
        if self.k == 0:
            return {**state, "context": ""}

        consultation_state = state["consultation_state"]
        patient_query = consultation_state.get("patient_query", "")
        consultation_type = consultation_state.get("consultation_type", "일반")

        # 척추 유합술 관련 문서 검색
        docs = search_spinal_fusion_topic(
            consultation_type=consultation_type,
            query=patient_query,
            k=self.k
        )

        # 검색 결과를 컨텍스트로 변환
        context = ""
        if docs:
            context = "\n".join([doc.page_content for doc in docs[:self.k]])

        # 상담 상태에 검색 결과 저장
        new_consultation_state = consultation_state.copy()
        new_consultation_state["contexts"] = new_consultation_state.get("contexts", {})
        new_consultation_state["contexts"][self.role] = context
        new_consultation_state["docs"] = new_consultation_state.get("docs", {})
        new_consultation_state["docs"][self.role] = docs

        return {**state, "context": context, "consultation_state": new_consultation_state}

    # 메시지 준비
    def _prepare_messages(self, state: AgentState) -> AgentState:

        consultation_state = state["consultation_state"]
        context = state["context"]

        # 상담 상태에 컨텍스트 추가
        consultation_state_with_context = consultation_state.copy()
        consultation_state_with_context["context"] = context

        # 프롬프트 생성
        prompt = self._create_prompt(consultation_state_with_context)

        # 메시지 구성
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]

        return {**state, "messages": messages}

    # 응답 생성
    def _generate_response(self, state: AgentState) -> AgentState:

        messages = state["messages"]
        llm = get_llm()

        # LLM 호출
        response = llm.invoke(messages)
        response_content = response.content if hasattr(response, 'content') else str(response)

        return {**state, "response": response_content}

    # 상태 업데이트
    def _update_state(self, state: AgentState) -> AgentState:

        consultation_state = state["consultation_state"]
        response = state["response"]

        # 새로운 메시지 추가
        new_message = {
            "role": self.role,
            "content": response,
            "timestamp": consultation_state.get("current_turn", 0)
        }

        # 상담 상태 업데이트
        new_consultation_state = consultation_state.copy()
        new_consultation_state["messages"] = new_consultation_state.get("messages", []) + [new_message]

        # 상태 업데이트
        return {**state, "consultation_state": new_consultation_state}

    # 상담 실행
    def run(self, state: ConsultationState) -> ConsultationState:

        # 초기 에이전트 상태 구성
        agent_state = AgentState(
            consultation_state=state, context="", messages=[], response=""
        )

        # 내부 그래프 실행
        langfuse_handler = CallbackHandler(session_id=self.session_id)
        result = self.graph.invoke(
            agent_state, config={"callbacks": [langfuse_handler]}
        )

        # 최종 상담 상태 반환
        return result["consultation_state"]

    @abstractmethod
    def _create_prompt(self, state: Dict[str, Any]) -> str:
        """각 에이전트별 프롬프트 생성 - 하위 클래스에서 구현"""
        pass
