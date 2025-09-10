"""
News Plugin for JARVIS Computer Assistant
Provides news updates and current events
"""

import asyncio
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..base_plugin import BasePlugin, PluginInfo, PluginType, PluginConfig


@dataclass
class NewsArticle:
    """News article data"""
    title: str
    description: str
    url: str
    source: str
    published_at: datetime
    category: str = "general"
    image_url: str = ""


class NewsPlugin(BasePlugin):
    """News and current events plugin"""
    
    PLUGIN_INFO = PluginInfo(
        name="news",
        version="1.0.0",
        description="News updates and current events",
        author="JARVIS Team",
        plugin_type=PluginType.UTILITY,
        dependencies=[],
        config_schema={
            "type": "object",
            "properties": {
                "api_key": {"type": "string", "description": "News API key"},
                "country": {"type": "string", "default": "us", "description": "Country code for news"},
                "language": {"type": "string", "default": "en", "description": "Language code"},
                "categories": {"type": "array", "items": {"type": "string"}, "default": ["technology", "business", "science"]},
                "update_interval": {"type": "integer", "default": 1800, "description": "Update interval in seconds"}
            },
            "required": ["api_key"]
        }
    )
    
    PRIORITY = 40
    
    def __init__(self, plugin_info: PluginInfo, config: PluginConfig = None):
        super().__init__(plugin_info, config)
        self.api_key = None
        self.country = "us"
        self.language = "en"
        self.categories = ["technology", "business", "science"]
        self.update_interval = 1800  # 30 minutes
        self._articles: List[NewsArticle] = []
        self._last_update = None
        self._update_task = None
        self.base_url = "https://newsapi.org/v2"
        
    async def _initialize(self) -> bool:
        """Initialize news plugin"""
        try:
            # Load configuration
            settings = self.config.settings or {}
            self.api_key = settings.get("api_key")
            self.country = settings.get("country", "us")
            self.language = settings.get("language", "en")
            self.categories = settings.get("categories", ["technology", "business", "science"])
            self.update_interval = settings.get("update_interval", 1800)
            
            if not self.api_key:
                self.logger.warning("No API key provided for news plugin")
                return False
            
            # Load initial news
            await self._update_news()
            
            self.logger.info("News plugin initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize news plugin: {e}")
            return False
    
    async def _cleanup(self) -> None:
        """Cleanup news plugin"""
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        
        self._articles.clear()
        self.logger.info("News plugin cleaned up")
    
    async def _start(self) -> bool:
        """Start news updates"""
        try:
            # Start periodic news updates
            self._update_task = asyncio.create_task(self._news_update_loop())
            self.logger.info("News updates started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start news updates: {e}")
            return False
    
    async def _stop(self) -> None:
        """Stop news updates"""
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
            self._update_task = None
        
        self.logger.info("News updates stopped")
    
    async def _news_update_loop(self) -> None:
        """Periodic news update loop"""
        while True:
            try:
                await self._update_news()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in news update loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _update_news(self) -> None:
        """Update news articles"""
        try:
            new_articles = []
            
            # Get top headlines
            headlines = await self._get_top_headlines()
            if headlines:
                new_articles.extend(headlines)
            
            # Get articles by category
            for category in self.categories:
                category_articles = await self._get_articles_by_category(category)
                if category_articles:
                    new_articles.extend(category_articles)
            
            if new_articles:
                self._articles = new_articles
                self._last_update = datetime.now()
                self.logger.info(f"Updated news: {len(new_articles)} articles")
                
                # Emit news update event
                self.emit_event("news_updated", {
                    "article_count": len(new_articles),
                    "categories": self.categories
                })
            
        except Exception as e:
            self.logger.error(f"Error updating news: {e}")
    
    async def _get_top_headlines(self) -> List[NewsArticle]:
        """Get top headlines"""
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                "apiKey": self.api_key,
                "country": self.country,
                "language": self.language,
                "pageSize": 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article_data in data.get("articles", []):
                article = NewsArticle(
                    title=article_data.get("title", ""),
                    description=article_data.get("description", ""),
                    url=article_data.get("url", ""),
                    source=article_data.get("source", {}).get("name", ""),
                    published_at=self._parse_date(article_data.get("publishedAt", "")),
                    category="headlines",
                    image_url=article_data.get("urlToImage", "")
                )
                articles.append(article)
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Error getting top headlines: {e}")
            return []
    
    async def _get_articles_by_category(self, category: str) -> List[NewsArticle]:
        """Get articles by category"""
        try:
            url = f"{self.base_url}/everything"
            params = {
                "apiKey": self.api_key,
                "q": category,
                "language": self.language,
                "sortBy": "publishedAt",
                "pageSize": 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article_data in data.get("articles", []):
                article = NewsArticle(
                    title=article_data.get("title", ""),
                    description=article_data.get("description", ""),
                    url=article_data.get("url", ""),
                    source=article_data.get("source", {}).get("name", ""),
                    published_at=self._parse_date(article_data.get("publishedAt", "")),
                    category=category,
                    image_url=article_data.get("urlToImage", "")
                )
                articles.append(article)
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Error getting articles for category {category}: {e}")
            return []
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string"""
        try:
            if date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            pass
        return datetime.now()
    
    async def handle_voice_command(self, command: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Handle news-related voice commands"""
        command_lower = command.lower()
        
        if any(keyword in command_lower for keyword in ["news", "haber", "headlines", "başlıklar", "current events", "güncel olaylar"]):
            try:
                if "technology" in command_lower or "teknoloji" in command_lower:
                    return await self._get_news_by_category("technology")
                elif "business" in command_lower or "iş" in command_lower:
                    return await self._get_news_by_category("business")
                elif "science" in command_lower or "bilim" in command_lower:
                    return await self._get_news_by_category("science")
                elif "latest" in command_lower or "son" in command_lower:
                    return await self._get_latest_news()
                else:
                    return await self._get_top_news()
                    
            except Exception as e:
                self.logger.error(f"Error handling news command: {e}")
                return "Sorry, I couldn't get the latest news right now."
        
        return None
    
    async def _get_news_by_category(self, category: str) -> str:
        """Get news by category"""
        try:
            category_articles = [
                article for article in self._articles
                if article.category == category
            ]
            
            if not category_articles:
                return f"No {category} news available right now."
            
            # Get top 3 articles
            top_articles = sorted(category_articles, key=lambda x: x.published_at, reverse=True)[:3]
            
            response = f"Here are the latest {category} news: "
            for i, article in enumerate(top_articles, 1):
                response += f"{i}. {article.title}. "
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting news by category: {e}")
            return f"Sorry, I couldn't get {category} news right now."
    
    async def _get_latest_news(self) -> str:
        """Get latest news"""
        try:
            if not self._articles:
                return "No news available right now."
            
            # Get latest 3 articles
            latest_articles = sorted(self._articles, key=lambda x: x.published_at, reverse=True)[:3]
            
            response = "Here are the latest news: "
            for i, article in enumerate(latest_articles, 1):
                response += f"{i}. {article.title}. "
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting latest news: {e}")
            return "Sorry, I couldn't get the latest news right now."
    
    async def _get_top_news(self) -> str:
        """Get top news"""
        try:
            if not self._articles:
                return "No news available right now."
            
            # Get top headlines
            headlines = [article for article in self._articles if article.category == "headlines"]
            
            if headlines:
                top_articles = headlines[:3]
            else:
                top_articles = sorted(self._articles, key=lambda x: x.published_at, reverse=True)[:3]
            
            response = "Here are the top news: "
            for i, article in enumerate(top_articles, 1):
                response += f"{i}. {article.title}. "
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting top news: {e}")
            return "Sorry, I couldn't get the top news right now."
    
    def get_articles(self, category: str = None, limit: int = 10) -> List[NewsArticle]:
        """Get news articles"""
        try:
            if category:
                articles = [article for article in self._articles if article.category == category]
            else:
                articles = self._articles
            
            return sorted(articles, key=lambda x: x.published_at, reverse=True)[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting articles: {e}")
            return []
    
    def get_commands(self) -> List[str]:
        """Get supported commands"""
        return [
            "news",
            "haberler",
            "headlines",
            "başlıklar",
            "latest news",
            "son haberler",
            "technology news",
            "teknoloji haberleri",
            "business news",
            "iş haberleri",
            "science news",
            "bilim haberleri",
            "current events",
            "güncel olaylar"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities"""
        return [
            "news_reading",
            "category_filtering",
            "news_updates",
            "headline_summary",
            "news_search"
        ]
