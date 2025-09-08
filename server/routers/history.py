from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import RealEstateConsultation as ConsultationModel, Property as PropertyModel
from db.schemas import RealEstateConsultationSchema, RealEstateConsultationCreate, PropertySchema, PropertyCreate

router = APIRouter(prefix="/api/v1", tags=["real-estate"])


# 부동산 상담 목록 조회
@router.get("/real-estate-consultations/", response_model=List[RealEstateConsultationSchema])
def read_consultations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    consultations = db.query(ConsultationModel).offset(skip).limit(limit).all()
    return consultations


# 부동산 상담 생성
@router.post("/real-estate-consultations/", response_model=RealEstateConsultationSchema)
def create_consultation(consultation: RealEstateConsultationCreate, db: Session = Depends(get_db)):
    db_consultation = ConsultationModel(**consultation.model_dump())
    db.add(db_consultation)
    db.commit()
    db.refresh(db_consultation)
    return db_consultation


# 부동산 상담 조회
@router.get("/real-estate-consultations/{consultation_id}", response_model=RealEstateConsultationSchema)
def read_consultation(consultation_id: int, db: Session = Depends(get_db)):
    db_consultation = db.query(ConsultationModel).filter(ConsultationModel.id == consultation_id).first()
    if db_consultation is None:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return db_consultation


# 부동산 상담 삭제
@router.delete("/real-estate-consultations/{consultation_id}")
def delete_consultation(consultation_id: int, db: Session = Depends(get_db)):
    db_consultation = db.query(ConsultationModel).filter(ConsultationModel.id == consultation_id).first()
    if db_consultation is None:
        raise HTTPException(status_code=404, detail="Consultation not found")

    db.delete(db_consultation)
    db.commit()
    return {"detail": "Consultation successfully deleted"}


# 부동산 매물 목록 조회
@router.get("/properties/", response_model=List[PropertySchema])
def read_properties(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    properties = db.query(PropertyModel).offset(skip).limit(limit).all()
    return properties


# 부동산 매물 생성
@router.post("/properties/", response_model=PropertySchema)
def create_property(property: PropertyCreate, db: Session = Depends(get_db)):
    db_property = PropertyModel(**property.model_dump())
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property
