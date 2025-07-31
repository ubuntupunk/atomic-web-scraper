"""
Mock website generator for testing scraping functionality.

This module provides comprehensive mock website generation capabilities
for testing various scraping scenarios without relying on external websites.
"""

import random
import string
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse

from pydantic import BaseModel, Field


class WebsiteType(str, Enum):
    """Types of websites that can be generated."""
    ECOMMERCE = "ecommerce"
    NEWS = "news"
    BLOG = "blog"
    DIRECTORY = "directory"
    PORTFOLIO = "portfolio"
    DOCUMENTATION = "documentation"
    FORUM = "forum"
    SOCIAL = "social"


class MockWebsiteConfig(BaseModel):
    """Configuration for mock website generation."""
    website_type: WebsiteType
    base_url: str = "https://example.com"
    num_pages: int = 10
    items_per_page: int = 20
    include_pagination: bool = True
    include_navigation: bool = True
    include_errors: bool = False
    error_rate: float = 0.1
    include_malformed_html: bool = False
    malformed_rate: float = 0.05
    include_dynamic_content: bool = False
    language: str = "en"
    include_metadata: bool = True


class MockWebsite:
    """Mock website generator for testing scraping functionality."""
    
    def __init__(self, config: MockWebsiteConfig):
        self.config = config
        self._pages_cache: Dict[str, str] = {}
        self._setup_generators()
    
    def _setup_generators(self):
        """Set up content generators based on website type."""
        self.generators = {
            WebsiteType.ECOMMERCE: self._generate_ecommerce_content,
            WebsiteType.NEWS: self._generate_news_content,
            WebsiteType.BLOG: self._generate_blog_content,
            WebsiteType.DIRECTORY: self._generate_directory_content,
            WebsiteType.PORTFOLIO: self._generate_portfolio_content,
            WebsiteType.DOCUMENTATION: self._generate_documentation_content,
            WebsiteType.FORUM: self._generate_forum_content,
            WebsiteType.SOCIAL: self._generate_social_content
        }
    
    def generate_page(self, path: str = "/") -> str:
        """Generate HTML content for a specific page."""
        if path in self._pages_cache:
            return self._pages_cache[path]
        
        # Determine page type and content
        if path == "/" or path == "/index.html":
            html = self._generate_homepage()
        elif path.startswith("/page/"):
            page_num = self._extract_page_number(path)
            html = self._generate_listing_page(page_num)
        elif path.startswith("/item/") or path.startswith("/product/"):
            item_id = self._extract_item_id(path)
            html = self._generate_item_page(item_id)
        elif path.startswith("/category/"):
            category = self._extract_category(path)
            html = self._generate_category_page(category)
        else:
            html = self._generate_generic_page(path)
        
        # Apply error simulation if enabled
        if self.config.include_errors and random.random() < self.config.error_rate:
            html = self._simulate_error(html)
        
        # Apply malformed HTML if enabled
        if self.config.include_malformed_html and random.random() < self.config.malformed_rate:
            html = self._introduce_malformed_html(html)
        
        self._pages_cache[path] = html
        return html
    
    def _generate_homepage(self) -> str:
        """Generate homepage HTML."""
        generator = self.generators[self.config.website_type]
        content = generator("homepage")
        
        return self._wrap_in_html_template(
            title=f"Homepage - {self.config.website_type.title()} Site",
            content=content,
            include_navigation=True
        )
    
    def _generate_ecommerce_content(self, page_type: str, **kwargs) -> str:
        """Generate e-commerce website content."""
        if page_type == "homepage":
            return """
            <div class="homepage">
                <div class="hero-section">
                    <h1>Welcome to Our Store</h1>
                    <p>Find the best products at amazing prices!</p>
                </div>
                <div class="featured-products">
                    <h2>Featured Products</h2>
                    <div class="product-grid">
                        <div class="product-card" data-product-id="1">
                            <img src="/images/product1.jpg" alt="Smartphone X1">
                            <h3><a href="/product/1">Smartphone X1</a></h3>
                            <p class="price">$599.99</p>
                            <p class="rating">★★★★☆ (4.2/5)</p>
                        </div>
                    </div>
                </div>
            </div>
            """
        return "<div>E-commerce content</div>"
    
    def _generate_news_content(self, page_type: str, **kwargs) -> str:
        """Generate news website content."""
        if page_type == "homepage":
            return """
            <div class="news-homepage">
                <div class="breaking-news">
                    <h1>Breaking News</h1>
                    <div class="headline-story">
                        <h2><a href="/article/1">Major Development</a></h2>
                        <p class="summary">Industry leaders announce...</p>
                        <p class="meta">By John Reporter | 2 hours ago</p>
                    </div>
                </div>
                <div class="top-stories">
                    <h2>Top Stories</h2>
                    <div class="story-grid">
                        <article class="story-card">
                            <h3><a href="/article/1">Economic Markets Show Growth</a></h3>
                            <p class="meta">By Jane Smith | 4 hours ago</p>
                        </article>
                    </div>
                </div>
            </div>
            """
        return "<div>News content</div>"
    
    def _generate_blog_content(self, page_type: str, **kwargs) -> str:
        """Generate blog website content."""
        if page_type == "homepage":
            return """
            <div class="blog-homepage">
                <h1>Welcome to My Blog</h1>
                <div class="recent-posts">
                    <article class="post-card">
                        <h3><a href="/post/1">My First Blog Post</a></h3>
                        <p class="excerpt">This is an excerpt...</p>
                    </article>
                </div>
            </div>
            """
        return "<div>Blog content</div>"
    
    def _generate_directory_content(self, page_type: str, **kwargs) -> str:
        """Generate directory website content."""
        if page_type == "homepage":
            return """
            <div class="directory-homepage">
                <h1>Business Directory</h1>
                <div class="listing-grid">
                    <div class="listing-card">
                        <h3><a href="/item/1">Acme Corporation</a></h3>
                        <p class="category">Technology</p>
                    </div>
                </div>
            </div>
            """
        return "<div>Directory content</div>"
    
    def _generate_portfolio_content(self, page_type: str, **kwargs) -> str:
        """Generate portfolio website content."""
        return "<div class='portfolio'>Portfolio content</div>"
    
    def _generate_documentation_content(self, page_type: str, **kwargs) -> str:
        """Generate documentation website content."""
        return "<div class='documentation'>Documentation content</div>"
    
    def _generate_forum_content(self, page_type: str, **kwargs) -> str:
        """Generate forum website content."""
        return "<div class='forum'>Forum content</div>"
    
    def _generate_social_content(self, page_type: str, **kwargs) -> str:
        """Generate social media website content."""
        return "<div class='social'>Social content</div>"
    
    def _wrap_in_html_template(self, title: str, content: str, include_navigation: bool = True) -> str:
        """Wrap content in a complete HTML template."""
        return f"""<!DOCTYPE html>
<html lang="{self.config.language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="Mock website for testing">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .product-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }}
        .product-card {{ border: 1px solid #ddd; padding: 15px; }}
        .price {{ font-weight: bold; color: #007cba; }}
        .rating {{ color: #ffa500; }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>"""
    
    def _simulate_error(self, html: str) -> str:
        """Simulate various types of errors in HTML."""
        error_types = ["network_timeout", "server_error", "partial_content"]
        error_type = random.choice(error_types)
        
        if error_type == "server_error":
            return "<html><body><h1>500 Internal Server Error</h1></body></html>"
        elif error_type == "partial_content":
            return html[:len(html)//2]
        else:
            return html[:len(html)//2] + "<!-- Connection timed out -->"
    
    def _introduce_malformed_html(self, html: str) -> str:
        """Introduce malformed HTML for testing error handling."""
        return html.replace("<div>", "<div")  # Missing closing bracket
    
    def _extract_page_number(self, path: str) -> int:
        """Extract page number from URL path."""
        try:
            return int(path.split("/")[-1])
        except (ValueError, IndexError):
            return 1
    
    def _extract_item_id(self, path: str) -> str:
        """Extract item ID from URL path."""
        try:
            parts = path.split("/")
            return parts[-1] if parts[-1] else "1"
        except IndexError:
            return "1"
    
    def _extract_category(self, path: str) -> str:
        """Extract category from URL path."""
        try:
            return path.split("/")[-1]
        except IndexError:
            return "general"
    
    def get_all_urls(self) -> List[str]:
        """Get all available URLs for this mock website."""
        urls = ["/"]
        
        # Add pagination URLs
        for page in range(1, self.config.num_pages + 1):
            urls.append(f"/page/{page}")
        
        # Add item URLs
        for item_id in range(1, min(self.config.items_per_page, 5) + 1):
            if self.config.website_type == WebsiteType.ECOMMERCE:
                urls.append(f"/product/{item_id}")
            elif self.config.website_type == WebsiteType.NEWS:
                urls.append(f"/article/{item_id}")
            elif self.config.website_type == WebsiteType.BLOG:
                urls.append(f"/post/{item_id}")
            else:
                urls.append(f"/item/{item_id}")
        
        # Add category URLs
        categories = ["electronics", "clothing"]
        for category in categories:
            urls.append(f"/category/{category}")
        
        return urls


class MockWebsiteGenerator:
    """Factory class for generating different types of mock websites."""
    
    @staticmethod
    def create_ecommerce_site(num_products: int = 50, include_errors: bool = False) -> MockWebsite:
        """Create a mock e-commerce website."""
        config = MockWebsiteConfig(
            website_type=WebsiteType.ECOMMERCE,
            num_pages=max(1, (num_products + 19) // 20),
            items_per_page=20,
            include_errors=include_errors,
            include_pagination=True,
            include_navigation=True
        )
        return MockWebsite(config)
    
    @staticmethod
    def create_news_site(num_articles: int = 30, include_errors: bool = False) -> MockWebsite:
        """Create a mock news website."""
        config = MockWebsiteConfig(
            website_type=WebsiteType.NEWS,
            num_pages=max(1, (num_articles + 14) // 15),
            items_per_page=15,
            include_errors=include_errors,
            include_pagination=True,
            include_navigation=True
        )
        return MockWebsite(config)
    
    @staticmethod
    def create_blog_site(num_posts: int = 25, include_errors: bool = False) -> MockWebsite:
        """Create a mock blog website."""
        config = MockWebsiteConfig(
            website_type=WebsiteType.BLOG,
            num_pages=max(1, (num_posts + 9) // 10),
            items_per_page=10,
            include_errors=include_errors,
            include_pagination=True,
            include_navigation=True
        )
        return MockWebsite(config)
    
    @staticmethod
    def create_directory_site(num_entries: int = 100, include_errors: bool = False) -> MockWebsite:
        """Create a mock directory website."""
        config = MockWebsiteConfig(
            website_type=WebsiteType.DIRECTORY,
            num_pages=max(1, (num_entries + 24) // 25),
            items_per_page=25,
            include_errors=include_errors,
            include_pagination=True,
            include_navigation=True
        )
        return MockWebsite(config)
    
    @staticmethod
    def create_problematic_site() -> MockWebsite:
        """Create a mock website with various problems for testing error handling."""
        config = MockWebsiteConfig(
            website_type=WebsiteType.ECOMMERCE,
            num_pages=5,
            items_per_page=10,
            include_errors=True,
            error_rate=0.3,
            include_malformed_html=True,
            malformed_rate=0.2,
            include_navigation=True
        )
        return MockWebsite(config)