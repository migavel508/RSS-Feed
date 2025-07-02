import feedparser
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Feed, Article
from ..database import SessionLocal
from ..config import load_feed_config
import logging
from typing import List, Dict
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

def parse_date(date_str: str) -> datetime:
    try:
        return date_parser.parse(date_str)
    except:
        return datetime.utcnow()

def fetch_feed(feed: Feed) -> List[Dict]:
    """Fetch articles from a single feed"""
    try:
        parsed = feedparser.parse(feed.url)
        articles = []
        
        for entry in parsed.entries:
            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": parse_date(entry.get("published", "")),
                "feed_id": feed.id
            })
        
        return articles
    except Exception as e:
        logger.error(f"Error fetching feed {feed.url}: {str(e)}")
        return []

def sync_feeds_from_config(db: Session):
    """Sync feeds from config file to database"""
    config = load_feed_config()
    
    for name, data in config.items():
        existing = db.query(Feed).filter(Feed.name == name).first()
        if not existing:
            feed = Feed(
                name=name,
                url=data["url"],
                language=data.get("language", "Unknown"),
                region=data.get("region", "Unknown"),
                state=data.get("state", "Unknown")
            )
            db.add(feed)
            db.commit()
            db.refresh(feed)

def fetch_all_feeds():
    """Fetch all feeds and store new articles"""
    db = SessionLocal()
    try:
        # First sync feeds from config
        sync_feeds_from_config(db)
        
        feeds = db.query(Feed).all()
        for feed in feeds:
            articles = fetch_feed(feed)
            for article_data in articles:
                # Check if article already exists
                exists = db.query(Article).filter(
                    Article.link == article_data["link"]
                ).first()
                
                if not exists:
                    article = Article(
                        **article_data,
                        created_at=datetime.utcnow()
                    )
                    db.add(article)
            
            db.commit()
            
    except Exception as e:
        logger.error(f"Error in fetch_all_feeds: {str(e)}")
        db.rollback()
    finally:
        db.close() 