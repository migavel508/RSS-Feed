from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import logging
from .database import get_db
from .models import Feed
from .rss.scheduler import RSSScheduler
import threading
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RSS Feed API")
logger = logging.getLogger(__name__)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start the RSS scheduler in a background thread
def start_scheduler_thread():
    scheduler = RSSScheduler()
    scheduler.start()

@app.on_event("startup")
async def startup_event():
    """Start the RSS scheduler when the application starts"""
    thread = threading.Thread(target=start_scheduler_thread, daemon=True)
    thread.start()
    logger.info("RSS Feed scheduler started")

@app.get("/feeds/", response_model=List[dict])
def get_feeds(
    skip: int = 0,
    limit: int = 100,
    language: str = None,
    region: str = None,
    state: str = None,
    db: Session = Depends(get_db)
):
    """Get RSS feeds with optional filtering"""
    query = db.query(Feed)
    
    if language:
        query = query.filter(Feed.language == language)
    if region:
        query = query.filter(Feed.region == region)
    if state:
        query = query.filter(Feed.state == state)
        
    feeds = query.offset(skip).limit(limit).all()
    
    # Convert feeds to dictionaries and handle JSON fields
    return [
        {
            "id": feed.id,
            "title": feed.title,
            "description": feed.description,
            "link": feed.link,
            "published_date": feed.published_date,
            "source": feed.source,
            "language": feed.language,
            "region": feed.region,
            "state": feed.state,
            "content": feed.content,
            "author": feed.author,
            "image_urls": feed.image_urls or [],
            "keywords": feed.keywords or [],
            "summary": feed.summary,
            "extraction_success": feed.extraction_success
        }
        for feed in feeds
    ]

@app.get("/feeds/{feed_id}")
def get_feed(feed_id: int, db: Session = Depends(get_db)):
    """Get a specific feed by ID"""
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    return feed 