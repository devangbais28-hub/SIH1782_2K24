import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.routers import health, verification, admin
from app.dependencies import get_faiss_store
from app.utils.logging import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing Nirnay application...")
    Base.metadata.create_all(bind=engine)
    store = get_faiss_store()
    if store.is_healthy():
        logger.info(f"FAISS index ready with {store.vector_count()} vectors.")
    else:
        logger.warning("FAISS index is not yet built or missing. Build via build_faiss_index script.")
    yield
    # Shutdown actions
    logger.info("Nirnay application shutting down...")


app = FastAPI(
    title="Nirnay API",
    description="AI-powered publication title similarity and conflict-screening system.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(verification.router)
app.include_router(admin.router)

# Serve Frontend Static Files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"message": "Nirnay API is running. Documentation available at /docs"})


@app.get("/verify.html", include_in_schema=False)
def serve_verify():
    verify_path = os.path.join(FRONTEND_DIR, "verify.html")
    if os.path.exists(verify_path):
        return FileResponse(verify_path)
    return JSONResponse({"message": "Submission page not found."})
