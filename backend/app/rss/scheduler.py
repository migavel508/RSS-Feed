import schedule
import time
import json
import logging
from pathlib import Path
from typing import Dict
from .fetcher import RSSFetcher

logger = logging.getLogger(__name__)

class RSSScheduler:
    def __init__(self, config_path: str = "feeds_config.json"):
        self.config_path = config_path
        self.fetcher = RSSFetcher()
        self.feeds_config = self._load_config()

    def _load_config(self) -> Dict:
        """Load RSS feed configuration from JSON file"""
        try:
            config_path = Path(self.config_path)
            if not config_path.is_absolute():
                # If path is relative, assume it's relative to the project root
                config_path = Path(__file__).parent.parent.parent / config_path
            
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config from {self.config_path}: {str(e)}")
            return {}

    def fetch_feeds(self) -> None:
        """Fetch all configured RSS feeds"""
        try:
            logger.info("Starting RSS feed fetch")
            self.fetcher.fetch_and_store_feeds(self.feeds_config)
            logger.info("Completed RSS feed fetch")
        except Exception as e:
            logger.error(f"Error in fetch_feeds: {str(e)}")

    def start(self, interval_minutes: int = 30) -> None:
        """Start the RSS feed scheduler"""
        logger.info(f"Starting RSS scheduler with {interval_minutes} minute interval")
        
        # Schedule the job
        schedule.every(interval_minutes).minutes.do(self.fetch_feeds)
        
        # Run immediately on start
        self.fetch_feeds()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(1) 