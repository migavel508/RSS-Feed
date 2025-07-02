from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    url = Column(String(1024), unique=True)
    language = Column(String(50))
    region = Column(String(100))
    state = Column(String(100))
    articles = relationship("Article", back_populates="feed")

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("feeds.id"))
    title = Column(String(512))
    link = Column(String(1024), unique=True, index=True)
    summary = Column(Text)
    published = Column(DateTime)
    created_at = Column(DateTime)
    
    feed = relationship("Feed", back_populates="articles") 