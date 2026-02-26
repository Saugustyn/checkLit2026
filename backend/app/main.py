from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import analysis

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="checkLit API",
    description="Platforma do analizy autentyczności i stylu tekstów literackich",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/api", tags=["analysis"])


@app.get("/")
def root():
    return {"message": "checkLit API działa!", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
