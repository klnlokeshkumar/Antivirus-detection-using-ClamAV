from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import router
from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    await init_db()
    yield

app = FastAPI(
    title="ClamAV Scanner API",
    description="A minimalistic antivirus scanning API using ClamAV",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Also include some routes at root level for convenience
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "ClamAV Scanner API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "clamav-scanner"}