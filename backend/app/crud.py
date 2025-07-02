from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
from typing import Optional, Dict, List
from datetime import datetime

def get_articles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    feed_id: Optional[int] = None,
    language: Optional[str] = None,
    region: Optional[str] = None,
    state: Optional[str] = None
) -> List[models.Article]:
    query = db.query(models.Article)
    
    if feed_id:
        query = query.filter(models.Article.feed_id == feed_id)
    if language:
        query = query.join(models.Feed).filter(models.Feed.language == language)
    if region:
        query = query.join(models.Feed).filter(models.Feed.region == region)
    if state:
        query = query.join(models.Feed).filter(models.Feed.state == state)
    
    return query.order_by(models.Article.published.desc()).offset(skip).limit(limit).all()

def get_article(db: Session, article_id: int) -> Optional[models.Article]:
    return db.query(models.Article).filter(models.Article.id == article_id).first()

def get_feeds(db: Session, skip: int = 0, limit: int = 100) -> List[models.Feed]:
    return db.query(models.Feed).offset(skip).limit(limit).all()

def create_feed(db: Session, name: str, url: str, language: str, region: str, state: str) -> models.Feed:
    feed = models.Feed(
        name=name,
        url=url,
        language=language,
        region=region,
        state=state
    )
    db.add(feed)
    db.commit()
    db.refresh(feed)
    return feed

def get_stats(db: Session) -> Dict:
    """Get statistics about articles and feeds"""
    stats = {
        "total_articles": db.query(func.count(models.Article.id)).scalar(),
        "total_feeds": db.query(func.count(models.Feed.id)).scalar(),
        "articles_by_language": {},
        "articles_by_region": {},
        "articles_by_state": {}
    }
    
    # Articles by language
    lang_stats = db.query(
        models.Feed.language,
        func.count(models.Article.id)
    ).join(models.Article).group_by(models.Feed.language).all()
    stats["articles_by_language"] = dict(lang_stats)
    
    # Articles by region
    region_stats = db.query(
        models.Feed.region,
        func.count(models.Article.id)
    ).join(models.Article).group_by(models.Feed.region).all()
    stats["articles_by_region"] = dict(region_stats)
    
    # Articles by state
    state_stats = db.query(
        models.Feed.state,
        func.count(models.Article.id)
    ).join(models.Article).group_by(models.Feed.state).all()
    stats["articles_by_state"] = dict(state_stats)
    
    return stats 