from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional
import json
import asyncio
from workflow.consultation_graph import create_consultation_graph, initialize_consultation_state
from db.models import ConsultationRequest, ConsultationResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/consultation", tags=["consultation"])


@router.post("/stream")
async def stream_consultation(request: ConsultationRequest):
    """상담을 스트리밍으로 실행"""
    
    try:
        # 상담 그래프 생성
        graph = create_consultation_graph(
            enable_rag=request.enable_rag,
            session_id=request.session_id or "default"
        )
        
        # 상담 상태 초기화
        initial_state = initialize_consultation_state(
            patient_query=request.patient_query,
            patient_info=request.patient_info,
            consultation_type=request.consultation_type,
            max_turns=request.max_turns
        )
        
        async def generate_events():
            """상담 진행 이벤트 생성"""
            try:
                # 상담 실행
                for event in graph.stream(initial_state):
                    # 각 노드의 실행 결과 처리
                    for node_name, node_output in event.items():
                        if node_name in ["DOCTOR_AGENT", "PATIENT_AGENT", "COORDINATOR_AGENT"]:
                            # 메시지가 있는 경우 스트리밍
                            if node_output.get("messages"):
                                last_message = node_output["messages"][-1]
                                
                                event_data = {
                                    "type": "update",
                                    "data": {
                                        "role": last_message["role"],
                                        "response": last_message["content"],
                                        "patient_query": node_output["patient_query"],
                                        "consultation_type": node_output["consultation_type"],
                                        "patient_info": node_output["patient_info"],
                                        "messages": node_output["messages"],
                                        "current_turn": node_output["current_turn"],
                                        "max_turns": node_output["max_turns"],
                                        "docs": node_output.get("docs", {}),
                                        "is_completed": node_output.get("is_completed", False)
                                    }
                                }
                                
                                yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
                                
                                # 상담 완료 시 종료
                                if node_output.get("is_completed", False):
                                    break
                        
                        # 작은 지연으로 스트리밍 효과
                        await asyncio.sleep(0.1)
                
                # 완료 이벤트 전송
                end_event = {"type": "end", "data": {}}
                yield f"data: {json.dumps(end_event)}\n\n"
                
            except Exception as e:
                logger.error(f"상담 스트리밍 중 오류: {str(e)}")
                error_event = {
                    "type": "error", 
                    "data": {"message": f"상담 진행 중 오류가 발생했습니다: {str(e)}"}
                }
                yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_events(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        logger.error(f"상담 시작 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상담을 시작할 수 없습니다: {str(e)}")


@router.post("/", response_model=ConsultationResponse)
async def run_consultation(request: ConsultationRequest):
    """상담을 일반적인 방식으로 실행 (비스트리밍)"""
    
    try:
        # 상담 그래프 생성
        graph = create_consultation_graph(
            enable_rag=request.enable_rag,
            session_id=request.session_id or "default"
        )
        
        # 상담 상태 초기화
        initial_state = initialize_consultation_state(
            patient_query=request.patient_query,
            patient_info=request.patient_info,
            consultation_type=request.consultation_type,
            max_turns=request.max_turns
        )
        
        # 상담 실행
        final_state = await asyncio.get_event_loop().run_in_executor(
            None, graph.invoke, initial_state
        )
        
        return ConsultationResponse(
            patient_query=final_state["patient_query"],
            consultation_type=final_state["consultation_type"],
            patient_info=final_state["patient_info"],
            messages=final_state["messages"],
            docs=final_state.get("docs", {}),
            summary=final_state.get("summary", ""),
            is_completed=final_state.get("is_completed", True)
        )
        
    except Exception as e:
        logger.error(f"상담 실행 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상담을 실행할 수 없습니다: {str(e)}")


@router.get("/health")
async def health_check():
    """상담 시스템 상태 확인"""
    try:
        # 간단한 상담 그래프 생성 테스트
        graph = create_consultation_graph(enable_rag=False)
        return {
            "status": "healthy",
            "message": "상담 시스템이 정상적으로 작동중입니다.",
            "graph_nodes": len(graph.get_graph().nodes)
        }
    except Exception as e:
        logger.error(f"헬스체크 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상담 시스템에 문제가 있습니다: {str(e)}")


@router.get("/types")
async def get_consultation_types():
    """사용 가능한 상담 유형 목록 반환"""
    return {
        "consultation_types": [
            {"code": "수술_전", "name": "수술 전 상담", "description": "수술 전 준비사항 및 주의사항"},
            {"code": "수술_후", "name": "수술 후 상담", "description": "수술 후 관리 및 회복 과정"},
            {"code": "재활", "name": "재활 상담", "description": "재활 운동 및 물리치료 관련"},
            {"code": "합병증", "name": "합병증 상담", "description": "합병증 및 응급상황 대처"},
            {"code": "일반", "name": "일반 상담", "description": "척추 유합술 전반적인 정보"}
        ]
    } 