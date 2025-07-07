from neo4j import GraphDatabase
from typing import Dict, List, Optional
import logging
from datetime import datetime
from .config import settings

logger = logging.getLogger(__name__)

class Neo4jManager:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        """Close the Neo4j driver"""
        self.driver.close()

    def _create_constraints(self, session):
        """Create necessary constraints for the graph database"""
        constraints = [
            "CREATE CONSTRAINT feed_url IF NOT EXISTS FOR (f:Feed) REQUIRE f.url IS UNIQUE",
            "CREATE CONSTRAINT source_name IF NOT EXISTS FOR (s:Source) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT state_name IF NOT EXISTS FOR (s:State) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT language_code IF NOT EXISTS FOR (l:Language) REQUIRE l.code IS UNIQUE",
            "CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE"
        ]
        
        for constraint in constraints:
            try:
                session.run(constraint)
            except Exception as e:
                logger.warning(f"Constraint creation warning: {str(e)}")

    def init_db(self):
        """Initialize the database with constraints"""
        with self.driver.session() as session:
            self._create_constraints(session)

    def create_or_update_feed(self, feed_data: Dict):
        """Create or update a feed node and its relationships"""
        with self.driver.session() as session:
            # Create feed query
            query = """
            MERGE (f:Feed {url: $url})
            SET f.title = $title,
                f.description = $description,
                f.published_date = datetime($published_date),
                f.content = $content,
                f.summary = $summary,
                f.author = $author,
                f.updated_at = datetime($updated_at)

            MERGE (s:Source {name: $source})
            MERGE (st:State {name: $state})
            MERGE (l:Language {code: $language})

            MERGE (f)-[:PUBLISHED_BY]->(s)
            MERGE (f)-[:BELONGS_TO]->(st)
            MERGE (f)-[:WRITTEN_IN]->(l)

            WITH f

            // Create topic nodes and relationships
            UNWIND $topics AS topic
            MERGE (t:Topic {name: topic})
            MERGE (f)-[:COVERS]->(t)

            // Create keyword nodes and relationships
            UNWIND $keywords AS keyword
            MERGE (k:Keyword {name: keyword})
            MERGE (f)-[:TAGGED_WITH]->(k)

            RETURN f.url
            """

            # Extract topics from content using NLP
            topics = self._extract_topics(feed_data.get('content', ''))
            
            # Prepare parameters
            params = {
                'url': feed_data['url'],
                'title': feed_data.get('title', ''),
                'description': feed_data.get('description', ''),
                'published_date': feed_data.get('published_date', datetime.utcnow().isoformat()),
                'content': feed_data.get('content', ''),
                'summary': feed_data.get('summary', ''),
                'author': feed_data.get('author', ''),
                'source': feed_data.get('source', ''),
                'state': feed_data.get('state', 'All'),
                'language': feed_data.get('language', 'en'),
                'topics': topics,
                'keywords': feed_data.get('keywords', []),
                'updated_at': datetime.utcnow().isoformat()
            }

            try:
                result = session.run(query, params)
                return result.single()
            except Exception as e:
                logger.error(f"Error creating/updating feed in Neo4j: {str(e)}")
                return None

    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content using NLP"""
        try:
            import nltk
            from nltk.tokenize import sent_tokenize, word_tokenize
            from nltk.tag import pos_tag
            from nltk.chunk import ne_chunk
            
            # Download required NLTK data
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            try:
                nltk.data.find('taggers/averaged_perceptron_tagger')
            except LookupError:
                nltk.download('averaged_perceptron_tagger', quiet=True)
            try:
                nltk.data.find('chunkers/maxent_ne_chunker')
            except LookupError:
                nltk.download('maxent_ne_chunker', quiet=True)
            try:
                nltk.data.find('corpora/words')
            except LookupError:
                nltk.download('words', quiet=True)

            # Process the content
            sentences = sent_tokenize(content)
            topics = set()

            for sentence in sentences:
                tokens = word_tokenize(sentence)
                tagged = pos_tag(tokens)
                entities = ne_chunk(tagged)
                
                # Extract named entities
                for entity in entities:
                    if hasattr(entity, 'label'):
                        if entity.label() in ('GPE', 'ORGANIZATION', 'PERSON'):
                            topic = ' '.join([leaf[0] for leaf in entity.leaves()])
                            topics.add(topic)

            return list(topics)
        except Exception as e:
            logger.warning(f"Topic extraction failed: {str(e)}")
            return []

    def get_related_feeds(self, feed_url: str, limit: int = 5) -> List[Dict]:
        """Get related feeds based on shared topics and keywords"""
        with self.driver.session() as session:
            query = """
            MATCH (f:Feed {url: $url})-[:COVERS|TAGGED_WITH]->(t)<-[:COVERS|TAGGED_WITH]-(related:Feed)
            WHERE related.url <> f.url
            WITH related, count(distinct t) as commonTopics
            ORDER BY commonTopics DESC, related.published_date DESC
            LIMIT $limit
            MATCH (related)-[:PUBLISHED_BY]->(s:Source)
            RETURN related.url as url,
                   related.title as title,
                   related.summary as summary,
                   related.published_date as published_date,
                   s.name as source,
                   commonTopics
            """
            
            try:
                result = session.run(query, {'url': feed_url, 'limit': limit})
                return [dict(record) for record in result]
            except Exception as e:
                logger.error(f"Error getting related feeds: {str(e)}")
                return []

    def get_trending_topics(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get trending topics based on recent feeds"""
        with self.driver.session() as session:
            query = """
            MATCH (f:Feed)-[:COVERS]->(t:Topic)
            WHERE f.published_date > datetime() - duration({days: $days})
            WITH t, count(f) as frequency
            ORDER BY frequency DESC
            LIMIT $limit
            RETURN t.name as topic, frequency
            """
            
            try:
                result = session.run(query, {'days': days, 'limit': limit})
                return [dict(record) for record in result]
            except Exception as e:
                logger.error(f"Error getting trending topics: {str(e)}")
                return []

    def search_feeds(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search feeds with advanced filtering"""
        with self.driver.session() as session:
            # Build the query based on filters
            base_query = """
            MATCH (f:Feed)
            WHERE toLower(f.title) CONTAINS toLower($query) 
               OR toLower(f.content) CONTAINS toLower($query)
            """
            
            if filters:
                if filters.get('source'):
                    base_query += "\nAND EXISTS { MATCH (f)-[:PUBLISHED_BY]->(:Source {name: $source}) }"
                if filters.get('state'):
                    base_query += "\nAND EXISTS { MATCH (f)-[:BELONGS_TO]->(:State {name: $state}) }"
                if filters.get('language'):
                    base_query += "\nAND EXISTS { MATCH (f)-[:WRITTEN_IN]->(:Language {code: $language}) }"
                if filters.get('date_from'):
                    base_query += "\nAND f.published_date >= datetime($date_from)"
                if filters.get('date_to'):
                    base_query += "\nAND f.published_date <= datetime($date_to)"

            base_query += """
            MATCH (f)-[:PUBLISHED_BY]->(s:Source)
            RETURN f.url as url,
                   f.title as title,
                   f.summary as summary,
                   f.published_date as published_date,
                   s.name as source
            ORDER BY f.published_date DESC
            LIMIT 100
            """

            try:
                params = {'query': query}
                if filters:
                    params.update(filters)
                result = session.run(base_query, params)
                return [dict(record) for record in result]
            except Exception as e:
                logger.error(f"Error searching feeds: {str(e)}")
                return []

    def get_feed_stats(self) -> Dict:
        """Get statistics about feeds"""
        with self.driver.session() as session:
            query = """
            MATCH (f:Feed)
            OPTIONAL MATCH (f)-[:PUBLISHED_BY]->(s:Source)
            OPTIONAL MATCH (f)-[:BELONGS_TO]->(st:State)
            OPTIONAL MATCH (f)-[:WRITTEN_IN]->(l:Language)
            RETURN count(distinct f) as total_feeds,
                   count(distinct s) as total_sources,
                   count(distinct st) as total_states,
                   count(distinct l) as total_languages,
                   max(f.published_date) as latest_feed_date
            """
            
            try:
                result = session.run(query)
                return dict(result.single())
            except Exception as e:
                logger.error(f"Error getting feed stats: {str(e)}")
                return {} 