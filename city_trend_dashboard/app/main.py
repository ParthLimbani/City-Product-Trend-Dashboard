from fastapi import FastAPI
from app.routes import trends
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()



app = FastAPI(title="City Trend Dashboard - Phase 1")

@app.get("/")
def root():
    return {"message": "Welcome to City-Wise Product Trend Dashboard API"}

app.include_router(trends.router, prefix="/api")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["*"] for all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

