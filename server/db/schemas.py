from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# 부동산 상담 DTO 클래스 정의
class RealEstateConsultationBase(BaseModel):
    budget: str
    property_type: str
    preference1: str
    preference2: str
    rounds: int
    messages: str  # JSON 문자열
    docs: Optional[str] = None  # JSON 문자열
    recommended_properties: Optional[str] = None  # JSON 문자열
    additional_options: Optional[str] = None  # JSON 문자열


class RealEstateConsultationCreate(RealEstateConsultationBase):
    pass


class RealEstateConsultationSchema(RealEstateConsultationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 부동산 매물 DTO 클래스 정의
class PropertyBase(BaseModel):
    title: str
    price: float
    property_type: str
    location: str
    area: float
    rooms: Optional[int] = None
    bathrooms: Optional[int] = None
    floor: Optional[int] = None
    total_floors: Optional[int] = None
    direction: Optional[str] = None
    parking: bool = False
    elevator: bool = False
    description: Optional[str] = None
    nearby_facilities: Optional[str] = None
    transportation: Optional[str] = None


class PropertyCreate(PropertyBase):
    pass


class PropertySchema(PropertyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# API 요청/응답 스키마
class RealEstateSearchRequest(BaseModel):
    budget: str
    property_type: str
    preference1: str
    preference2: str
    max_rounds: int = 1
    enable_rag: bool = True


class RealEstateSearchResponse(BaseModel):
    messages: List[Dict[str, Any]]
    recommended_properties: Optional[List[Dict[str, Any]]] = None
    additional_options: Optional[List[str]] = None
    docs: Optional[Dict[str, List[str]]] = None
