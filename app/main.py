from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import auth, paragraphs

# Initialize FastAPI application
app = FastAPI(
    title="Backend Assignment",
    description="A lightweight backend for paragraph indexing and search",
    version="1.0.0"
)

# Configure CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API route handlers
app.include_router(auth.router)
app.include_router(paragraphs.router)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup"""
    init_db()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {"message": "Backend Assignment API", "docs": "/docs"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
