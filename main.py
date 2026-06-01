import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from routers import auth_router

load_dotenv()

# Create all DB if not present
Base.metadata.create_all(bind=engine)

Path("uploads/avatars").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Philix API", description="Backend", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_router.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Philix API is running", "docs": "/docs"}
