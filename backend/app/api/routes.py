from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, models
from ..database import get_db
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class FeedCreate(BaseModel):
    name: str
    url: str
    language: str
    region: str
    state: str

class Feed(FeedCreate):
    id: int
    
    class Config:
        from_attributes = True

class Article(BaseModel):
    id: int
    title: str
    link: str
    summary: str
    published: datetime
    feed: Feed
    
    class Config:
        from_attributes = True

@router.get("/articles", response_model=List[Article])
def list_articles(
    skip: int = 0,
    limit: int = 100,
    feed_id: Optional[int] = None,
    language: Optional[str] = None,
    region: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of articles with optional filters
    """
    articles = crud.get_articles(
        db,
        skip=skip,
        limit=limit,
        feed_id=feed_id,
        language=language,
        region=region,
        state=state
    )
    return articles

@router.get("/articles/{article_id}", response_model=Article)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """
    Get a specific article by ID
    """
    article = crud.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.get("/feeds", response_model=List[Feed])
def list_feeds(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of all monitored feeds
    """
    return crud.get_feeds(db, skip=skip, limit=limit)

@router.post("/feeds", response_model=Feed)
def create_feed(feed: FeedCreate, db: Session = Depends(get_db)):
    """
    Add a new feed to monitor
    """
    return crud.create_feed(
        db,
        name=feed.name,
        url=feed.url,
        language=feed.language,
        region=feed.region,
        state=feed.state
    )

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    Get statistics about articles and feeds
    """
    return crud.get_stats(db) 