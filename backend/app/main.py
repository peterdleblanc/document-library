"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import auth, documents

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(documents.router, prefix=f"{settings.API_V1_PREFIX}/documents", tags=["Documents"])


@app.on_event("startup")
async def startup_event():
    """Actions to perform on application startup"""
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    # Initialize database connection pool
    # Initialize MinIO client
    # Initialize Meilisearch client
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """Actions to perform on application shutdown"""
    print(f"Shutting down {settings.APP_NAME}")
    # Close database connections
    # Close other connections
    pass
