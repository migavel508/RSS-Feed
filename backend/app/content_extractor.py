import trafilatura
from newspaper import Article, Config
import logging
from typing import Optional, Dict, List
import requests
from datetime import datetime
import json
import time
from urllib.parse import urlparse, urlparse
import re
from bs4 import BeautifulSoup
import dateparser
import tldextract

logger = logging.getLogger(__name__)

class ContentExtractor:
    def __init__(self):
        # Configure newspaper
        self.newspaper_config = Config()
        self.newspaper_config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.newspaper_config.request_timeout = 10
        self.newspaper_config.fetch_images = True
        self.newspaper_config.keep_article_html = True
        self.newspaper_config.memoize_articles = False

        # Configure requests
        self.headers = {
            'User-Agent': self.newspaper_config.browser_user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        # Configure trafilatura
        self.trafilatura_config = {
            'include_comments': False,
            'include_tables': True,
            'include_images': True,
            'include_links': True,
            'output_format': 'json',
            'favor_precision': True,
            'include_formatting': True
        }

        # State mapping for Indian news sources
        self.state_mapping = {
            'thehindu.com': 'All',
            'timesofindia.indiatimes.com': 'All',
            'jagran.com': 'All',
            'dinamalar.com': 'Tamil Nadu',
            'dinakaran.com': 'Tamil Nadu',
            'amarujala.com': 'Uttar Pradesh',
            'bhaskar.com': 'Madhya Pradesh',
            'lokmat.com': 'Maharashtra',
            # Add more mappings as needed
        }

    def _extract_source(self, url: str) -> str:
        """Extract source name from URL"""
        try:
            ext = tldextract.extract(url)
            domain = f"{ext.domain}.{ext.suffix}"
            # Map common domains to their proper names
            source_mapping = {
                'thehindu.com': 'The Hindu',
                'timesofindia.indiatimes.com': 'Times of India',
                'jagran.com': 'Dainik Jagran',
                'dinamalar.com': 'Dinamalar',
                'dinakaran.com': 'Dinakaran',
                'amarujala.com': 'Amar Ujala',
                'bhaskar.com': 'Dainik Bhaskar',
                'lokmat.com': 'Lokmat',
                # Add more mappings as needed
            }
            return source_mapping.get(domain, domain)
        except Exception as e:
            logger.error(f"Error extracting source from URL {url}: {str(e)}")
            return urlparse(url).netloc

    def _extract_state(self, url: str, content: str = '') -> str:
        """Extract state information from URL and content"""
        try:
            # First check domain-based mapping
            domain = tldextract.extract(url).registered_domain
            if domain in self.state_mapping:
                return self.state_mapping[domain]

            # Look for state mentions in URL path
            path = urlparse(url).path.lower()
            state_keywords = {
                'tamil-nadu': 'Tamil Nadu',
                'kerala': 'Kerala',
                'karnataka': 'Karnataka',
                'andhra-pradesh': 'Andhra Pradesh',
                'maharashtra': 'Maharashtra',
                'delhi': 'Delhi',
                'uttar-pradesh': 'Uttar Pradesh',
                'west-bengal': 'West Bengal',
                # Add more state mappings
            }
            
            for keyword, state in state_keywords.items():
                if keyword in path:
                    return state

            # Default to 'All' if no specific state is found
            return 'All'
        except Exception as e:
            logger.error(f"Error extracting state from URL {url}: {str(e)}")
            return 'All'

    def _parse_date(self, date_str: str, html_content: str = None) -> Optional[str]:
        """Parse date string to ISO format with multiple fallbacks"""
        if not date_str and html_content:
            try:
                # Try to find date in meta tags
                soup = BeautifulSoup(html_content, 'lxml')
                meta_dates = soup.find_all('meta', attrs={'property': ['article:published_time', 'og:published_time', 'published_time']})
                if meta_dates:
                    date_str = meta_dates[0].get('content', '')
                else:
                    # Try to find date in schema.org metadata
                    schema = soup.find('script', type='application/ld+json')
                    if schema:
                        try:
                            data = json.loads(schema.string)
                            if isinstance(data, dict):
                                date_str = data.get('datePublished', '')
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                logger.warning(f"Error parsing date from HTML: {str(e)}")

        if date_str:
            try:
                # Use dateparser for flexible date parsing
                parsed_date = dateparser.parse(date_str)
                if parsed_date:
                    return parsed_date.isoformat()
            except Exception as e:
                logger.warning(f"Error parsing date string {date_str}: {str(e)}")

        return datetime.utcnow().isoformat()

    def _clean_text(self, text: str) -> str:
        """Clean extracted text by removing extra whitespace and normalizing line endings"""
        if not text:
            return ""
        # Replace multiple newlines with a single one
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()

    def _detect_language(self, text: str, meta_lang: str = None) -> str:
        """Detect language of the content"""
        if meta_lang:
            return meta_lang.lower()[:2]
        
        try:
            # Try to detect language from content
            from langdetect import detect
            return detect(text)
        except Exception as e:
            logger.warning(f"Language detection failed: {str(e)}")
            return 'en'  # Default to English

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text using basic NLP techniques"""
        try:
            from nltk.tokenize import word_tokenize
            from nltk.corpus import stopwords
            from nltk.tag import pos_tag
            import nltk
            
            # Download required NLTK data if not already present
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            try:
                nltk.data.find('taggers/averaged_perceptron_tagger')
            except LookupError:
                nltk.download('averaged_perceptron_tagger', quiet=True)
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords', quiet=True)

            # Tokenize and tag parts of speech
            tokens = word_tokenize(text.lower())
            tagged = pos_tag(tokens)
            
            # Get English stop words
            stop_words = set(stopwords.words('english'))
            
            # Extract nouns and adjectives that aren't stop words
            keywords = [word for word, tag in tagged 
                       if word not in stop_words 
                       and len(word) > 2
                       and tag.startswith(('NN', 'JJ'))  # Nouns and adjectives
                       and word.isalnum()]  # Only alphanumeric words
            
            # Return unique keywords
            return list(set(keywords))[:10]  # Limit to top 10 keywords
        except Exception as e:
            logger.warning(f"Keyword extraction failed: {str(e)}")
            return []

    def _retry_download(self, url: str, max_retries: int = 3, delay: int = 2) -> Optional[str]:
        """Download URL content with retries"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to download {url} after {max_retries} attempts: {str(e)}")
                    return None
                time.sleep(delay * (attempt + 1))
        return None

    def _extract_with_trafilatura(self, url: str) -> Optional[Dict]:
        """Extract content using trafilatura with enhanced error handling"""
        try:
            # Download with retries
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                downloaded = self._retry_download(url)
                if not downloaded:
                    return None

            # Extract content
            result = trafilatura.extract(downloaded, **self.trafilatura_config)
            if not result:
                return None

            try:
                if isinstance(result, str):
                    result = json.loads(result)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse trafilatura JSON result for {url}: {str(e)}")
                return None

            # Clean and process the extracted content
            text = self._clean_text(result.get('text', ''))
            source = self._extract_source(url)
            state = self._extract_state(url, text)
            
            # Get the date with fallback to HTML content
            date = self._parse_date(result.get('date', ''), downloaded)
            
            # Detect language
            language = self._detect_language(text, result.get('language'))

            return {
                'title': result.get('title', ''),
                'text': text,
                'html': result.get('raw_html', ''),
                'author': result.get('author', ''),
                'date': date,
                'source': source,
                'state': state,
                'language': language,
                'summary': result.get('description', '') or text[:200] + '...' if text else '',
                'image_urls': result.get('images', []) if isinstance(result.get('images'), list) else [],
                'extracted_by': 'trafilatura'
            }
        except Exception as e:
            logger.error(f"Trafilatura extraction failed for {url}: {str(e)}")
            return None

    def _extract_with_newspaper(self, url: str) -> Optional[Dict]:
        """Extract content using newspaper3k with enhanced error handling"""
        try:
            article = Article(url, config=self.newspaper_config)
            
            # Download with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    article.download()
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed to download article after {max_retries} attempts: {str(e)}")
                        return None
                    time.sleep(2 * (attempt + 1))

            # Parse article
            article.parse()
            
            # Clean the extracted text
            text = self._clean_text(article.text)
            
            # Extract source and state
            source = self._extract_source(url)
            state = self._extract_state(url, text)
            
            # Get the date with fallback to HTML content
            date = self._parse_date(
                article.publish_date.isoformat() if article.publish_date else '',
                article.html
            )
            
            # Detect language
            language = self._detect_language(text, article.meta_lang)
            
            # Try NLP for summary
            summary = ''
            try:
                article.nlp()
                summary = article.summary
            except Exception as e:
                logger.warning(f"NLP processing failed for {url}: {str(e)}")
                summary = text[:200] + '...' if text else ''

            return {
                'title': article.title,
                'text': text,
                'html': article.html,
                'author': ', '.join(article.authors) if article.authors else '',
                'date': date,
                'source': source,
                'state': state,
                'language': language,
                'summary': summary,
                'image_urls': [article.top_image] if article.top_image else [],
                'extracted_by': 'newspaper3k'
            }
        except Exception as e:
            logger.error(f"Newspaper3k extraction failed for {url}: {str(e)}")
            return None

    def extract_content(self, url: str) -> Dict:
        """Extract content from a URL using both trafilatura and newspaper3k"""
        start_time = time.time()
        
        # Validate URL
        try:
            parsed_url = urlparse(url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                return {
                    'url': url,
                    'extraction_time': datetime.utcnow().isoformat(),
                    'extraction_success': False,
                    'error': 'Invalid URL format'
                }
        except Exception:
            return {
                'url': url,
                'extraction_time': datetime.utcnow().isoformat(),
                'extraction_success': False,
                'error': 'Invalid URL'
            }

        # Try trafilatura first
        content = self._extract_with_trafilatura(url)
        
        # If trafilatura fails or returns minimal content, try newspaper3k
        if not content or not content.get('text'):
            logger.info(f"Trafilatura failed or returned minimal content for {url}, trying newspaper3k")
            content = self._extract_with_newspaper(url)

        # Prepare the final result
        if content and content.get('text'):
            # Add metadata
            content.update({
                'url': url,
                'extraction_time': datetime.utcnow().isoformat(),
                'extraction_success': True,
                'processing_time': round(time.time() - start_time, 2)
            })
        else:
            # Return error information if both methods fail
            content = {
                'url': url,
                'extraction_time': datetime.utcnow().isoformat(),
                'extraction_success': False,
                'error': 'Content extraction failed with both methods',
                'processing_time': round(time.time() - start_time, 2)
            }
        
        return content 