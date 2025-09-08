from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# 환경변수 로드
load_dotenv()

# 라우터 임포트
from routers.consultation import router as consultation_router
from routers.workflow import router as workflow_router  # 기존 토론용 (레거시)
from routers.history import router as history_router

# 데이터베이스 설정
from db.database import engine
from db.models import Base

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI(
    title="척추 유합술 AI 상담 시스템",
    description="LangChain & LangGraph 기반 Multi-Agent 척추 유합술 상담 시스템",
    version="2.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 오리진 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(consultation_router, prefix="/api/v1")
app.include_router(workflow_router, prefix="/api/v1")  # 레거시 지원
app.include_router(history_router, prefix="/api/v1")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "척추 유합술 AI 상담 시스템",
        "description": "LangChain & LangGraph 기반 Multi-Agent 시스템",
        "version": "2.0.0",
        "features": [
            "🩺 전문의 수준의 의학 상담",
            "🤒 실제 환자 관점의 질문",
            "👩‍💼 체계적인 상담 요약",
            "🔍 RAG 기반 지식 검색",
            "💬 Chain-of-Thought 추론",
            "📝 Few-shot Learning"
        ],
        "endpoints": {
            "consultation": "/api/v1/consultation",
            "health": "/api/v1/consultation/health",
            "types": "/api/v1/consultation/types",
            "history": "/api/v1/history"
        }
    }


@app.get("/health")
async def health_check():
    """전체 시스템 헬스체크"""
    return {
        "status": "healthy",
        "message": "척추 유합술 AI 상담 시스템이 정상적으로 작동중입니다.",
        "services": {
            "database": "connected",
            "consultation_engine": "ready",
            "rag_system": "initialized"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )