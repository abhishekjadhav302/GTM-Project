import os, csv, codecs, requests
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
# here i have pass my api key
EXPLORIUM_API_KEY = "6b5be667-744f-4a59-85f6-0f5000853b0c"

# i have added pooling settings to handle cloud connections better
engine = create_engine(
    DATABASE_URL, 
    pool_size=10, 
    max_overflow=20, 
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True)
    industry = Column(String, default="Processing...")
    size = Column(String, default="-")
    revenue = Column(String, default="-")

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def enrich_with_explorium(domain: str):
    db = SessionLocal()
    # here i have use the explorium endpoints
    search_url = "https://api.explorium.ai"
    headers = {"API_KEY": EXPLORIUM_API_KEY, "Content-Type": "application/json"}
    
    try:
        match_res = requests.post(search_url, headers=headers, json={"domain": domain}).json()
        biz_id = match_res.get("business_id")
        
        if biz_id:
            # Fixed the details endpoint
            enrich_url = f"https://api.explorium.ai{biz_id}"
            details = requests.get(enrich_url, headers=headers).json()
            
            company = db.query(Company).filter(Company.domain == domain).first()
            if company:
                company.industry = details.get("industry", "Unknown")
                company.size = details.get("employee_count_range", "N/A")
                company.revenue = details.get("annual_revenue_range", "N/A")
                db.commit()
    except Exception as e:
        print(f"Error enriching {domain}: {e}")
    finally:
        db.close()           # Closes connection after AI work

@app.post("/upload")
async def upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    db = SessionLocal()
    try:
        reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
        for row in reader:
            domain = row['domain']
            if not db.query(Company).filter(Company.domain == domain).first():
                new_co = Company(domain=domain)
                db.add(new_co)
                db.commit()
                background_tasks.add_task(enrich_with_explorium, domain)
        return {"message": "Batch processing started"}
    finally:
        db.close()           # Closes connection after CSV upload

@app.get("/companies")
def get_companies():
    db = SessionLocal()
    try:
        # Fixed the memory leak by ensuring the query is returned inside the try block
        return db.query(Company).all()
    finally:
        db.close()            #Closes connection after UI refreshes
