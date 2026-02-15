import os, csv, codecs, requests
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 1. Setup Environment and Database
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
EXPLORIUM_API_KEY = "6b5be667-744f-4a59-85f6-0f5000853b0c"

# Cloud-optimized connection pooling for Neon
engine = create_engine(
    DATABASE_URL, 
    pool_size=10, 
    max_overflow=20, 
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Database Schema
class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True)
    industry = Column(String, default="Processing...")
    size = Column(String, default="-")
    revenue = Column(String, default="-")

# Auto-create table in Neon Cloud
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 3. Middleware (Allow React to talk to FastAPI)
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# 4. AI Enrichment Logic
def enrich_with_explorium(domain: str):
    db = SessionLocal()
    # FIX: Correct Explorium Endpoints
    search_url = "https://api.explorium.ai"
    headers = {"API_KEY": EXPLORIUM_API_KEY, "Content-Type": "application/json"}
    
    try:
        # Match call to get business_id
        match_res = requests.post(search_url, headers=headers, json={"domain": domain}).json()
        biz_id = match_res.get("business_id")
        
        if biz_id:
            # Details call using the biz_id
            enrich_url = f"https://api.explorium.ai{biz_id}"
            details = requests.get(enrich_url, headers=headers).json()
            
            company = db.query(Company).filter(Company.domain == domain).first()
            if company:
                company.industry = details.get("industry", company.industry)
                company.size = str(details.get("employee_count_range", company.size))
                company.revenue = str(details.get("annual_revenue_range", "N/A"))
                db.commit()
    except Exception as e:
        print(f"Error enriching {domain}: {e}")
    finally:
        db.close()

# 5. API Endpoints
@app.get("/")
def home():
    return {"status": "GTM Cloud Brain Online"}

@app.post("/upload")
async def upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    db = SessionLocal()
    try:
        content = await file.read()
        decoded = content.decode('utf-8').splitlines()
        reader = csv.DictReader(decoded)
        
        # Clean whitespace from headers
        reader.fieldnames = [field.strip().lower() for field in reader.fieldnames]

        for row in reader:
            domain = row.get('domain', '').strip()
            csv_industry = row.get('industry', '').strip()
            csv_size = row.get('size', '').strip()

            if not domain:
                continue

            existing = db.query(Company).filter(Company.domain == domain).first()
            
            if existing:
                existing.industry = csv_industry if csv_industry else existing.industry
                existing.size = csv_size if csv_size else existing.size
            else:
                new_co = Company(
                    domain=domain,
                    industry=csv_industry if csv_industry else "Processing...",
                    size=csv_size if csv_size else "-"
                )
                db.add(new_co)
            
            db.commit()
            # Run AI enrichment in background
            background_tasks.add_task(enrich_with_explorium, domain)
            
        return {"message": "CSV data saved and enrichment started"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

# FIX: Added the missing /companies endpoint that was causing 404
@app.get("/companies")
def get_companies():
    db = SessionLocal()
    try:
        return db.query(Company).all()
    finally:
        db.close()

# NEW: Added a manual clear database endpoint for testing
@app.delete("/clear-database")
def clear_db():
    db = SessionLocal()
    try:
        db.query(Company).delete()
        db.commit()
        return {"message": "Database cleared"}
    finally:
        db.close()
