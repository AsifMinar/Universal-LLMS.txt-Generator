#!/usr/bin/env python3
"""
Universal LLMs.txt Generator
A Python tool to automatically generate and maintain llms.txt files for any website
With automatic sitemap.xml and robots.txt updates!

Version: 1.0.0
Author: AsifMinar
Updated: 2025-06-06
License: MIT
"""

import os
import json
import yaml
import datetime
import shutil
import signal
import sys
import time
import re
import hashlib
import logging
import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse, quote
import xml.etree.ElementTree as ET

# Import required packages with error handling
try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
except ImportError:
    print("❌ Missing required package: requests")
    print("Install with: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Missing required package: beautifulsoup4")
    print("Install with: pip install beautifulsoup4")
    sys.exit(1)

try:
    import frontmatter
except ImportError:
    print("❌ Missing required package: python-frontmatter")
    print("Install with: pip install python-frontmatter")
    sys.exit(1)

# Setup enhanced logging
def setup_logging(level='INFO', log_file=None, format_str=None):
    """Setup enhanced logging configuration"""
    if format_str is None:
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout),
            *([] if log_file is None else [logging.FileHandler(log_file)])
        ]
    )
    
    # Suppress verbose third-party logs
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

logger = setup_logging()

# Version information
__version__ = "1.0.0"
__author__ = "AsifMinar"
__email__ = "asifminar7@gmail.com"
__license__ = "MIT"


@dataclass
class ContentItem:
    """Represents a single content item for llms.txt"""
    title: str
    url: str
    content_type: str  # 'article', 'page', 'documentation', etc.
    description: Optional[str] = None
    last_modified: Optional[str] = None
    tags: Optional[List[str]] = None
    word_count: Optional[int] = None
    author: Optional[str] = None
    language: Optional[str] = None
    reading_time: Optional[int] = None
    
    def to_llms_format(self) -> str:
        """Convert to llms.txt format"""
        lines = [f"# {self.title}"]
        lines.append(f"URL: {self.url}")
        lines.append(f"Type: {self.content_type}")
        
        if self.description:
            # Clean and truncate description
            clean_desc = re.sub(r'<[^>]+>', '', self.description).strip()
            if len(clean_desc) > 300:
                clean_desc = clean_desc[:300] + '...'
            lines.append(f"Description: {clean_desc}")
            
        if self.last_modified:
            lines.append(f"Last Modified: {self.last_modified}")
        if self.author:
            lines.append(f"Author: {self.author}")
        if self.language:
            lines.append(f"Language: {self.language}")
        if self.tags:
            lines.append(f"Tags: {', '.join(self.tags[:10])}")  # Limit to 10 tags
        if self.word_count:
            lines.append(f"Word Count: {self.word_count}")
        if self.reading_time:
            lines.append(f"Reading Time: {self.reading_time} minutes")
            
        lines.append("")  # Empty line separator
        return "\n".join(lines)
    
    def calculate_reading_time(self) -> int:
        """Calculate reading time based on word count (250 words per minute)"""
        if self.word_count:
            return max(1, round(self.word_count / 250))
        return 0


