import feedparser
from datetime import datetime
from typing import Dict, List, Optional
import json
import logging
from dateutil import parser as date_parser
from ..content_extractor import ContentExtractor
from ..database import SessionLocal
from ..models import Feed, Article
from sqlalchemy.orm import Session
from sqlalchemy import exists

logger = logging.getLogger(__name__)

class RSSFetcher:
    def __init__(self):
        self.content_extractor = ContentExtractor()
        
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        try:
            if not date_str:
                return None
            return date_parser.parse(date_str)
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {str(e)}")
            return None

    def fetch_and_store_feeds(self, feeds_config: Dict) -> None:
        """Fetch RSS feeds and store in database"""
        db = SessionLocal()
        try:
            for feed_id, config in feeds_config.items():
                self._process_feed(db, feed_id, config)
        finally:
            db.close()

    def _process_feed(self, db: Session, feed_id: str, config: Dict) -> None:
        """Process a single RSS feed"""
        try:
            feed_data = feedparser.parse(config['url'])
            
            for entry in feed_data.entries:
                if not self._entry_exists(db, entry.link):
                    try:
                        # Extract full content from the article URL
                        content_data = self.content_extractor.extract_content(entry.link)
                        
                        # Create feed entry
                        feed = Feed(
                            title=entry.get('title', ''),
                            description=entry.get('description', ''),
                            link=entry.get('link', ''),
                            published_date=self.parse_date(entry.get('published', '')),
                            source=feed_id,
                            language=config.get('language'),
                            region=config.get('region'),
                            state=config.get('state')
                        )

                        # Add content extraction data if available
                        if content_data and content_data.get('extraction_success'):
                            feed.content = content_data.get('text', '')
                            feed.content_html = content_data.get('html', '')
                            feed.author = content_data.get('author', '')
                            feed.image_urls = content_data.get('image_urls', [])
                            feed.keywords = content_data.get('keywords', [])
                            feed.summary = content_data.get('summary', '')
                            feed.extracted_by = content_data.get('extracted_by', '')
                            feed.extraction_time = (
                                datetime.fromisoformat(content_data['extraction_time'].replace('Z', '+00:00'))
                                if content_data.get('extraction_time')
                                else datetime.utcnow()
                            )
                            feed.extraction_success = True
                        
                        db.add(feed)
                        db.commit()
                        logger.info(f"Stored new feed entry: {entry.get('title', 'Untitled')}")
                    except Exception as e:
                        logger.error(f"Error processing entry {entry.get('link', 'unknown')}: {str(e)}")
                        db.rollback()
                        continue
                
        except Exception as e:
            logger.error(f"Error processing feed {feed_id}: {str(e)}")
            db.rollback()

    def _entry_exists(self, db: Session, link: str) -> bool:
        """Check if an entry already exists in the database"""
        return db.query(exists().where(Feed.link == link)).scalar() 