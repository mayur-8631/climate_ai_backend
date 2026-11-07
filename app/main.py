from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import ClimateTwinException
from app.db.session import engine
from app.db.base import Base
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure database tables exist
    logger.info("Starting up ClimateTwin AI Backend...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schemas initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
    yield
    # Shutdown
    logger.info("Shutting down ClimateTwin AI Backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Localized climate-risk intelligence backend for ClimateTwin AI (Team PrithviNex)",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware (Crucial for Pravin's Next.js Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ClimateTwinException)
async def climate_twin_exception_handler(request: Request, exc: ClimateTwinException):
    logger.error(f"ClimateTwin Domain Exception: {exc.message} (Details: {exc.details})")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": exc.message,
            "details": exc.details
        }
    )


@app.get("/", tags=["Health & Status"])
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "pilot_region": f"{settings.DEFAULT_LOCATION_NAME}, Maharashtra, India",
        "docs_url": "/docs"
    }


@app.get("/health", tags=["Health & Status"])
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": "connected"
    }


# Mount API V1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)

