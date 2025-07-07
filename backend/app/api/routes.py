from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from ..graph_db import Neo4jManager
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter()
neo4j = Neo4jManager()

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

@router.get("/feeds/related/{feed_url}")
async def get_related_feeds(
    feed_url: str,
    limit: int = Query(default=5, ge=1, le=20)
) -> List[Dict]:
    """Get related feeds based on shared topics and keywords"""
    try:
        return neo4j.get_related_feeds(feed_url, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feeds/trending")
async def get_trending_topics(
    days: int = Query(default=7, ge=1, le=30),
    limit: int = Query(default=10, ge=1, le=50)
) -> List[Dict]:
    """Get trending topics from recent feeds"""
    try:
        return neo4j.get_trending_topics(days, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feeds/search")
async def search_feeds(
    query: str,
    source: Optional[str] = None,
    state: Optional[str] = None,
    language: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> List[Dict]:
    """Search feeds with advanced filtering"""
    try:
        filters = {}
        if source:
            filters['source'] = source
        if state:
            filters['state'] = state
        if language:
            filters['language'] = language
        if date_from:
            filters['date_from'] = date_from
        if date_to:
            filters['date_to'] = date_to
            
        return neo4j.search_feeds(query, filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feeds/stats")
async def get_feed_stats() -> Dict:
    """Get statistics about feeds"""
    try:
        return neo4j.get_feed_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update the existing feed endpoints to also store in Neo4j
@router.get("/feeds/")
def get_feeds(
    skip: int = 0,
    limit: int = 100,
    language: Optional[str] = None,
    region: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get RSS feeds with optional filtering"""
    from ..models import Feed  # Import here to avoid circular imports
    
    query = db.query(Feed)
    
    if language:
        query = query.filter(Feed.language == language)
    if region:
        query = query.filter(Feed.region == region)
    if state:
        query = query.filter(Feed.state == state)
        
    feeds = query.offset(skip).limit(limit).all()
    
    # Convert feeds to dictionaries and handle JSON fields
    feed_list = []
    for feed in feeds:
        feed_dict = {
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
        feed_list.append(feed_dict)
        
        # Store in Neo4j asynchronously
        try:
            neo4j.create_or_update_feed(feed_dict)
        except Exception as e:
            logger.warning(f"Failed to store feed in Neo4j: {str(e)}")
    
    return feed_list

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