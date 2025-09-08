from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func

from db.database import Base


# 부동산 상담 모델
class RealEstateConsultation(Base):
    __tablename__ = "real_estate_consultations"

    id = Column(Integer, primary_key=True, index=True)
    budget = Column(String(100), nullable=False)  # 예산
    property_type = Column(String(50), nullable=False)  # 매물 유형
    preference1 = Column(String(100), nullable=False)  # 선호 조건1
    preference2 = Column(String(200), nullable=False)  # 선호 조건2
    rounds = Column(Integer, default=1)
    messages = Column(Text, nullable=False)  # JSON 문자열로 저장
    docs = Column(Text, nullable=True)  # JSON 문자열로 저장
    recommended_properties = Column(Text, nullable=True)  # 추천 매물 JSON
    additional_options = Column(Text, nullable=True)  # 추가 옵션 JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# 부동산 매물 모델 (RAG용)
class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)  # 매물 제목
    price = Column(Float, nullable=False)  # 가격 (억원)
    property_type = Column(String(50), nullable=False)  # 매물 유형
    location = Column(String(100), nullable=False)  # 위치
    area = Column(Float, nullable=False)  # 면적 (평)
    rooms = Column(Integer, nullable=True)  # 방 개수
    bathrooms = Column(Integer, nullable=True)  # 화장실 개수
    floor = Column(Integer, nullable=True)  # 층수
    total_floors = Column(Integer, nullable=True)  # 총 층수
    direction = Column(String(20), nullable=True)  # 방향
    parking = Column(Boolean, default=False)  # 주차 가능 여부
    elevator = Column(Boolean, default=False)  # 엘리베이터 여부
    description = Column(Text, nullable=True)  # 상세 설명
    nearby_facilities = Column(Text, nullable=True)  # 주변 편의시설
    transportation = Column(Text, nullable=True)  # 교통편
    created_at = Column(DateTime(timezone=True), server_default=func.now())
