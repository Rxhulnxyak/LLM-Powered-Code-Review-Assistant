from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config import get_settings
from api import health
from models.database import Base, get_engine
from utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)

engine = get_engine(settings.DATABASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting CodeSentinel backend...")

    # Initialize database
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    # Initialize analyzers and scanners
    # app.state.static_analyzer = setup_static_analyzer()
    # app.state.security_scanner = VulnerabilityScanner()
    # app.state.llm_reviewer = LLMReviewer()
    # logger.info("Analyzers loaded")

    yield

    logger.info("Shutting down CodeSentinel...")

app = FastAPI(
    title="CodeSentinel API",
    description="LLM-Powered Code Review Assistant",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routes
app.include_router(health.router, prefix="/health", tags=["health"])
# app.include_router(review.router, prefix="/api/review", tags=["review"])
# app.include_router(github.router, prefix="/api/github", tags=["github"])
# app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
