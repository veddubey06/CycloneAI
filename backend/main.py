from fastapi import FastAPI  # type: ignore[reportMissingImports]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[reportMissingImports]

from database.database import engine, Base
from database import models

from api.cyclone import router as cyclone_router
from api.ai import router as ai_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="CycloneAI Backend",
    description="AI-Powered Tropical Cyclone Intelligence System",
    version="1.0.0"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# ROUTERS
# ==========================================

app.include_router(cyclone_router)
app.include_router(ai_router)


# ==========================================
# ROOT
# ==========================================

@app.get("/")
def root():
    return {
        "message": "CycloneAI Backend is running",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }