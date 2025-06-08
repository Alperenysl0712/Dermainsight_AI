import json
import os
from typing import List

from fastapi import FastAPI, Depends, File, UploadFile
from sqlalchemy.orm import Session

from db.schemas import CsvDetailSchema
from db.utility import SessionLocal, engine, Base
import db.crud as crud
import db.schemas as schema
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware
import db.responses as resp
from fastapi.responses import JSONResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health/")
def health_check():
    return {"status": "ok"}


@app.post("/register/")
def register_user(user: schema.UserSchema, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


@app.post("/getUserByUsername/")
def get_user_by_un(user_request: schema.UserRequest, db: Session = Depends(get_db)):
    user_schema = crud.get_user_by_username(db, user_request.username, user_request.password)
    if user_schema:
        return JSONResponse(content=user_schema.model_dump(by_alias=True))
    return JSONResponse(status_code=404, content={"error": "Kullanıcı bulunamadı"})


@app.get("/getDiseases/")
def get_diseases(db: Session = Depends(get_db)):
    disease_list = crud.get_disease_list(db)
    if disease_list:
        return JSONResponse(content=[item.model_dump(by_alias=True) for item in disease_list])
    return JSONResponse(status_code=404, content={"error": "Hastalıklar Bulunamadı"})


@app.post("/getPatientsByDoctor/")
def get_patients_by_doctor_api(doctor_id: schema.PatientsRequest, db: Session = Depends(get_db)):
    try:
        records = crud.get_patients_by_doctor(db, doctor_id.doctor_id)
        if records:
            return JSONResponse(content=[record.model_dump(by_alias=True) for record in records])
        return JSONResponse(status_code=404, content={"error": "Hastalar Bulunamadı"})
    except Exception as e:
        return {"error": str(e)}

@app.get("/getPatients/")
def get_patients_api(db: Session = Depends(get_db)):
    patient_list = crud.get_patients(db)
    if patient_list:
        return JSONResponse(content=[item.model_dump(by_alias=True) for item in patient_list])
    return JSONResponse(status_code=404, content={"error": "Hastalar Bulunamadı"})


@app.post("/getDiseaseInfo/", response_model=List[schema.DiseaseInfoSchema], response_model_by_alias=True)
def get_disease_info_api(patient_id: schema.DiseaseInfoRequest, db: Session = Depends(get_db)):
    return crud.get_disease_info(db, patient_id.patient_id)

@app.post("/createDiseaseInfo/")
def create_disease_info_api(disease_req: schema.DiseaseInfoSchema, db: Session = Depends(get_db)):
    try:
        result = crud.save_disease(db, disease_req)
        if result:
            return JSONResponse(content=json.loads(result.model_dump_json(by_alias=True)))
        return JSONResponse(status_code=404, content={"error": "Hastalık Kaydedilemedi"})
    except Exception as e:
        return {"error": str(e)}

@app.post("/getAiDisease/")
async def upload_image(image: UploadFile = File(...), db: Session = Depends(get_db)):
    if not image.filename:
        return JSONResponse(status_code=400, content={"error": "Dosya alınamadı."})

    temp_path = f"temp_{image.filename}"
    with open(temp_path, "wb") as f:
        f.write(await image.read())

    try:
        result = crud.get_ai_result(db, temp_path)
        os.remove(temp_path)
        return JSONResponse(content={"predictions": result})
    except Exception as e:
        os.remove(temp_path)
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/createNewCsv/")
def create_csv_api(csv_schema: schema.CsvDetailSchema, db: Session = Depends(get_db)):
    result = crud.create_new_csv(db, csv_schema)
    return result