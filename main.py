from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
# import models
# import schemas
# import crud
# from database import engine, get_db

# # Create database tables
# models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Electricity Power Monitoring API",
    description="API for monitoring electricity power consumption",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== Health Check ==============

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "message": "Electricity Power Monitoring API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """API health check"""
    return {"status": "healthy"}

# ============== Power Reading Endpoints ==============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)