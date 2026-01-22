import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.routers import admin
from src.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic can go here (e.g. connecting to DB check)
    print("Starting MIA-Data-Service...")
    yield
    print("Shutting down MIA-Data-Service...")

app = FastAPI(
    title="MIA-Data-Service (Server C)",
    version="1.0.0",
    description="Backend for Admin Portal & Data Analytics",
    lifespan=lifespan,
)

# CORS Setup
origins = ["*"] # Adjust in production to specific frontend domains

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(admin.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "MIA-Data-Service"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
