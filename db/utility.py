import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

server = "localhost"
database = 'Dermainsight'
username = 'Alperenysl0712'
password = 'Alperen0712.'

connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

engine = create_engine(connection_string)
SessionLocal = sessionmaker(autocommit = False, bind=engine)
Base = declarative_base()


