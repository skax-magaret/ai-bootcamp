import uvicorn
from fastapi import FastAPI

# 절대 경로 임포트로 수정
from routers import workflow

# 데이터베이스 초기화를 위한 임포트 추가
from db.database import Base, engine
from routers import history

# 데이터베이스 초기화
Base.metadata.create_all(bind=engine)

# FastAPI 인스턴스 생성
app = FastAPI(
    title="Real Estate AI Agent API",
    description="AI 부동산 중개 에이전트 서비스를 위한 API",
    version="0.1.0",
)

# router 추가
app.include_router(history.router)
app.include_router(workflow.router)

# 실행은 server 경로에서
# . venv/bin/activate
# uvicorn main:app --port=8001