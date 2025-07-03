# RSS Feed Backend

This is the backend service for the RSS Feed aggregator. It fetches RSS feeds from various news sources and stores them in a database.

## Configuration

### RSS Feed Configuration

The RSS feeds are configured in `feeds_config.json`. Each feed entry has the following structure:

```json
{
  "feed_id": {
    "url": "RSS feed URL",
    "language": "Language code (en, hi, ta, etc.)",
    "region": "Region name",
    "state": "State name"
  }
}
```

To add a new RSS feed:
1. Open `feeds_config.json`
2. Add a new entry following the format above
3. Use a unique `feed_id` as the key
4. Provide the required fields: url, language, region, and state

Example:
```json
{
  "new_feed_name": {
    "url": "https://example.com/rss.xml",
    "language": "en",
    "region": "India",
    "state": "Karnataka"
  }
}
```

### Scheduler Configuration

The RSS feed fetcher runs on a schedule configured in `app/config.py`. The default fetch interval is set in minutes.

Current scheduling configuration:
- Fetch Interval: Every 15 minutes (configurable)
- Initial fetch happens on startup
- Runs in a background thread

To modify the fetch interval:
1. Update `FETCH_INTERVAL` in `app/config.py`
2. Restart the backend service

## Sample Output

The backend provides the following API endpoints:

1. GET `/feeds/` - Returns all fetched RSS feeds
   ```json
   {
     "feeds": [
       {
         "id": "unique_id",
         "title": "Article Title",
         "description": "Article Description",
         "link": "https://article-url.com",
         "published_date": "2024-01-01T12:00:00Z",
         "source": "feed_id",
         "language": "en",
         "region": "India",
         "state": "Maharashtra"
       }
     ]
   }
   ```

2. GET `/feeds/filter` - Returns filtered feeds based on query parameters
   - Parameters:
     - language (optional): Filter by language code
     - region (optional): Filter by region
     - state (optional): Filter by state
     - source (optional): Filter by feed source

## Setup and Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

The server will start on http://localhost:8000 