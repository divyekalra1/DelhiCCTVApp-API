"""
        A DelhiCCTV App API built with SQLAlchemy and FastAPI
"""
# Importing all required libraries and functions
from numpy import integer
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, Float, String, Integer
import uvicorn
 

app = FastAPI(docs_url="/schemas") # Initializing the app. Default schema can now be viewed at localhost:8000/schemas


'''Setting up an sqlite3 database using SQLAlchemy connection'''

SQLALCHEMY_DATABASE_URL = 'sqlite+pysqlite:///./db.sqlite3'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

'''
    The get_db() function creates a local instance of the session in the current directory.
'''
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

'''
    A SQLAlchemny ORM IncidentFormDatabase 
'''
class IncidentFormDatabase(Base):
    __tablename__ = 'IncidentForm_DB' # This creates the metadata or the data required to explain the data entries within the database

    id = Column(Integer,primary_key=True,index=True) # The row number of an entry in the table will be its incidentID
    incidentID = Column(Integer)
    siteId = Column(Integer)
    caNumber =  Column(String(50))
    hName =  Column(String(50))
    hAddress=  Column(String(50)) 
    category=  Column(String(50))
    constituency=  Column(String(50))
    phNumber= Column(String(50))
    altPhNumber =  Column(String(50))
    description =  Column(String, nullable=True)
    service =  Column(String(50))
    status =  Column(String(50))
    priority =  Column(String(50))
    date =  Column(String(50))
    image1 = Column(String(250))
    image2 = Column(String(250))
    image3 = Column(String(250))
    image4 = Column(String(250))
    image5 = Column(String(250))

''' 
    Executing this command will issue create table SQL Queries and actually start making tables in the sqlite3 database
'''
Base.metadata.create_all(bind=engine) 

'''
    A Pydantic  Class "Incident"
    All the fields in the class will be displayed in the schema of the response model being used for the API endpoints
'''
class Incident(BaseModel):
    
    incidentID : int
    siteId: int
    caNumber: Optional[str] = None
    hName: str
    hAddress: str
    category: str
    constituency: str
    phNumber: str
    altPhNumber : str
    description : Optional[str] = None
    service : str
    status : str
    priority : str
    date : str
    image1 : str
    image2 : str
    image3 : str
    image4 : str
    image5 : str

    class Config:
        orm_mode = True


'''
    Accessibility Methods/Endpoints used within the API
'''

'''
    GET method to retrieve all incidents
    db_all_incidents is a function which takes in the current database session as input and returns all the entries present in the database.
'''
def db_all_incidents(db : Session):
    return db.query(IncidentFormDatabase).all()

@app.get("/incidents/", response_model=List[Incident])
def all_incidents(db : Session = Depends(get_db)): #Existence of this session instance to be verified by the get_db() function
    return db_all_incidents(db)


'''
    POST method to create an incident
    db_create_incident is a function that instantiates an object of class IncidentFormDatabase (incident_db) and takes in the session instance and an Incident object as input parameters. The incident_db object is converted into a parsable dictionary and then appending it to the database.
'''
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


'''
    GET method to retrieve incident based on its Incident ID
    The get_incident displays the retrieved incident with all its fields from the database.
'''
def db_get_incident(db : Session, incidentID : int):
    return db.query(IncidentFormDatabase).where(IncidentFormDatabase.incidentID == incidentID).first()

@app.get('/incident/{incidentID}')
def get_incident(incidentID: int, db: Session = Depends(get_db)):
    return db_get_incident(db, incidentID)



'''
    PUT method to update an incident based on its Incident ID
    The db_update_incident takes in the incidentID, session instance and an incident parsable dictionary created through the vars() function in the API part from the updated_incident given by the user input.
    This is then queried through SQL in the function to update the value where the incidentID is equal to the user input
'''
def db_update_incident(db : Session, incidentID: int, updated_incident : Incident, incident_dictionary):
    return db.query(IncidentFormDatabase).filter(IncidentFormDatabase.incidentID==incidentID).update(incident_dictionary)

@app.put('/incident/{incidentID}', response_model = IncidentFormDatabase)
def update_incident(updated_incident: Incident, incidentID: int, db: Session = Depends(get_db)):
    incident_dictionary = vars(updated_incident)
    db_update_incident(db, incidentID, updated_incident, incident_dictionary)
    db.commit()
    return updated_incident

@app.get('/', include_in_schema=False)
def rootText():
    return {"Message" : "Welcome to the API for the DelhiCCTV App "}

uvicorn.run(app) # by default runs the app on port 8000
