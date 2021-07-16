from numpy import integer
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, Float, String, Integer

app = FastAPI()

# SqlAlchemy Setup
SQLALCHEMY_DATABASE_URL = 'sqlite+pysqlite:///./db.sqlite3:'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# A SQLAlchemny ORM Place
class IncidentFormDatabase(Base):
    __tablename__ = 'IncidentForm_DB'

    id = Column(Integer,primary_key=True,index=True)
    incident_id = Column(Integer)
    site_id: Column(Integer)
    ca_number: Column(String(50))
    h_name: Column(String(50))
    h_address: Column(String(50)) #location
    category: Column(String(50))
    constituency: Column(String(50))
    ph_no: Column(Integer)
    alt_ph_no : Column(Integer)
    description : Column(String, nullable=True)
    service : Column(String(50))
    status : 
    priority : 
    date : 

Base.metadata.create_all(bind=engine)

# A Pydantic Place
class Incident(BaseModel):
    
    incident_id: int
    site_id: int
    ca_number: Optional[str] = None
    h_name: str
    h_address: str
    category: str
    constituency: str
    ph_no: int
    alt_ph_no : int
    description : Optional[str] = None
    service : str

    class Config:
        orm_mode = True

# Methods for interacting with the database


def db_all_incidents(db : Session):
    return db.query(IncidentFormDatabase).all()

# Routes for interacting with the API
def db_create_incident(db: Session, incident: Incident):
    incident_db = IncidentFormDatabase(**incident.dict())
    db.add(incident_db)
    db.commit()
    db.refresh(incident_db)

    return incident_db

def db_get_incident(db : Session, incident_id : int):
    return db.query(IncidentFormDatabase).where(IncidentFormDatabase.id == incident_id).first()

@app.post('/incident/', response_model=Incident)
def create_places_view(incident: Incident, db: Session = Depends(get_db)):
    incident_db = db_create_incident(db, incident)
    return incident_db

@app.get("/incidents/", response_model=List[Incident])
def all_incidents(db : Session = Depends(get_db)):
    return db_all_incidents(db)

@app.get('/incident/{incident_id}')
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    return db_get_incident(db, incident_id)


