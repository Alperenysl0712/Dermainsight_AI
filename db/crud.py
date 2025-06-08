import random
from typing import Optional
import re

from sqlalchemy.orm import Session, joinedload
from datetime import  datetime
from db.models import User, Disease, DiseaseInfo, CsvDetail
from passlib.context import CryptContext
import db.schemas as schema
import base64
import test_model

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def create_user(db: Session, user: schema.UserSchema):
    new_user = User(
        username=user.Username,
        name=user.Name,
        surname=user.Surname,
        email=user.Email,
        user_type=user.UserType,
        phone=user.Phone,
        password=user.Password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_users(db: Session):
    return db.query(User).all()


def get_user_by_username(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username, User.password == password).first()
    if user:
        return schema.UserSchema.model_validate(user)
    return None


def get_disease_list(db: Session):
    try:
        records = db.query(Disease).all()
        return [schema.DiseaseSchema.from_orm_with_base64(record) for record in records]
    except Exception as e:
        print("❌ Hata:", e)
        return {"error": str(e)}



def get_disease_info(db: Session, patient_id: int):
    records = db.query(DiseaseInfo) \
        .options(
        joinedload(DiseaseInfo.doctor),
        joinedload(DiseaseInfo.patient),
        joinedload(DiseaseInfo.disease)
        ) \
        .filter(DiseaseInfo.patient_id == patient_id) \
        .all()

    result = [schema.DiseaseInfoSchema.from_orm_with_base64(record) for record in records]
    return result



def get_patients_by_doctor(db: Session, doctor_id: int):
    records = db.query(User) \
        .join(DiseaseInfo, DiseaseInfo.patient_id == User.id) \
        .filter(DiseaseInfo.doctor_id.isnot(None), DiseaseInfo.doctor_id == doctor_id) \
        .all()

    return [schema.UserSchema.model_validate(record) for record in records]


def get_patients(db: Session):
    records = db.query(User) \
        .filter(User.user_type == "Hasta") \
        .all()

    return [schema.UserSchema.model_validate(record) for record in records]

def save_disease(db: Session, disease_req: schema.DiseaseInfoSchema):
    dis_info = DiseaseInfo(
        doctor_id = disease_req.doctor_id,
        patient_id = disease_req.patient_id,
        disease_id = disease_req.disease_id,
        diagnosis_date = datetime.now()
    )
    db.add(dis_info)
    db.commit()
    db.refresh(dis_info)
    return disease_req

def get_ai_result(db: Session, file_path: str):
    predict = test_model.predict_image(file_path)
    return predict

def create_new_csv(db: Session, csv_detail: schema.CsvDetailSchema) -> bool:
    try:
        disease = db.query(Disease).filter(Disease.disease_name == csv_detail.disease_name).first()
        dis_id = disease.id if disease else None

        if not dis_id:
            new_disease = Disease(
                disease_name=csv_detail.disease_name,
                image_name=decode_base64_to_bytes(csv_detail.image_base64),
            )
            db.add(new_disease)
            db.commit()
            db.refresh(new_disease)
            dis_id = new_disease.id

        nullable_fields = ["age", "sex_id", "body_location_id", "benign_type_id"]
        nulls = random.sample(nullable_fields, 2)

        age = None if "age" in nulls else random.randint(20, 80)
        sex_id = None if "sex_id" in nulls else random.randint(1, 2)
        body_location_id = None if "body_location_id" in nulls else random.randint(1, 8)
        benign_type_id = None if "benign_type_id" in nulls else random.randint(1, 3)

        new_csv_detail = CsvDetail(
            isic_id=generate_next_isic_id(db),
            age=age,
            disease_id=dis_id,
            sex_id=sex_id,
            body_location_id=body_location_id,
            benign_type_id=benign_type_id,
            image=decode_base64_to_bytes(csv_detail.image_base64)
        )

        db.add(new_csv_detail)
        db.commit()
        db.refresh(new_csv_detail)
        return True

    except Exception as e:
        db.rollback()  # 🔁 Hata durumunda rollback yap
        print(f"Hata: {e}")
        return False


def decode_base64_to_bytes(base64_str: str) -> bytes:
    # Eğer "data:image/png;base64,..." gibi geliyorsa başlık kısmını temizle
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]

    return base64.b64decode(base64_str)

def generate_next_isic_id(db: Session) -> str:
    # new_ ile başlayan isic_id’leri çek
    results = db.query(CsvDetail.isic_id).filter(CsvDetail.isic_id.like("new_%")).all()

    max_number = 0
    for (id_str,) in results:
        match = re.match(r"new_(\d+)", id_str)
        if match:
            num = int(match.group(1))
            if num > max_number:
                max_number = num

    # 1 artır ve yeni ID oluştur
    next_id = f"new_{max_number + 1}"
    return next_id