from typing import Any
import uuid
import json
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langfuse.callback import CallbackHandler


from workflow.state import AgentType, RealEstateState
from workflow.graph import create_real_estate_graph


# API 경로를 /api/v1로 변경
router = APIRouter(
    prefix="/api/v1/workflow",
    tags=["workflow"],
    responses={404: {"description": "Not found"}},
)


class RealEstateWorkflowRequest(BaseModel):
    budget: str
    property_type: str
    preference1: str
    preference2: str
    max_rounds: int = 3
    enable_rag: bool = True


class WorkflowResponse(BaseModel):
    status: str = "success"
    result: Any = None


async def real_estate_generator(real_estate_graph, initial_state, langfuse_handler):
    # 그래프에서 청크 스트리밍
    for chunk in real_estate_graph.stream(
        initial_state,
        config={"callbacks": [langfuse_handler]},
        subgraphs=True,
        stream_mode="updates",
    ):
        if not chunk:
            continue

        node = chunk[0] if len(chunk) > 0 else None
        if not node or node == ():
            continue

        node_name = node[0]
        role = node_name.split(":")[0]
        subgraph = chunk[1]
        subgraph_node = subgraph.get("update_state", None)

        if subgraph_node:
            response = subgraph_node.get("response", None)
            real_estate_state = subgraph_node.get("real_estate_state", None)
            messages = real_estate_state.get("messages", [])
            round = real_estate_state.get("current_round")
            max_rounds = real_estate_state.get("max_rounds")
            docs = real_estate_state.get("docs", {})
            budget = real_estate_state.get("budget")
            property_type = real_estate_state.get("property_type")
            preference1 = real_estate_state.get("preference1")
            preference2 = real_estate_state.get("preference2")
            recommended_properties = real_estate_state.get("recommended_properties", [])
            additional_options = real_estate_state.get("additional_options", [])

            state = {
                "role": role,
                "response": response,
                "budget": budget,
                "property_type": property_type,
                "preference1": preference1,
                "preference2": preference2,
                "messages": messages,
                "current_round": round,
                "max_rounds": max_rounds,
                "docs": docs,
                "recommended_properties": recommended_properties,
                "additional_options": additional_options,
            }

            event_data = {"type": "update", "data": state}
            yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
            print(event_data)

            await asyncio.sleep(0.01)

    # 상담 종료 메시지
    yield f"data: {json.dumps({'type': 'end', 'data': {}}, ensure_ascii=False)}\n\n"


# 부동산 상담 스트리밍 엔드포인트
@router.post("/real-estate/stream")
async def stream_real_estate_workflow(request: RealEstateWorkflowRequest):
    budget = request.budget
    property_type = request.property_type
    preference1 = request.preference1
    preference2 = request.preference2
    max_rounds = request.max_rounds
    enable_rag = request.enable_rag

    session_id = str(uuid.uuid4())
    real_estate_graph = create_real_estate_graph(enable_rag, session_id)

    initial_state: RealEstateState = {
        "budget": budget,
        "property_type": property_type,
        "preference1": preference1,
        "preference2": preference2,
        "messages": [],
        "current_round": 1,
        "max_rounds": max_rounds,
        "prev_node": "START",  # 이전 노드 START로 설정
        "docs": {},  # RAG 결과 저장
        "recommended_properties": [],  # 추천 매물
        "additional_options": [],  # 추가 옵션
    }

    langfuse_handler = CallbackHandler(session_id=session_id)

    # 스트리밍 응답 반환
    return StreamingResponse(
        real_estate_generator(real_estate_graph, initial_state, langfuse_handler),
        media_type="text/event-stream",
    )
