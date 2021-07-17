from numpy import integer
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, Float, String, Integer
from fastapi.encoders import jsonable_encoder
import uvicorn
 
# default schemas can now be viewed at localhost:8000/schemas
app = FastAPI(docs_url="/schemas")

# SqlAlchemy Setup
SQLALCHEMY_DATABASE_URL = 'sqlite+pysqlite:///./db.sqlite3'
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
    site_id = Column(Integer)
    ca_number =  Column(String(50))
    h_name =  Column(String(50))
    h_address=  Column(String(50)) #location
    category=  Column(String(50))
    constituency=  Column(String(50))
    ph_no= Column(String(50))
    alt_ph_no =  Column(String(50))
    description =  Column(String, nullable=True)
    service =  Column(String(50))
    status =  Column(String(50))
    priority =  Column(String(50))
    date =  Column(String(50))

Base.metadata.create_all(bind=engine)

# A Pydantic Place
class Incident(BaseModel):
    
    site_id: int
    ca_number: Optional[str] = None
    h_name: str
    h_address: str
    category: str
    constituency: str
    ph_no: str
    alt_ph_no : str
    description : Optional[str] = None
    service : str
    status : str
    priority : str
    date : str

    class Config:
        orm_mode = True


# GET method to retrieve all incidents
def db_all_incidents(db : Session):
    return db.query(IncidentFormDatabase).all()

@app.get("/incidents/", response_model=List[Incident])
def all_incidents(db : Session = Depends(get_db)):
    return db_all_incidents(db)

# POST method to create an incident
def db_create_incident(db: Session, incident: Incident):
    incident_db = IncidentFormDatabase(**incident.dict())
    db.add(incident_db)
    db.commit()
    db.refresh(incident_db)
    return incident_db

@app.post('/incident/', response_model=Incident)
def create_places_view(incident: Incident, db: Session = Depends(get_db)):
    incident_db = db_create_incident(db, incident)
    return incident_db

# GET method to retrieve incident based on its Incident ID
def db_get_incident(db : Session, incident_id : int):
    return db.query(IncidentFormDatabase).where(IncidentFormDatabase.id == incident_id).first()

@app.get('/incident/{incident_id}')
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    return db_get_incident(db, incident_id)


# PUT method to update an incident based on its Incident ID
def db_update_incident(db : Session, incident_id: int, updated_incident : Incident, incident_dictionary):
    return db.query(IncidentFormDatabase).filter(IncidentFormDatabase.id==incident_id).update(incident_dictionary)

@app.put('/incident/{incident_id}', response_model = Incident)
def update_incident(updated_incident: Incident, incident_id: int, db: Session = Depends(get_db)):
    incident_dictionary = vars(updated_incident)
    db_update_incident(db, incident_id, updated_incident, incident_dictionary)
    db.commit()
    return updated_incident

@app.get('/', include_in_schema=False)
def rootText():
    return {"Message" : "Welcome to the API for the DelhiCCTV App "}

uvicorn.run(app)