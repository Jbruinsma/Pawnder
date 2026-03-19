from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

# 1. Import your database engine and Base
from .database import engine, Base, get_db

# 2. IMPORTANT: Import models so SQLAlchemy knows they exist
from . import models

# 3. Create the tables in the database
# This tells SQLAlchemy to look at everything in models.py and build it
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pawnder API - Dev")

@app.get("/")
def read_root():
    return {"message": "Pawnder API is running!", "lead": "Justin"}

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        # Verifies PostGIS is active for your geo-relevant feed [cite: 39, 42]
        result = db.execute(text("SELECT postgis_full_version();"))
        version = result.fetchone()[0]
        return {
            "status": "Connected to PostGIS",
            "version": version,
            "tables": "Models have been initialized"
        }
    except Exception as e:
        return {"status": "Error", "details": str(e)}