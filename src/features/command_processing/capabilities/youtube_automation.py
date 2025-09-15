"""
YouTube Automation Capabilities

Advanced YouTube automation including video search, selection, and playback
with intelligent video recommendation and interaction.
"""

import asyncio
import logging
import time
import urllib.parse
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from integrations.browser_automation import WebAutomationExecutor, BrowserConfig, BrowserType, BrowserBackend
from integrations.browser_automation.element_finder import FindStrategy, ElementType
from ..capability_system import BaseCapabilityExecutor

logger = logging.getLogger(__name__)

@dataclass
class YouTubeVideo:
    """YouTube video information"""
    title: str
    url: str
    duration: str
    views: str
    channel: str
    thumbnail: str
    description: str = ""

@dataclass
class YouTubeSearchResult:
    """YouTube search result"""
    query: str
    videos: List[YouTubeVideo]
    total_results: int
    search_time: float

class YouTubeAutomationExecutor(BaseCapabilityExecutor):
    """Advanced YouTube automation executor"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.automation_executor: Optional[WebAutomationExecutor] = None
        self._is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize YouTube automation executor"""
        try:
            # Create browser configuration for YouTube
            config = BrowserConfig(
                browser_type=BrowserType.CHROME,
                backend=BrowserBackend.SELENIUM,
                headless=False,  # YouTube needs visual interaction
                window_size=(1920, 1080),
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            self.automation_executor = WebAutomationExecutor(config)
            success = await self.automation_executor.initialize()
            
            if success:
                self._is_initialized = True
                self.logger.info("YouTube automation executor initialized successfully")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to initialize YouTube automation executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if YouTube automation can be executed"""
        action = parameters.get('action', 'search')
        return action in ['search', 'play_video', 'play_playlist', 'get_recommendations', 'get_video_info']
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute YouTube automation operation"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "YouTube automation executor not initialized"}
            
            action = parameters.get('action', 'search')
            query = parameters.get('query', '')
            video_url = parameters.get('video_url', '')
            playlist_url = parameters.get('playlist_url', '')
            
            if action == "search":
                return await self._search_videos(query, parameters)
            elif action == "play_video":
                return await self._play_video(video_url, parameters)
            elif action == "play_playlist":
                return await self._play_playlist(playlist_url, parameters)
            elif action == "get_recommendations":
                return await self._get_recommendations(parameters)
            elif action == "get_video_info":
                return await self._get_video_info(video_url, parameters)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            self.logger.error(f"Error executing YouTube automation: {e}")
            return {"success": False, "error": str(e)}
    
    async def _search_videos(self, query: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Search for YouTube videos with intelligent selection"""
        try:
            start_time = time.time()
            
            # Navigate to YouTube
            nav_result = await self.automation_executor.navigate_to("https://www.youtube.com")
            if not nav_result.success:
                return {"success": False, "error": "Failed to navigate to YouTube"}
            
            # Wait for page to load
            await asyncio.sleep(2)
            
            # Find and click search box
            search_result = await self.automation_executor.click_element(
                locator="input#search",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.INPUT
            )
            
            if not search_result.success:
                # Try alternative selectors
                search_result = await self.automation_executor.click_element(
                    locator="input[name='search_query']",
                    strategy=FindStrategy.CSS_SELECTOR,
                    element_type=ElementType.INPUT
                )
            
            if not search_result.success:
                return {"success": False, "error": "Failed to find search box"}
            
            # Type search query
            type_result = await self.automation_executor.type_text(
                locator="input#search",
                text=query,
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.INPUT
            )
            
            if not type_result.success:
                return {"success": False, "error": "Failed to type search query"}
            
            # Press Enter to search
            enter_result = await self.automation_executor.execute_javascript(
                "document.querySelector('input#search').dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter'}))"
            )
            
            # Wait for search results
            await asyncio.sleep(3)
            
            # Extract video information
            videos = await self._extract_video_results()
            
            search_time = time.time() - start_time
            
            return {
                "success": True,
                "message": f"Found {len(videos)} videos for '{query}'",
                "data": {
                    "query": query,
                    "videos": [video.__dict__ for video in videos],
                    "total_results": len(videos),
                    "search_time": search_time
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to search videos: {e}"}
    
    async def _extract_video_results(self) -> List[YouTubeVideo]:
        """Extract video information from search results"""
        try:
            videos = []
            
            # Wait for video elements to load
            await self.automation_executor.wait_for_element(
                locator="ytd-video-renderer",
                strategy=FindStrategy.CSS_SELECTOR,
                timeout=10
            )
            
            # Get video elements
            video_elements = await self.automation_executor.element_finder.find_elements(
                locator="ytd-video-renderer",
                strategy=FindStrategy.CSS_SELECTOR
            )
            
            for i, element in enumerate(video_elements[:10]):  # Limit to first 10 results
                try:
                    # Extract video information
                    title_element = await self.automation_executor.element_finder.find_element(
                        locator="h3 a",
                        strategy=FindStrategy.CSS_SELECTOR,
                        element_type=ElementType.LINK
                    )
                    
                    if title_element:
                        title = await self.automation_executor.get_text(
                            locator="h3 a",
                            strategy=FindStrategy.CSS_SELECTOR
                        )
                        
                        url_element = await self.automation_executor.element_finder.find_element(
                            locator="h3 a",
                            strategy=FindStrategy.CSS_SELECTOR
                        )
                        
                        if url_element:
                            url_result = await self.automation_executor.get_attribute(
                                locator="h3 a",
                                attribute="href",
                                strategy=FindStrategy.CSS_SELECTOR
                            )
                            
                            if url_result.success:
                                video_url = url_result.data.get("value", "")
                                if not video_url.startswith("http"):
                                    video_url = f"https://www.youtube.com{video_url}"
                                
                                # Extract other information
                                duration = await self._extract_duration(element)
                                views = await self._extract_views(element)
                                channel = await self._extract_channel(element)
                                thumbnail = await self._extract_thumbnail(element)
                                
                                video = YouTubeVideo(
                                    title=title.data.get("text", "") if title.success else f"Video {i+1}",
                                    url=video_url,
                                    duration=duration,
                                    views=views,
                                    channel=channel,
                                    thumbnail=thumbnail
                                )
                                
                                videos.append(video)
                
                except Exception as e:
                    self.logger.warning(f"Failed to extract video {i+1}: {e}")
                    continue
            
            return videos
            
        except Exception as e:
            self.logger.error(f"Failed to extract video results: {e}")
            return []
    
    async def _extract_duration(self, element) -> str:
        """Extract video duration"""
        try:
            duration_result = await self.automation_executor.get_text(
                locator="span.ytd-thumbnail-overlay-time-status-renderer",
                strategy=FindStrategy.CSS_SELECTOR
            )
            return duration_result.data.get("text", "Unknown") if duration_result.success else "Unknown"
        except:
            return "Unknown"
    
    async def _extract_views(self, element) -> str:
        """Extract video views"""
        try:
            views_result = await self.automation_executor.get_text(
                locator="span.ytd-video-meta-block",
                strategy=FindStrategy.CSS_SELECTOR
            )
            return views_result.data.get("text", "Unknown") if views_result.success else "Unknown"
        except:
            return "Unknown"
    
    async def _extract_channel(self, element) -> str:
        """Extract channel name"""
        try:
            channel_result = await self.automation_executor.get_text(
                locator="a.yt-simple-endpoint.style-scope.yt-formatted-string",
                strategy=FindStrategy.CSS_SELECTOR
            )
            return channel_result.data.get("text", "Unknown") if channel_result.success else "Unknown"
        except:
            return "Unknown"
    
    async def _extract_thumbnail(self, element) -> str:
        """Extract video thumbnail"""
        try:
            thumbnail_result = await self.automation_executor.get_attribute(
                locator="img",
                attribute="src",
                strategy=FindStrategy.CSS_SELECTOR
            )
            return thumbnail_result.data.get("value", "") if thumbnail_result.success else ""
        except:
            return ""
    
    async def _play_video(self, video_url: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Play a specific YouTube video"""
        try:
            # Navigate to video URL
            nav_result = await self.automation_executor.navigate_to(video_url)
            if not nav_result.success:
                return {"success": False, "error": "Failed to navigate to video"}
            
            # Wait for video to load
            await asyncio.sleep(3)
            
            # Try to click play button if video is paused
            play_result = await self.automation_executor.click_element(
                locator="button.ytp-play-button",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.BUTTON
            )
            
            # Get video title
            title_result = await self.automation_executor.get_text(
                locator="h1.title",
                strategy=FindStrategy.CSS_SELECTOR
            )
            
            video_title = title_result.data.get("text", "Unknown") if title_result.success else "Unknown"
            
            return {
                "success": True,
                "message": f"Playing video: {video_title}",
                "data": {
                    "video_url": video_url,
                    "video_title": video_title,
                    "auto_played": play_result.success
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to play video: {e}"}
    
    async def _play_playlist(self, playlist_url: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Play a YouTube playlist"""
        try:
            # Navigate to playlist URL
            nav_result = await self.automation_executor.navigate_to(playlist_url)
            if not nav_result.success:
                return {"success": False, "error": "Failed to navigate to playlist"}
            
            # Wait for playlist to load
            await asyncio.sleep(3)
            
            # Click play all button
            play_all_result = await self.automation_executor.click_element(
                locator="button[aria-label*='Play all']",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.BUTTON
            )
            
            # Get playlist title
            title_result = await self.automation_executor.get_text(
                locator="h1.title",
                strategy=FindStrategy.CSS_SELECTOR
            )
            
            playlist_title = title_result.data.get("text", "Unknown") if title_result.success else "Unknown"
            
            return {
                "success": True,
                "message": f"Playing playlist: {playlist_title}",
                "data": {
                    "playlist_url": playlist_url,
                    "playlist_title": playlist_title,
                    "auto_played": play_all_result.success
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to play playlist: {e}"}
    
    async def _get_recommendations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get YouTube recommendations"""
        try:
            # Navigate to YouTube homepage
            nav_result = await self.automation_executor.navigate_to("https://www.youtube.com")
            if not nav_result.success:
                return {"success": False, "error": "Failed to navigate to YouTube"}
            
            # Wait for recommendations to load
            await asyncio.sleep(3)
            
            # Extract recommended videos
            videos = await self._extract_video_results()
            
            return {
                "success": True,
                "message": f"Found {len(videos)} recommended videos",
                "data": {
                    "videos": [video.__dict__ for video in videos],
                    "total_results": len(videos)
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get recommendations: {e}"}
    
    async def _get_video_info(self, video_url: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a video"""
        try:
            # Navigate to video URL
            nav_result = await self.automation_executor.navigate_to(video_url)
            if not nav_result.success:
                return {"success": False, "error": "Failed to navigate to video"}
            
            # Wait for video to load
            await asyncio.sleep(3)
            
            # Extract video information
            title_result = await self.automation_executor.get_text(
                locator="h1.title",
                strategy=FindStrategy.CSS_SELECTOR
            )
            
            channel_result = await self.automation_executor.get_text(
                locator="ytd-channel-name a",
                strategy=FindStrategy.CSS_SELECTOR
            )
            
            views_result = await self.automation_executor.get_text(
                locator="span.view-count",
                strategy=FindStrategy.CSS_SELECTOR
            )
            
            description_result = await self.automation_executor.get_text(
                locator="ytd-expander #content",
                strategy=FindStrategy.CSS_SELECTOR
            )
            
            return {
                "success": True,
                "message": "Video information retrieved successfully",
                "data": {
                    "video_url": video_url,
                    "title": title_result.data.get("text", "") if title_result.success else "",
                    "channel": channel_result.data.get("text", "") if channel_result.success else "",
                    "views": views_result.data.get("text", "") if views_result.success else "",
                    "description": description_result.data.get("text", "") if description_result.success else ""
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get video info: {e}"}
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.automation_executor:
                await self.automation_executor.cleanup()
            self._is_initialized = False
            self.logger.info("YouTube automation executor cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

