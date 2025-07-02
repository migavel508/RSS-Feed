import schedule
import time
import threading
from .fetcher import fetch_all_feeds
from ..config import settings
import logging

logger = logging.getLogger(__name__)

def start_scheduler():
    """Start the RSS feed scheduler in a background thread"""
    def run_scheduler():
        schedule.every(settings.FETCH_INTERVAL).minutes.do(fetch_all_feeds)
        
        # Initial fetch
        fetch_all_feeds()
        
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    logger.info(f"RSS Feed scheduler started. Running every {settings.FETCH_INTERVAL} minutes.") 