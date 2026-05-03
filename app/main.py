from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.redis import get_redis, close_redis
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up Redis connection
    await get_redis()
    yield
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for KnowAI — deep ML learning platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok"}
