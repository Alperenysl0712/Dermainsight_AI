import base64

from pydantic import BaseModel, Field
from typing import Optional
from datetime import  datetime


class UserSchema(BaseModel):
    id: Optional[int] = Field(default=None, alias="Id")
    username: str = Field(alias="Username")
    name: str = Field(alias="Name")
    surname: str = Field(alias="Surname")
    user_type: str = Field(alias="UserType")
    email: str = Field(alias="Email")
    phone: str = Field(alias="Phone")
    password: str = Field(alias="Password")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "by_alias": True
    }

class DiseaseSchema(BaseModel):
    id: Optional[int] = Field(default=None, alias="Id")
    disease_name: str = Field(alias="DiseaseName")
    image_name: Optional[str] = Field(default=None, alias="ImageName")  # base64 string dönecek
    image_ar: Optional[str] = Field(default=None, alias="ImageAr")
    disease_detail: Optional[str] = Field(default=None, alias="DiseaseDetail")

    model_config = {
        "from_attributes": True,
        "ser_json_typed": True,
        "populate_by_name": True,
        "json_encoders": {},
        "alias_generator": None,
        "by_alias": True
    }

    @classmethod
    def from_orm_with_base64(cls, disease):
        return cls(
            Id=disease.id,
            DiseaseName=disease.disease_name,
            ImageName=base64.b64encode(disease.image_name).decode('utf-8') if disease.image_name else None,
            ImageAr=base64.b64encode(disease.image_ar).decode('utf-8') if disease.image_ar else None,
            DiseaseDetail=disease.disease_detail
        )

    @classmethod
    def form_orm_without_images(cls, disease):
        return cls(
            Id = disease.id,
            DiseaseName = disease.disease_name,
            ImageName = None,
            ImageAr = None,
            DiseaseDetail = disease.disease_detail
        )

class DiseaseInfoSchema(BaseModel):
    id: Optional[int] = Field(default=None, alias="Id")
    doctor_id: int = Field(alias="DoctorId")
    patient_id: int = Field(alias="PatientId")
    disease_id: int = Field(alias="DiseaseId")
    diagnosis_date: Optional[datetime] = Field(default_factory=datetime.now, alias="DiagnosisDate")

    doctor: Optional[UserSchema] = Field(default=None, alias="Doctor")
    patient: Optional[UserSchema] = Field(default=None, alias="Patient")
    disease: Optional[DiseaseSchema] = Field(default=None, alias="Disease")

    model_config = {
        "from_attributes": True,
        "ser_json_typed": True,
        "populate_by_name": True,
        "json_encoders": {},
        "alias_generator": None,
        "by_alias": True
    }

    @classmethod
    def from_orm_with_base64(cls, instance):
        data = {
            "DoctorId": instance.doctor_id,
            "PatientId": instance.patient_id,
            "DiseaseId": instance.disease_id,
            "DiagnosisDate": instance.diagnosis_date,
            "Id": instance.id,
            "Doctor": UserSchema.model_validate(instance.doctor) if instance.doctor else None,
            "Patient": UserSchema.model_validate(instance.patient) if instance.patient else None,
            "Disease": DiseaseSchema.form_orm_without_images(instance.disease) if instance.disease else None
        }
        return cls(**data)


class UserRequest(BaseModel):
    username: str
    password: str


class DiseaseInfoRequest(BaseModel):
    patient_id: int


class PatientsRequest(BaseModel):
    doctor_id: int

class DiseaseRequest(BaseModel):
    doctor_id: int
    patient_id: int
    disease_id: int

class CsvDetailSchema(BaseModel):
    disease_name: str
    image_base64: str