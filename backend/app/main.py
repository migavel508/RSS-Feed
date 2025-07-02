from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import routes
from .database import engine
from . import models
from .rss.scheduler import start_scheduler

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="RSS Feed API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(routes.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Start the RSS feed scheduler when the app starts"""
    start_scheduler()

@app.get("/")
async def root():
    return {"message": "RSS Feed API is running"} 