class ContentExtractor(ABC):
    """Abstract base class for content extractors"""
    
    def __init__(self):
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            'User-Agent': f'LLMs.txt Generator {__version__} (https://github.com/AsifMinar/Universal-LLMS.txt-Generator)'
        })
        return session
    
    @abstractmethod
    def extract_content(self, config: Dict) -> List[ContentItem]:
        """Extract content items from the source"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this extractor"""
        pass
    
    def validate_config(self, config: Dict) -> bool:
        """Validate configuration for this extractor"""
        return True
    
    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content and extract text"""
        if not html_content:
            return ""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean whitespace
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return ' '.join(chunk for chunk in chunks if chunk)
        except Exception as e:
            logger.warning(f"Error cleaning HTML: {e}")
            return re.sub(r'<[^>]+>', '', html_content)
    
    def _detect_language(self, text: str) -> Optional[str]:
        """Simple language detection"""
        if not text:
            return None
        
        # Simple heuristic - count common English words
        english_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return None
        
        english_count = sum(1 for word in words[:100] if word in english_words)
        if english_count / min(len(words), 100) > 0.1:
            return 'en'
        
        return None


class WordPressExtractor(ContentExtractor):
    """Extract content from WordPress sites via REST API"""
    
    def get_name(self) -> str:
        return "wordpress"
    
    def validate_config(self, config: Dict) -> bool:
        if 'site_url' not in config:
            logger.error("WordPress extractor requires 'site_url' in config")
            return False
        return True
    
    def extract_content(self, config: Dict) -> List[ContentItem]:
        items = []
        site_url = config['site_url'].rstrip('/')
        wp_config = config.get('wordpress', {})
        
        # Auto-detect API URL if not provided
        api_url = wp_config.get('api_url', 'auto')
        if api_url == 'auto':
            api_url = f"{site_url}/wp-json/wp/v2"
        
        per_page = min(wp_config.get('per_page', 100), 100)  # WordPress API limit
        post_types = wp_config.get('post_types', ['posts', 'pages'])
        exclude_categories = wp_config.get('exclude_categories', [])
        
        # Fetch categories to get IDs for exclusion
        excluded_category_ids = []
        if exclude_categories:
            try:
                categories_response = self.session.get(f"{api_url}/categories", timeout=30)
                if categories_response.status_code == 200:
                    categories = categories_response.json()
                    excluded_category_ids = [
                        cat['id'] for cat in categories 
                        if cat['slug'] in exclude_categories or cat['name'].lower() in [ec.lower() for ec in exclude_categories]
                    ]
            except Exception as e:
                logger.warning(f"Could not fetch categories: {e}")
        
        for post_type in post_types:
            try:
                page = 1
                while True:
                    params = {
                        'per_page': per_page,
                        'page': page,
                        'status': 'publish',
                        '_embed': True,
                        'orderby': 'modified',
                        'order': 'desc'
                    }
                    
                    # Add category exclusion
                    if excluded_category_ids:
                        params['categories_exclude'] = ','.join(map(str, excluded_category_ids))
                    
                    endpoint = f"{api_url}/{post_type}"
                    logger.info(f"Fetching {post_type} page {page} from WordPress API...")
                    
                    response = self.session.get(endpoint, params=params, timeout=30)
                    response.raise_for_status()
                    
                    posts = response.json()
                    if not posts:
                        break
                    
                    for post in posts:
                        try:
                            item = self._process_wordpress_post(post, post_type)
                            if item:
                                items.append(item)
                        except Exception as e:
                            logger.warning(f"Error processing post {post.get('id', 'unknown')}: {e}")
                    
                    # Check if there are more pages
                    total_pages = int(response.headers.get('X-WP-TotalPages', 1))
                    if page >= total_pages:
                        break
                    
                    page += 1
                    time.sleep(0.1)  # Rate limiting
                    
            except Exception as e:
                logger.error(f"Error extracting WordPress {post_type}: {e}")
        
        logger.info(f"Extracted {len(items)} items from WordPress")
        return items
    
    def _process_wordpress_post(self, post: Dict, post_type: str) -> Optional[ContentItem]:
        """Process a single WordPress post"""
        try:
            # Extract basic information
            title = self._clean_html(post['title']['rendered'])
            if not title:
                return None
            
            url = post['link']
            
            # Extract and clean content
            content_html = post.get('content', {}).get('rendered', '')
            content_text = self._clean_html(content_html)
            word_count = len(content_text.split()) if content_text else 0
            
            # Extract description from excerpt or content
            description = None
            if post.get('excerpt', {}).get('rendered'):
                description = self._clean_html(post['excerpt']['rendered'])
            elif content_text:
                description = content_text[:300] + '...' if len(content_text) > 300 else content_text
            
            # Extract author
            author = None
            if '_embedded' in post and 'author' in post['_embedded']:
                author_data = post['_embedded']['author'][0]
                author = author_data.get('name') or author_data.get('display_name')
            
            # Extract tags and categories
            tags = []
            if '_embedded' in post and 'wp:term' in post['_embedded']:
                for term_group in post['_embedded']['wp:term']:
                    for term in term_group:
                        if term.get('taxonomy') in ['post_tag', 'category']:
                            tags.append(term.get('name'))
            
            # Detect language
            language = self._detect_language(content_text)
            
            item = ContentItem(
                title=title,
                url=url,
                content_type='article' if post_type == 'posts' else 'page',
                description=description,
                last_modified=post.get('modified'),
                author=author,
                tags=tags if tags else None,
                word_count=word_count,
                language=language
            )
            
            # Calculate reading time
            item.reading_time = item.calculate_reading_time()
            
            return item
            
        except Exception as e:
            logger.warning(f"Error processing WordPress post: {e}")
            return None


class StaticSiteExtractor(ContentExtractor):
    """Extract content from static sites (markdown files, etc.)"""
    
    def get_name(self) -> str:
        return "static"
    
    def validate_config(self, config: Dict) -> bool:
        static_config = config.get('static', {})
        content_dir = static_config.get('content_directory', './content')
        if not Path(content_dir).exists():
            logger.error(f"Content directory not found: {content_dir}")
            return False
        return True
    
    def extract_content(self, config: Dict) -> List[ContentItem]:
        items = []
        static_config = config.get('static', {})
        content_dir = Path(static_config.get('content_directory', './content'))
        base_url = config['site_url']
        file_patterns = static_config.get('file_patterns', ['*.md', '*.html'])
        exclude_patterns = static_config.get('exclude_patterns', [])
        
        if not content_dir.exists():
            logger.warning(f"Content directory not found: {content_dir}")
            return items
        
        # Find all matching files
        all_files = []
        for pattern in file_patterns:
            all_files.extend(content_dir.rglob(pattern))
        
        logger.info(f"Found {len(all_files)} files to process")
        
        # Process files with threading for better performance
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(self._process_static_file, file_path, content_dir, base_url, exclude_patterns): file_path 
                for file_path in all_files
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    item = future.result()
                    if item:
                        items.append(item)
                except Exception as e:
                    logger.warning(f"Error processing {file_path}: {e}")
        
        logger.info(f"Extracted {len(items)} items from static site")
        return items
    
    def _process_static_file(self, file_path: Path, content_dir: Path, base_url: str, exclude_patterns: List[str]) -> Optional[ContentItem]:
        """Process a single static file"""
        try:
            # Check exclude patterns
            for exclude_pattern in exclude_patterns:
                if file_path.match(exclude_pattern):
                    return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Parse frontmatter if present
            post = frontmatter.loads(file_content)
            content = post.content
            metadata = post.metadata
            
            # Extract title
            title = metadata.get('title')
            if not title:
                # Try to extract from first h1
                h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if h1_match:
                    title = h1_match.group(1).strip()
                else:
                    title = file_path.stem.replace('-', ' ').replace('_', ' ').title()
            
            # Skip if title is empty
            if not title:
                return None
            
            # Extract other metadata
            description = metadata.get('description') or metadata.get('excerpt')
            tags = metadata.get('tags') or metadata.get('categories')
            author = metadata.get('author')
            language = metadata.get('language') or metadata.get('lang')
            
            # Clean content and calculate word count
            clean_content = self._clean_html(content) if file_path.suffix == '.html' else content
            clean_content = re.sub(r'!\[.*?\]\(.*?\)', '', clean_content)  # Remove markdown images
            clean_content = re.sub(r'\[.*?\]\(.*?\)', '', clean_content)   # Remove markdown links
            word_count = len(clean_content.split())
            
            # Skip if below minimum word count
            min_word_count = 50  # Can be made configurable
            if word_count < min_word_count:
                return None
            
            # Generate URL
            rel_path = file_path.relative_to(content_dir)
            url_path = str(rel_path).replace('.md', '.html').replace('.markdown', '.html')
            url = urljoin(base_url, url_path)
            
            # Auto-generate description if not provided
            if not description and clean_content:
                sentences = re.split(r'[.!?]+', clean_content)
                if sentences:
                    description = sentences[0].strip()[:200]
                    if len(description) < len(sentences[0].strip()):
                        description += '...'
            
            # Detect language if not provided
            if not language:
                language = self._detect_language(clean_content)
            
            # Ensure tags is a list
            if tags and not isinstance(tags, list):
                tags = [tags] if isinstance(tags, str) else list(tags)
            
            item = ContentItem(
                title=title,
                url=url,
                content_type=metadata.get('type', 'article'),
                description=description,
                author=author,
                last_modified=datetime.datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).isoformat(),
                tags=tags,
                word_count=word_count,
                language=language
            )
            
            # Calculate reading time
            item.reading_time = item.calculate_reading_time()
            
            return item
            
        except Exception as e:
            logger.warning(f"Error processing file {file_path}: {e}")
            return None


class SitemapExtractor(ContentExtractor):
    """Extract content from sitemap.xml - works with any website"""
    
    def get_name(self) -> str:
        return "sitemap"
    
    def extract_content(self, config: Dict) -> List[ContentItem]:
        items = []
        site_url = config['site_url'].rstrip('/')
        sitemap_config = config.get('sitemap', {})
        sitemap_url = sitemap_config.get('url', 'auto')
        
        if sitemap_url == 'auto':
            sitemap_url = f"{site_url}/sitemap.xml"
        
        max_urls = sitemap_config.get('max_urls', 10000)
        timeout = sitemap_config.get('timeout', 30)
        
        try:
            logger.info(f"Fetching sitemap from: {sitemap_url}")
            response = self.session.get(sitemap_url, timeout=timeout)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            # Handle different sitemap formats
            namespaces = {
                'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                'news': 'http://www.google.com/schemas/sitemap-news/0.9',
                'image': 'http://www.google.com/schemas/sitemap-image/1.1'
            }
            
            # Check if this is a sitemap index
            if root.tag.endswith('sitemapindex'):
                logger.info("Processing sitemap index...")
                items = self._process_sitemap_index(root, namespaces, max_urls, timeout)
            else:
                logger.info("Processing single sitemap...")
                items = self._extract_from_urlset(root, namespaces, max_urls)
                    
        except Exception as e:
            logger.error(f"Error extracting from sitemap: {e}")
            
        logger.info(f"Extracted {len(items)} items from sitemap")
        return items
    
    def _process_sitemap_index(self, root: ET.Element, namespaces: Dict, max_urls: int, timeout: int) -> List[ContentItem]:
        """Process sitemap index file"""
        items = []
        processed_urls = 0
        
        for sitemap_elem in root.findall('ns:sitemap', namespaces):
            if processed_urls >= max_urls:
                break
                
            loc = sitemap_elem.find('ns:loc', namespaces)
            if loc is not None:
                sub_sitemap_url = loc.text
                try:
                    logger.info(f"Processing sub-sitemap: {sub_sitemap_url}")
                    sub_response = self.session.get(sub_sitemap_url, timeout=timeout)
                    sub_response.raise_for_status()
                    sub_root = ET.fromstring(sub_response.content)
                    
                    remaining_urls = max_urls - processed_urls
                    sub_items = self._extract_from_urlset(sub_root, namespaces, remaining_urls)
                    items.extend(sub_items)
                    processed_urls += len(sub_items)
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Error processing sub-sitemap {sub_sitemap_url}: {e}")
        
        return items
    
    def _extract_from_urlset(self, root: ET.Element, namespaces: Dict, max_urls: int) -> List[ContentItem]:
        """Extract items from a urlset element"""
        items = []
        processed = 0
        
        for url_elem in root.findall('ns:url', namespaces):
            if processed >= max_urls:
                break
                
            loc = url_elem.find('ns:loc', namespaces)
            lastmod = url_elem.find('ns:lastmod', namespaces)
            
            if loc is not None:
                url = loc.text
                
                # Skip non-content URLs
                skip_patterns = [
                    '/admin', '/api', '/wp-admin', '/wp-content', '/wp-includes',
                    '.xml', '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg',
                    '/feed', '/rss', '/sitemap', '/robots.txt'
                ]
                
                if any(skip in url.lower() for skip in skip_patterns):
                    continue
                
                # Extract title from URL path
                path = urlparse(url).path.strip('/')
                if path:
                    # Convert URL path to title
                    title_parts = path.split('/')[-1].split('-')
                    title = ' '.join(word.capitalize() for word in title_parts if word)
                    if not title or title.lower() in ['index', 'home', 'default']:
                        title = "Home Page"
                else:
                    title = "Home Page"
                
                # Determine content type based on URL
                content_type = 'page'
                blog_indicators = ['/blog/', '/post/', '/article/', '/news/', '/press/']
                if any(indicator in url.lower() for indicator in blog_indicators):
                    content_type = 'article'
                
                item = ContentItem(
                    title=title,
                    url=url,
                    content_type=content_type,
                    last_modified=lastmod.text if lastmod is not None else None
                )
                items.append(item)
                processed += 1
        
        return items


class LLMsTxtGenerator:
    """Main class for generating llms.txt files"""
    
    def __init__(self, config_path: str = "llms_config.yaml", config_dict: Optional[Dict] = None):
        self.config_path = config_path
        self.config = config_dict or self.load_config()
        self.extractors = {
            'wordpress': WordPressExtractor(),
            'static': StaticSiteExtractor(),
            'sitemap': SitemapExtractor(),
        }
        
        # Setup logging from config
        log_config = self.config.get('logging', {})
        self.logger = setup_logging(
            level=log_config.get('level', 'INFO'),
            log_file=log_config.get('file'),
            format_str=log_config.get('format')
        )
        
    def register_extractor(self, name: str, extractor: ContentExtractor):
        """Register a custom extractor"""
        self.extractors[name] = extractor
        
    def load_config(self) -> Dict:
        """Load configuration from file"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            return self.create_default_config()
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            # Validate and set defaults
            return self._validate_and_set_defaults(config)
            
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self.create_default_config()
    
    def _validate_and_set_defaults(self, config: Dict) -> Dict:
        """Validate configuration and set defaults"""
        defaults = {
            'site_url': 'https://example.com',
            'site_name': 'My Website',
            'description': 'A website with great content',
            'contact_email': 'contact@example.com',
            'extractor': 'sitemap',
            'output_path': './llms.txt',
            'auto_update': True,
            'auto_update_sitemap': True,
            'auto_update_robots': True,
            'backup_files': True,
            'max_items': 1000,
            'min_word_count': 50,
            'include_drafts': False,
            'cache_file': '.llms_cache.json',
            'cache_duration': 3600,
            'include_patterns': ['*.html', '*.md'],
            'exclude_patterns': ['admin/*', 'private/*', 'draft/*'],
        }
        
        # Merge with defaults
        for key, value in defaults.items():
            if key not in config:
                config[key] = value
        
        return config
    
    def create_default_config(self) -> Dict:
        """Create default configuration"""
        default_config = {
            'site_url': 'https://example.com',
            'site_name': 'My Website',
            'description': 'A website with great content for AI and language models',
            'contact_email': 'contact@example.com',
            'extractor': 'sitemap',
            'output_path': './llms.txt',
            'auto_update': True,
            'auto_update_sitemap': True,
            'auto_update_robots': True,
            'backup_files': True,
            'max_items': 1000,
            'min_word_count': 50,
            'include_drafts': False,
            'cache_file': '.llms_cache.json',
            'cache_duration': 3600,
            'include_patterns': ['*.html', '*.md'],
            'exclude_patterns': ['admin/*', 'private/*', 'draft/*'],
            
            # Extractor-specific configs
            'wordpress': {
                'api_url': 'auto',
                'per_page': 100,
                'post_types': ['posts', 'pages'],
                'include_categories': [],
                'exclude_categories': ['uncategorized']
            },
            'static': {
                'content_directory': './content',
                'file_patterns': ['*.md', '*.html'],
                'front_matter': True,
                'excerpt_length': 200
            },
            'sitemap': {
                'url': 'auto',
                'follow_sitemap_index': True,
                'max_urls': 10000,
                'timeout': 30
            },
            'webhook': {
                'enabled': False,
                'port': 8080,
                'host': '0.0.0.0',
                'secret': 'change-this-secret',
                'allowed_ips': ['127.0.0.1']
            },
            'logging': {
                'level': 'INFO',
                'file': None,
                'format': '%(asctime)s - %(levelname)s - %(message)s'
            },
            'performance': {
                'max_workers': 4,
                'request_delay': 0.1,
                'retry_attempts': 3,
                'retry_delay': 1
            }
        }
        
        config_file = Path(self.config_path)
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
            self.logger.info(f"Created default config at {config_file}")
        except Exception as e:
            self.logger.error(f"Could not create config file: {e}")
            
        return default_config
    
    def generate_header(self) -> str:
        """Generate llms.txt header"""
        timestamp = datetime.datetime.now().isoformat()
        header = f"""# LLMs.txt for {self.config['site_name']}
#
# Generated on: {timestamp}
# Generator: Universal LLMs.txt Generator v{__version__}
# Author: {self.config.get('contact_email', 'N/A')}
# Website: {self.config['site_url']}
# Description: {self.config['description']}
#
# This file provides structured information about our website's content
# for Large Language Models (LLMs) and AI systems.
#
# Learn more about LLMs.txt: https://llmstxt.org/
# Generator source: https://github.com/AsifMinar/Universal-LLMS.txt-Generator
#
# ==========================================

"""
        return header
    
    def get_content_hash(self, items: List[ContentItem]) -> str:
        """Generate hash of content for change detection"""
        content_str = json.dumps([asdict(item) for item in items], sort_keys=True, default=str)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def load_cache(self) -> Dict:
        """Load cache file"""
        cache_file = Path(self.config['cache_file'])
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    
                # Check if cache is still valid
                cache_duration = self.config.get('cache_duration', 3600)
                if cache.get('timestamp'):
                    cache_time = datetime.datetime.fromisoformat(cache['timestamp'])
                    if (datetime.datetime.now() - cache_time).total_seconds() > cache_duration:
                        return {}
                return cache
            except Exception as e:
                self.logger.warning(f"Error loading cache: {e}")
        return {}
    
    def save_cache(self, cache_data: Dict):
        """Save cache file"""
        cache_data['timestamp'] = datetime.datetime.now().isoformat()
        cache_data['generator_version'] = __version__
        try:
            with open(self.config['cache_file'], 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving cache: {e}")
    
    def backup_file(self, file_path: Union[str, Path]):
        """Create backup of a file"""
        if not self.config.get('backup_files', True):
            return
            
        file_path = Path(file_path)
        if file_path.exists():
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup_{timestamp}")
            try:
                shutil.copy2(file_path, backup_path)
                self.logger.info(f"Created backup: {backup_path}")
            except Exception as e:
                self.logger.warning(f"Failed to create backup for {file_path}: {e}")
    
    def update_sitemap(self, llms_txt_url: str):
        """Update sitemap.xml to include llms.txt"""
        if not self.config.get('auto_update_sitemap', True):
            return
            
        # Common sitemap paths
        sitemap_paths = ['sitemap.xml', 'sitemap_index.xml', 'public/sitemap.xml', 'static/sitemap.xml']
        
        for sitemap_path in sitemap_paths:
            sitemap_file = Path(sitemap_path)
            if sitemap_file.exists():
                try:
                    self.backup_file(sitemap_file)
                    
                    # Parse existing sitemap
                    tree = ET.parse(sitemap_file)
                    root = tree.getroot()
                    
                    # Check if llms.txt is already in sitemap
                    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                    
                    # Register namespace to avoid ns0 prefix
                    ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
                    
                    existing_urls = []
                    for url_elem in root.findall('ns:url', namespace):
                        loc = url_elem.find('ns:loc', namespace)
                        if loc is not None:
                            existing_urls.append(loc.text)
                    
                    if llms_txt_url not in existing_urls:
                        # Add llms.txt to sitemap
                        url_elem = ET.SubElement(root, 'url')
                        loc_elem = ET.SubElement(url_elem, 'loc')
                        loc_elem.text = llms_txt_url
                        
                        lastmod_elem = ET.SubElement(url_elem, 'lastmod')
                        lastmod_elem.text = datetime.datetime.now().strftime('%Y-%m-%d')
                        
                        changefreq_elem = ET.SubElement(url_elem, 'changefreq')
                        changefreq_elem.text = 'daily'
                        
                        priority_elem = ET.SubElement(url_elem, 'priority')
                        priority_elem.text = '0.8'
                        
                        # Write updated sitemap
                        tree.write(sitemap_file, encoding='utf-8', xml_declaration=True)
                        self.logger.info(f"Updated sitemap: {sitemap_file}")
                    else:
                        self.logger.info(f"LLMs.txt already exists in sitemap: {sitemap_file}")
                    
                except Exception as e:
                    self.logger.error(f"Error updating sitemap {sitemap_file}: {e}")
                break
    
    def update_robots_txt(self, llms_txt_url: str):
        """Update robots.txt to include llms.txt"""
        if not self.config.get('auto_update_robots', True):
            return
            
        robots_paths = ['robots.txt', 'public/robots.txt', 'static/robots.txt']
        
        for robots_path in robots_paths:
            robots_file = Path(robots_path)
            
            # Create robots.txt if it doesn't exist
            if not robots_file.exists():
                robots_file.parent.mkdir(parents=True, exist_ok=True)
                robots_file.touch()
            
            try:
                self.backup_file(robots_file)
                
                # Read existing robots.txt
                with open(robots_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if llms.txt is already referenced
                if 'llms.txt' not in content.lower():
                    # Add llms.txt reference
                    if not content.endswith('\n'):
                        content += '\n'
                    
                    content += f"\n# LLMs.txt for AI and language models\n"
                    content += f"# Learn more: https://llmstxt.org/\n"
                    content += f"# Generated by: https://github.com/AsifMinar/Universal-LLMS.txt-Generator\n"
                    content += f"Allow: /llms.txt\n"
                    
                    # Write updated robots.txt
                    with open(robots_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.logger.info(f"Updated robots.txt: {robots_file}")
                else:
                    self.logger.info(f"LLMs.txt already exists in robots.txt: {robots_file}")
                
            except Exception as e:
                self.logger.error(f"Error updating robots.txt {robots_file}: {e}")
            break
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        required_fields = ['site_url', 'site_name', 'extractor']
        
        for field in required_fields:
            if field not in self.config:
                self.logger.error(f"Missing required config field: {field}")
                return False
        
        extractor_name = self.config['extractor']
        if extractor_name not in self.extractors:
            self.logger.error(f"Unknown extractor: {extractor_name}")
            return False
        
        # Validate extractor-specific config
        extractor = self.extractors[extractor_name]
        if not extractor.validate_config(self.config):
            return False
        
        return True
    
    def generate_llms_txt(self, force_update: bool = False) -> bool:
        """Generate llms.txt file"""
        if not self.validate_config():
            return False
            
        extractor_name = self.config['extractor']
        extractor = self.extractors[extractor_name]
        
        self.logger.info(f"Using {extractor.get_name()} extractor...")
        start_time = time.time()
        
        # Extract content
        try:
            items = extractor.extract_content(self.config)
        except Exception as e:
            self.logger.error(f"Error extracting content: {e}")
            return False
        
        if not items:
            self.logger.warning("No content found!")
            return False
        
        # Filter and process items
        filtered_items = self._filter_and_process_items(items)
        
        if not filtered_items:
            self.logger.warning("No items remaining after filtering!")
            return False
        
        # Check if content changed
        content_hash = self.get_content_hash(filtered_items)
        cache = self.load_cache()
        
        if not force_update and cache.get('content_hash') == content_hash:
            self.logger.info("Content unchanged, skipping update")
            return False
        
        # Generate llms.txt content
        content = self._generate_llms_content(filtered_items)
        
        # Write file
        output_path = Path(self.config['output_path'])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            self.logger.error(f"Error writing llms.txt: {e}")
            return False
        
        # Update sitemap and robots.txt
        llms_txt_url = urljoin(self.config['site_url'], 'llms.txt')
        self.update_sitemap(llms_txt_url)
        self.update_robots_txt(llms_txt_url)
        
        # Update cache
        cache.update({
            'content_hash': content_hash,
            'last_updated': datetime.datetime.now().isoformat(),
            'item_count': len(filtered_items),
            'generation_time': time.time() - start_time,
            'extractor_used': extractor_name
        })
        self.save_cache(cache)
        
        generation_time = time.time() - start_time
        self.logger.info(f"✅ Generated llms.txt with {len(filtered_items)} items in {generation_time:.2f}s at {output_path}")
        return True
    
    def _filter_and_process_items(self, items: List[ContentItem]) -> List[ContentItem]:
        """Filter and process content items"""
        filtered_items = []
        min_word_count = self.config.get('min_word_count', 50)
        
        for item in items:
            # Skip if below minimum word count
            if item.word_count and item.word_count < min_word_count:
                continue
                
            # Skip drafts if not included
            if not self.config.get('include_drafts', False):
                if 'draft' in (item.tags or []) or 'draft' in item.title.lower():
                    continue
            
            filtered_items.append(item)
        
        # Sort items
        sort_by = self.config.get('output', {}).get('sort_by', 'last_modified')
        sort_order = self.config.get('output', {}).get('sort_order', 'desc')
        
        try:
            reverse = sort_order.lower() == 'desc'
            if sort_by == 'title':
                filtered_items.sort(key=lambda x: x.title.lower(), reverse=reverse)
            elif sort_by == 'word_count':
                filtered_items.sort(key=lambda x: x.word_count or 0, reverse=reverse)
            elif sort_by == 'last_modified':
                filtered_items.sort(key=lambda x: x.last_modified or "", reverse=reverse)
        except Exception as e:
            self.logger.warning(f"Error sorting items: {e}")
        
        # Limit items
        max_items = self.config.get('max_items', 1000)
        if len(filtered_items) > max_items:
            filtered_items = filtered_items[:max_items]
        
        return filtered_items
    
    def _generate_llms_content(self, items: List[ContentItem]) -> str:
        """Generate the complete llms.txt content"""
        content = self.generate_header()
        
        # Add statistics if enabled
        if self.config.get('output', {}).get('include_stats', True):
            stats = self._generate_statistics(items)
            content += stats + "\n"
        
        # Group by type if enabled
        if self.config.get('output', {}).get('group_by_type', False):
            content += self._generate_grouped_content(items)
        else:
            # Add all items
            for item in items:
                content += item.to_llms_format()
        
        # Add footer
        content += self._generate_footer(items)
        
        return content
    
    def _generate_statistics(self, items: List[ContentItem]) -> str:
        """Generate statistics section"""
        total_items = len(items)
        total_words = sum(item.word_count or 0 for item in items)
        avg_words = int(total_words / total_items) if total_items > 0 else 0
        
        # Count by type
        type_counts = {}
        for item in items:
            type_counts[item.content_type] = type_counts.get(item.content_type, 0) + 1
        
        # Count by language
        language_counts = {}
        for item in items:
            lang = item.language or 'unknown'
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        stats = f"""# Statistics
# Total items: {total_items}
# Total words: {total_words:,}
# Average words per item: {avg_words}
# Content types: {', '.join(f"{k}({v})" for k, v in type_counts.items())}
# Languages: {', '.join(f"{k}({v})" for k, v in language_counts.items())}
# Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

"""
        return stats
    
    def _generate_grouped_content(self, items: List[ContentItem]) -> str:
        """Generate content grouped by type"""
        grouped = {}
        for item in items:
            content_type = item.content_type
            if content_type not in grouped:
                grouped[content_type] = []
            grouped[content_type].append(item)
        
        content = ""
        for content_type, type_items in grouped.items():
            content += f"\n# ========== {content_type.upper()} ({len(type_items)} items) ==========\n\n"
            for item in type_items:
                content += item.to_llms_format()
        
        return content
    
    def _generate_footer(self, items: List[ContentItem]) -> str:
        """Generate footer section"""
        footer = f"""
# ==========================================
# End of LLMs.txt
# ==========================================
#
# Generated by: Universal LLMs.txt Generator v{__version__}
# Author: {__author__}
# Repository: https://github.com/AsifMinar/Universal-LLMS.txt-Generator
# License: {__license__}
#
# Total content items: {len(items)}
# Generated on: {datetime.datetime.now().isoformat()}
# 
# This file follows the LLMs.txt specification
# Learn more: https://llmstxt.org/
#
# ==========================================
"""
        return footer
    
    def get_content_items(self) -> List[ContentItem]:
        """Get content items without generating file"""
        if not self.validate_config():
            return []
            
        extractor_name = self.config['extractor']
        extractor = self.extractors[extractor_name]
        
        try:
            return extractor.extract_content(self.config)
        except Exception as e:
            self.logger.error(f"Error extracting content: {e}")
            return []


def create_cron_job(interval: str = 'daily', time_str: str = '02:00', config_path: str = 'llms_config.yaml') -> bool:
    """Create a cron job for automatic updates"""
    try:
        # Get the current script path
        script_path = os.path.abspath(__file__)
        python_path = sys.executable
        
        # Create cron command
        cron_command = f"cd {os.path.dirname(script_path)} && {python_path} {os.path.basename(script_path)} --config {config_path} --generate"
        
        # Create cron schedule
        if interval == 'hourly':
            cron_schedule = "0 * * * *"
        elif interval == 'daily':
            hour, minute = time_str.split(':')
            cron_schedule = f"{minute} {hour} * * *"
        elif interval == 'weekly':
            hour, minute = time_str.split(':')
            cron_schedule = f"{minute} {hour} * * 0"  # Sunday
        else:
            logger.error(f"Unsupported interval: {interval}")
            return False
        
        cron_line = f"{cron_schedule} {cron_command}\n"
        
        # Get current crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout if result.returncode == 0 else ""
        
        # Check if our job already exists
        if cron_command in current_cron:
            logger.info("Cron job already exists")
            return True
        
        # Add new cron job
        new_cron = current_cron + cron_line
        
        # Write to temporary file and install
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cron') as f:
            f.write(new_cron)
            temp_path = f.name
        
        subprocess.run(['crontab', temp_path], check=True)
        os.unlink(temp_path)
        
        logger.info(f"✅ Created cron job: {cron_schedule} for {interval} updates")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating cron job: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error creating cron job: {e}")
        return False


def start_webhook_server(port: int = 8080, config_path: str = 'llms_config.yaml') -> bool:
    """Start a simple webhook server for real-time updates"""
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        logger.error("Flask is required for webhook server. Install with: pip install flask")
        return False
    
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    
    # Load webhook configuration
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading config for webhook: {e}")
        return False
    
    webhook_config = config.get('webhook', {})
    expected_secret = webhook_config.get('secret')
    allowed_ips = webhook_config.get('allowed_ips', ['127.0.0.1'])
    
    @app.route('/update', methods=['POST'])
    def webhook_update():
        try:
            # Check IP if configured
            client_ip = request.remote_addr
            if allowed_ips and client_ip not in allowed_ips:
                logger.warning(f"Webhook request from unauthorized IP: {client_ip}")
                return jsonify({'error': 'Unauthorized IP address'}), 403
            
            # Check secret if configured
            if expected_secret and expected_secret != 'change-this-secret':
                provided_secret = None
                if request.is_json:
                    provided_secret = request.json.get('secret')
                elif request.form:
                    provided_secret = request.form.get('secret')
                
                if provided_secret != expected_secret:
                    logger.warning("Webhook request with invalid secret")
                    return jsonify({'error': 'Invalid secret'}), 403
            
            # Generate llms.txt
            generator = LLMsTxtGenerator(config_path)
            success = generator.generate_llms_txt(force_update=True)
            
            response_data = {
                'status': 'success' if success else 'no_update',
                'message': 'LLMs.txt updated successfully' if success else 'No update needed',
                'timestamp': datetime.datetime.now().isoformat(),
                'generator_version': __version__
            }
            
            if success:
                logger.info("✅ Webhook triggered successful update")
            else:
                logger.info("ℹ️ Webhook triggered but no update needed")
                
            return jsonify(response_data)
                
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return jsonify({
                'error': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }), 500
    
    @app.route('/status', methods=['GET'])
    def status():
        return jsonify({
            'status': 'running',
            'service': 'Universal LLMs.txt Generator',
            'version': __version__,
            'timestamp': datetime.datetime.now().isoformat()
        })
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    # Setup graceful shutdown
    def signal_handler(sig, frame):
        logger.info('Webhook server shutting down...')
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    host = webhook_config.get('host', '0.0.0.0')
    logger.info(f"🚀 Starting webhook server on {host}:{port}")
    logger.info(f"💡 Trigger updates: POST to http://{host}:{port}/update")
    logger.info(f"📊 Check status: GET http://{host}:{port}/status")
    logger.info(f"❤️ Health check: GET http://{host}:{port}/health")
    
    try:
        app.run(host=host, port=port, debug=False, use_reloader=False)
        return True
    except Exception as e:
        logger.error(f"Error starting webhook server: {e}")
        return False


def watch_directory(content_dir: str, config_path: str = 'llms_config.yaml', debounce: int = 5) -> bool:
    """Watch directory for changes and auto-update"""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        logger.error("Watchdog is required for directory watching. Install with: pip install watchdog")
        return False
    
    class ContentHandler(FileSystemEventHandler):
        def __init__(self):
            self.last_update = 0
            
        def on_modified(self, event):
            if event.is_directory:
                return
                
            # Debounce rapid file changes
            now = time.time()
            if now - self.last_update < debounce:
                return
            
            self.last_update = now
            
            # Check if it's a content file
            content_extensions = ['.md', '.html', '.txt', '.markdown', '.mdx']
            if any(event.src_path.endswith(ext) for ext in content_extensions):
                logger.info(f"Content changed: {event.src_path}")
                
                # Generate llms.txt
                try:
                    generator = LLMsTxtGenerator(config_path)
                    generator.generate_llms_txt()
                except Exception as e:
                    logger.error(f"Error generating llms.txt after file change: {e}")
    
    if not os.path.exists(content_dir):
        logger.error(f"Directory not found: {content_dir}")
        return False
    
    event_handler = ContentHandler()
    observer = Observer()
    observer.schedule(event_handler, content_dir, recursive=True)
    
    logger.info(f"👁️ Watching directory: {content_dir}")
    logger.info(f"⚙️ Debounce time: {debounce} seconds")
    logger.info("Press Ctrl+C to stop watching")
    
    # Setup graceful shutdown
    def signal_handler(sig, frame):
        logger.info('Stopping directory watcher...')
        observer.stop()
        observer.join()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Stopped watching directory")
    
    observer.join()
    return True


def validate_llms_txt(file_path: str) -> bool:
    """Validate an existing llms.txt file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        issues = []
        
        # Check for header
        if not any(line.startswith('# LLMs.txt for') for line in lines[:10]):
            issues.append("Missing proper header")
        
        # Check for content items
        content_items = content.count('# ') - content.count('# =') - content.count('# LLMs.txt')
        if content_items == 0:
            issues.append("No content items found")
        
        # Check for required fields in items
        url_count = content.count('URL: ')
        type_count = content.count('Type: ')
        
        if url_count != content_items:
            issues.append(f"Mismatch: {content_items} items but {url_count} URLs")
        
        if type_count != content_items:
            issues.append(f"Mismatch: {content_items} items but {type_count} types")
        
        if issues:
            logger.error(f"Validation issues in {file_path}:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        else:
            logger.info(f"✅ {file_path} is valid!")
            logger.info(f"📊 Found {content_items} content items")
            return True
            
    except Exception as e:
        logger.error(f"Error validating {file_path}: {e}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description=f'Universal LLMs.txt Generator v{__version__} - Generate and maintain llms.txt files for any website',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s --init                              # Interactive initialization
  %(prog)s --init --type wordpress             # Initialize for WordPress
  %(prog)s --generate                          # Generate llms.txt
  %(prog)s --generate --force                  # Force regeneration
  %(prog)s --setup-cron --interval daily       # Set up daily auto-updates
  %(prog)s --webhook --port 8080               # Start webhook server
  %(prog)s --watch --content-dir ./content     # Watch directory for changes
  %(prog)s --validate llms.txt                 # Validate existing file

Author: {__author__} ({__email__})
License: {__license__}
Repository: https://github.com/AsifMinar/Universal-LLMS.txt-Generator
        """
    )
    
    # Configuration arguments
    parser.add_argument('--config', default='llms_config.yaml', 
                       help='Configuration file path (default: llms_config.yaml)')
    parser.add_argument('--version', action='version', 
                       version=f'Universal LLMs.txt Generator {__version__}')
    
    # Initialization arguments
    parser.add_argument('--init', action='store_true', 
                       help='Initialize with default configuration')
    parser.add_argument('--type', choices=['wordpress', 'static', 'django', 'flask', 'sitemap'], 
                       help='Website type for initialization')
    
    # Generation arguments
    parser.add_argument('--generate', action='store_true', 
                       help='Generate llms.txt file')
    parser.add_argument('--force', action='store_true', 
                       help='Force update even if no changes detected')
    
    # Validation arguments
    parser.add_argument('--validate', metavar='FILE', 
                       help='Validate an existing llms.txt file')
    parser.add_argument('--validate-config', action='store_true', 
                       help='Validate configuration file')
    
    # Automation arguments
    parser.add_argument('--setup-cron', action='store_true', 
                       help='Set up cron job for automatic updates')
    parser.add_argument('--interval', choices=['hourly', 'daily', 'weekly'], default='daily',
                       help='Cron job interval (default: daily)')
    parser.add_argument('--time', default='02:00', 
                       help='Time for daily/weekly cron jobs in HH:MM format (default: 02:00)')
    
    # Server arguments
    parser.add_argument('--webhook', action='store_true', 
                       help='Start webhook server for real-time updates')
    parser.add_argument('--port', type=int, default=8080, 
                       help='Webhook server port (default: 8080)')
    
    # Monitoring arguments
    parser.add_argument('--watch', action='store_true', 
                       help='Watch directory for file changes')
    parser.add_argument('--content-dir', default='./content', 
                       help='Content directory to watch (default: ./content)')
    parser.add_argument('--debounce', type=int, default=5, 
                       help='Debounce time for file watching in seconds (default: 5)')
    
    # Testing arguments
    parser.add_argument('--test', action='store_true', 
                       help='Test content extraction without generating files')
    parser.add_argument('--url', 
                       help='Test URL for content extraction')
    
    # Logging arguments
