import base64
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserOut(BaseModel):
    id: int
    name: str
    surname: str

    class Config:
        orm_mode = True


class DiseaseOut(BaseModel):
    id: int
    disease_name: str
    disease_detail: Optional[str]
    image_name: Optional[str] = None
    image_ar: Optional[str] = None

    @classmethod
    def from_orm_with_base64(cls, disease):
        return cls(
            id=disease.id,
            disease_name=disease.disease_name,
            disease_detail=disease.disease_detail,
            image_name=base64.b64encode(disease.image_name).decode('utf-8') if disease.image_name else None,
            image_ar=base64.b64encode(disease.image_ar).decode('utf-8') if disease.image_ar else None,
        )

    class Config:
        orm_mode = True


class DiseaseInfoOut(BaseModel):
    id: int
    diagnosis_date: datetime
    doctor: Optional[UserOut]
    patient: Optional[UserOut]
    disease: Optional[DiseaseOut]

    @classmethod
    def from_orm_with_base64(cls, disease_info):
        return cls(
            id=disease_info.id,
            diagnosis_date=disease_info.diagnosis_date,
            doctor=disease_info.doctor,
            patient=disease_info.patient,
            disease=DiseaseOut.from_orm_with_base64(disease_info.disease) if disease_info.disease else None
        )

    class Config:
        orm_mode = True


class CsvDetailOut(BaseModel):
    id: int
    isic_id: str
    age: int
    image: Optional[str] = None

    disease: Optional[DiseaseOut]
    body_location: Optional[str]
    benign_type: Optional[str]
    sex: Optional[str]

    @classmethod
    def from_orm_with_base64(cls, csv):
        return cls(
            id=csv.id,
            isic_id=csv.isic_id,
            age=csv.age,
            image=base64.b64encode(csv.image).decode('utf-8') if csv.image else None,
            disease=DiseaseOut.from_orm_with_base64(csv.disease) if csv.disease else None,
            body_location=csv.body_location.location if csv.body_location else None,
            benign_type=csv.benign_type.type if csv.benign_type else None,
            sex=csv.sex.type if csv.sex else None
        )

    class Config:
        orm_mode = True
