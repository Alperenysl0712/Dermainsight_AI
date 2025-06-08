from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from db.utility import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    name = Column(String)
    surname = Column(String)
    email = Column(String)
    user_type = Column(String)
    phone = Column(String)
    password = Column(String)


class Disease(Base):
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    disease_name = Column(String)
    image_name = Column(LargeBinary)
    image_ar = Column(LargeBinary)
    disease_detail = Column(String)


class DiseaseInfo(Base):
    __tablename__ = "diseaseinfo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey('users.id'))
    patient_id = Column(Integer, ForeignKey('users.id'))
    disease_id = Column(Integer, ForeignKey('diseases.id'))
    diagnosis_date = Column(DateTime)

    doctor = relationship("User", foreign_keys=[doctor_id])
    patient = relationship("User", foreign_keys=[patient_id])
    disease = relationship("Disease", foreign_keys=[disease_id])

class Sex(Base):
    __tablename__ = "sex"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)

class BenignType(Base):
    __tablename__ = "benigntype"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)

class BodyLocation(Base):
    __tablename__ = "bodylocation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String)

class CsvDetail(Base):
    __tablename__ = "csvdetail"
    id = Column(Integer, primary_key=True, autoincrement=True)
    isic_id = Column(String)
    age = Column(Integer)
    disease_id = Column(Integer, ForeignKey('diseases.id'))
    body_location_id = Column(Integer, ForeignKey('bodylocation.id'))
    benign_type_id = Column(Integer, ForeignKey('benigntype.id'))
    sex_id = Column(Integer, ForeignKey('sex.id'))
    image = Column(LargeBinary)

    disease = relationship("Disease", foreign_keys=[disease_id])
    body_location = relationship("BodyLocation", foreign_keys=[body_location_id])
    benign_type = relationship("BenignType", foreign_keys=[benign_type_id])
    sex = relationship('Sex', foreign_keys=[sex_id])

