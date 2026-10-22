from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routes import router
from app.core.config import settings
from app.db import engine
from app.storage import storage

@asynccontextmanager
async def lifespan(_: FastAPI):
    # Schema changes are intentionally handled by the one-shot migration service,
    # not independently by every API replica.
    await storage.ensure_bucket()
    yield
    await engine.dispose()

app = FastAPI(title="Catalog API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api/v1")

@app.get("/health/live", tags=["health"])
async def live():
    return {"status": "ok"}

@app.get("/health/ready", tags=["health"])
async def ready():
    from sqlalchemy import text
    from app.db import async_session
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not_ready"})