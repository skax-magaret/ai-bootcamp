from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

Base = declarative_base()


class Consultation(Base):
    """상담 기록 데이터베이스 모델"""
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_query = Column(Text, nullable=False)
    consultation_type = Column(String(50), nullable=False)
    patient_info = Column(Text, nullable=False)  # JSON 문자열
    messages = Column(Text, nullable=False)  # JSON 문자열
    docs = Column(Text, nullable=True)  # JSON 문자열
    summary = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic 모델들 (API 요청/응답용)

class PatientInfo(BaseModel):
    """환자 정보 모델"""
    age: str = "50"
    occupation: str = "사무직"
    family: str = "배우자와 자녀 2명"
    post_surgery_period: str = "수술 예정"
    symptoms: str = "허리 통증"


class ConsultationMessage(BaseModel):
    """상담 메시지 모델"""
    role: str
    content: str
    timestamp: int = 0


class ConsultationRequest(BaseModel):
    """상담 요청 모델"""
    patient_query: str
    patient_info: PatientInfo = PatientInfo()
    consultation_type: str = "일반"
    max_turns: int = 6
    enable_rag: bool = True
    session_id: Optional[str] = None


class ConsultationResponse(BaseModel):
    """상담 응답 모델"""
    patient_query: str
    consultation_type: str
    patient_info: PatientInfo
    messages: List[ConsultationMessage]
    docs: Dict[str, List[str]] = {}
    summary: str = ""
    is_completed: bool = True


class ConsultationHistory(BaseModel):
    """상담 기록 모델"""
    id: int
    patient_query: str
    consultation_type: str
    patient_info: PatientInfo
    message_count: int
    created_at: datetime


class ConsultationStatistics(BaseModel):
    """상담 통계 모델"""
    total_consultations: int
    consultations_by_type: Dict[str, int]
    recent_consultations: int
    average_turns: float


# 기존 Debate 모델들 (하위 호환성을 위해 유지)
class Debate(Base):
    """토론 기록 데이터베이스 모델 (레거시)"""
    __tablename__ = "debates"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(500), nullable=False)
    rounds = Column(Integer, nullable=False)
    messages = Column(Text, nullable=False)
    docs = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DebateRequest(BaseModel):
    """토론 요청 모델 (레거시)"""
    topic: str
    max_rounds: int = 3
    enable_rag: bool = True
    session_id: Optional[str] = None


class DebateResponse(BaseModel):
    """토론 응답 모델 (레거시)"""
    topic: str
    messages: List[Dict[str, Any]]
    docs: Dict[str, List[str]] = {}
    rounds: int = 0
