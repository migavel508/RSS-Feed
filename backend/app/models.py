from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    link = Column(String, unique=True, index=True)
    published_date = Column(DateTime)
    source = Column(String, index=True)
    language = Column(String, index=True)
    region = Column(String, index=True)
    state = Column(String, index=True)
    
    # New fields for article content
    content = Column(Text, nullable=True)
    content_html = Column(Text, nullable=True)
    author = Column(String, nullable=True)
    image_urls = Column(JSON, nullable=True)
    keywords = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    extracted_by = Column(String, nullable=True)
    extraction_time = Column(DateTime, nullable=True)
    extraction_success = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    articles = relationship("Article", back_populates="feed")

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("feeds.id"))
    title = Column(String, index=True)
    link = Column(String, unique=True, index=True)
    description = Column(Text)
    published_date = Column(DateTime)
    feed = relationship("Feed", back_populates="articles") 