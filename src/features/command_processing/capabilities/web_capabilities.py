"""
Web Capability Executors

Implements concrete executors for web operations including
search, navigation, data extraction, and form automation.
"""

import asyncio
import logging
import platform
import subprocess
import webbrowser
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..capability_system import BaseCapabilityExecutor

logger = logging.getLogger(__name__)

class WebSearchExecutor(BaseCapabilityExecutor):
    """Executor for web search operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web search operation"""
        try:
            action = parameters.get('action', 'search')
            query = parameters.get('query', '')
            engine = parameters.get('engine', 'google')
            num_results = parameters.get('num_results', 10)
            language = parameters.get('language', 'en')
            
            if action == "search":
                return await self._search_web(query, engine, num_results, language)
            elif action == "image_search":
                return await self._search_images(query, num_results)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing web search: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if web search can be executed"""
        action = parameters.get('action', 'search')
        return action in ['search', 'image_search']
    
    async def _search_web(self, query: str, engine: str, num_results: int, language: str) -> Dict[str, Any]:
        """Search the web using specified engine"""
        try:
            if engine == "google":
                search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={num_results}&hl={language}"
            elif engine == "duckduckgo":
                search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            elif engine == "bing":
                search_url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&count={num_results}"
            else:
                search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={num_results}"
            
            # Open search in browser
            webbrowser.open(search_url)
            
            return {
                "success": True,
                "message": f"Searched for '{query}' using {engine}",
                "data": {"url": search_url, "query": query, "engine": engine}
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to search web: {e}"}
    
    async def _search_images(self, query: str, num_results: int) -> Dict[str, Any]:
        """Search for images"""
        try:
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&tbm=isch&num={num_results}"
            webbrowser.open(search_url)
            
            return {
                "success": True,
                "message": f"Searched for images of '{query}'",
                "data": {"url": search_url, "query": query}
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to search images: {e}"}

class WebNavigationExecutor(BaseCapabilityExecutor):
    """Executor for web navigation operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web navigation operation"""
        try:
            action = parameters.get('action', 'open')
            url = parameters.get('url', '')
            browser = parameters.get('browser', 'chrome')
            incognito = parameters.get('incognito', False)
            new_tab = parameters.get('new_tab', True)
            
            if action == "open":
                return await self._open_url(url, browser, incognito, new_tab)
            elif action == "check_status":
                return await self._check_website_status(url)
            elif action == "get_title":
                return await self._get_website_title(url)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing web navigation: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if web navigation can be executed"""
        action = parameters.get('action', 'open')
        return action in ['open', 'check_status', 'get_title']
    
    async def _open_url(self, url: str, browser: str, incognito: bool, new_tab: bool) -> Dict[str, Any]:
        """Open URL in browser"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            if platform.system() == "Windows":
                if browser == "chrome":
                    cmd = ["start", "chrome", url]
                elif browser == "firefox":
                    cmd = ["start", "firefox", url]
                elif browser == "edge":
                    cmd = ["start", "msedge", url]
                else:
                    webbrowser.open(url)
                    return {"success": True, "message": f"Opened {url} in default browser"}
            else:
                if browser == "chrome":
                    cmd = ["google-chrome", url]
                elif browser == "firefox":
                    cmd = ["firefox", url]
                else:
                    webbrowser.open(url)
                    return {"success": True, "message": f"Opened {url} in default browser"}
            
            if incognito and browser == "chrome":
                cmd.append("--incognito")
            elif incognito and browser == "firefox":
                cmd.append("--private-window")
            
            if new_tab and browser == "chrome":
                cmd.append("--new-tab")
            
            subprocess.Popen(cmd)
            return {"success": True, "message": f"Opened {url} in {browser}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to open URL: {e}"}
    
    async def _check_website_status(self, url: str) -> Dict[str, Any]:
        """Check if website is accessible"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # Use curl to check status
            cmd = ["curl", "-I", "-L", "--max-time", "10", url]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse response headers
            headers = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip().lower()] = value.strip()
            
            status_code = headers.get('http', '').split()[1] if 'http' in headers else "Unknown"
            
            return {
                "success": True,
                "data": {
                    "url": url,
                    "status_code": status_code,
                    "accessible": status_code.startswith('2') or status_code.startswith('3')
                },
                "message": f"Website {url} is {'accessible' if status_code.startswith('2') else 'not accessible'}"
            }
            
        except subprocess.CalledProcessError:
            return {
                "success": True,
                "data": {"url": url, "status_code": "Error", "accessible": False},
                "message": f"Website {url} is not accessible"
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to check website status: {e}"}
    
    async def _get_website_title(self, url: str) -> Dict[str, Any]:
        """Get website title"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # Use curl to get page content
            cmd = ["curl", "-s", "--max-time", "10", url]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Extract title from HTML
            import re
            title_match = re.search(r'<title[^>]*>([^<]*)</title>', result.stdout, re.IGNORECASE)
            
            if title_match:
                title = title_match.group(1).strip()
                return {
                    "success": True,
                    "data": {"url": url, "title": title},
                    "message": f"Website title: {title}"
                }
            else:
                return {
                    "success": True,
                    "data": {"url": url, "title": "No title found"},
                    "message": "No title found for website"
                }
                
        except subprocess.CalledProcessError:
            return {"success": False, "error": f"Failed to access website: {url}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to get website title: {e}"}

class DataExtractionExecutor(BaseCapabilityExecutor):
    """Executor for web data extraction operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data extraction operation"""
        try:
            action = parameters.get('action', 'extract_text')
            url = parameters.get('url', '')
            selector = parameters.get('selector', '')
            max_length = parameters.get('max_length', 10000)
            
            if action == "extract_text":
                return await self._extract_text(url, max_length)
            elif action == "extract_links":
                return await self._extract_links(url)
            elif action == "extract_images":
                return await self._extract_images(url)
            elif action == "extract_elements":
                return await self._extract_elements(url, selector)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing data extraction: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if data extraction can be executed"""
        action = parameters.get('action', 'extract_text')
        return action in ['extract_text', 'extract_links', 'extract_images', 'extract_elements']
    
    async def _extract_text(self, url: str, max_length: int) -> Dict[str, Any]:
        """Extract text content from webpage"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # Use curl to get page content
            cmd = ["curl", "-s", "--max-time", "10", url]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Remove HTML tags using sed
            cmd = ["sed", "s/<[^>]*>//g"]
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            text, _ = process.communicate(input=result.stdout)
            
            # Limit text length
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            return {
                "success": True,
                "data": {"url": url, "text": text, "length": len(text)},
                "message": f"Extracted {len(text)} characters from {url}"
            }
            
        except subprocess.CalledProcessError:
            return {"success": False, "error": f"Failed to access website: {url}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to extract text: {e}"}
    
    async def _extract_links(self, url: str) -> Dict[str, Any]:
        """Extract all links from webpage"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # Use curl to get page content
            cmd = ["curl", "-s", "--max-time", "10", url]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Extract links using grep and sed
            cmd = ["grep", "-o", 'href="[^"]*"', "-"]
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            links_output, _ = process.communicate(input=result.stdout)
            
            # Clean up links
            links = []
            for line in links_output.split('\n'):
                if line.strip():
                    link = line.replace('href="', '').replace('"', '').strip()
                    if link and not link.startswith('#'):
                        links.append(link)
            
            return {
                "success": True,
                "data": {"url": url, "links": links, "count": len(links)},
                "message": f"Extracted {len(links)} links from {url}"
            }
            
        except subprocess.CalledProcessError:
            return {"success": False, "error": f"Failed to access website: {url}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to extract links: {e}"}
    
    async def _extract_images(self, url: str) -> Dict[str, Any]:
        """Extract all images from webpage"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # Use curl to get page content
            cmd = ["curl", "-s", "--max-time", "10", url]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Extract image sources using grep and sed
            cmd = ["grep", "-o", 'src="[^"]*"', "-"]
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            images_output, _ = process.communicate(input=result.stdout)
            
            # Clean up image URLs
            images = []
            for line in images_output.split('\n'):
                if line.strip():
                    img_src = line.replace('src="', '').replace('"', '').strip()
                    if img_src and img_src.startswith(('http://', 'https://', '/')):
                        images.append(img_src)
            
            return {
                "success": True,
                "data": {"url": url, "images": images, "count": len(images)},
                "message": f"Extracted {len(images)} images from {url}"
            }
            
        except subprocess.CalledProcessError:
            return {"success": False, "error": f"Failed to access website: {url}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to extract images: {e}"}
    
    async def _extract_elements(self, url: str, selector: str) -> Dict[str, Any]:
        """Extract specific elements from webpage"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # Use curl to get page content
            cmd = ["curl", "-s", "--max-time", "10", url]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Extract elements using grep (simplified CSS selector support)
            if selector.startswith('.'):
                # Class selector
                class_name = selector[1:]
                cmd = ["grep", "-o", f'class="[^"]*{class_name}[^"]*"[^>]*>[^<]*</[^>]*>', "-"]
            elif selector.startswith('#'):
                # ID selector
                id_name = selector[1:]
                cmd = ["grep", "-o", f'id="{id_name}"[^>]*>[^<]*</[^>]*>', "-"]
            else:
                # Tag selector
                cmd = ["grep", "-o", f'<{selector}[^>]*>[^<]*</{selector}>', "-"]
            
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            elements_output, _ = process.communicate(input=result.stdout)
            
            # Clean up elements
            elements = []
            for line in elements_output.split('\n'):
                if line.strip():
                    elements.append(line.strip())
            
            return {
                "success": True,
                "data": {"url": url, "selector": selector, "elements": elements, "count": len(elements)},
                "message": f"Extracted {len(elements)} elements matching '{selector}' from {url}"
            }
            
        except subprocess.CalledProcessError:
            return {"success": False, "error": f"Failed to access website: {url}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to extract elements: {e}"}

class FormAutomationExecutor(BaseCapabilityExecutor):
    """Executor for web form automation operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute form automation operation"""
        try:
            action = parameters.get('action', 'fill_form')
            url = parameters.get('url', '')
            field_name = parameters.get('field_name', '')
            value = parameters.get('value', '')
            form_data = parameters.get('form_data', {})
            
            if action == "fill_form":
                return await self._fill_form(url, field_name, value)
            elif action == "submit_form":
                return await self._submit_form(url, form_data)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing form automation: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if form automation can be executed"""
        action = parameters.get('action', 'fill_form')
        return action in ['fill_form', 'submit_form']
    
    async def _fill_form(self, url: str, field_name: str, value: str) -> Dict[str, Any]:
        """Fill a form field (simplified implementation)"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # This is a simplified implementation
            # In a real scenario, you would use a web automation tool like Selenium
            # For now, we'll just open the URL and provide instructions
            
            webbrowser.open(url)
            
            return {
                "success": True,
                "message": f"Opened {url} for form filling. Please fill field '{field_name}' with value '{value}' manually.",
                "data": {"url": url, "field_name": field_name, "value": value}
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to fill form: {e}"}
    
    async def _submit_form(self, url: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a form (simplified implementation)"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            # This is a simplified implementation
            # In a real scenario, you would use a web automation tool like Selenium
            # For now, we'll just open the URL and provide instructions
            
            webbrowser.open(url)
            
            form_info = ", ".join([f"{k}: {v}" for k, v in form_data.items()])
            
            return {
                "success": True,
                "message": f"Opened {url} for form submission. Please submit form with data: {form_info}",
                "data": {"url": url, "form_data": form_data}
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to submit form: {e}"}

class YouTubeExecutor(BaseCapabilityExecutor):
    """Executor for YouTube operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute YouTube operation"""
        try:
            action = parameters.get('action', 'search')
            query = parameters.get('query', '')
            video_id = parameters.get('video_id', '')
            playlist_id = parameters.get('playlist_id', '')
            
            if action == "search":
                return await self._search_youtube(query)
            elif action == "play_video":
                return await self._play_video(video_id)
            elif action == "play_playlist":
                return await self._play_playlist(playlist_id)
            elif action == "open_channel":
                return await self._open_channel(query)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing YouTube operation: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if YouTube operation can be executed"""
        action = parameters.get('action', 'search')
        return action in ['search', 'play_video', 'play_playlist', 'open_channel']
    
    async def _search_youtube(self, query: str) -> Dict[str, Any]:
        """Search YouTube for videos"""
        try:
            if not query:
                return {"success": False, "error": "No search query provided"}
            
            # Create YouTube search URL
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            
            # Open in browser
            webbrowser.open(search_url)
            
            return {
                "success": True,
                "message": f"Searching YouTube for '{query}'",
                "data": {"url": search_url, "query": query}
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to search YouTube: {e}"}
    
    async def _play_video(self, video_id: str) -> Dict[str, Any]:
        """Play a specific YouTube video"""
        try:
            if not video_id:
                return {"success": False, "error": "No video ID provided"}
            
            # Create YouTube video URL
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Open in browser
            webbrowser.open(video_url)
            
            return {
                "success": True,
                "message": f"Playing YouTube video: {video_id}",
                "data": {"url": video_url, "video_id": video_id}
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to play video: {e}"}
    
    async def _play_playlist(self, playlist_id: str) -> Dict[str, Any]:
        """Play a YouTube playlist"""
        try:
            if not playlist_id:
                return {"success": False, "error": "No playlist ID provided"}
            
            # Create YouTube playlist URL
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            
            # Open in browser
            webbrowser.open(playlist_url)
            
            return {
                "success": True,
                "message": f"Playing YouTube playlist: {playlist_id}",
                "data": {"url": playlist_url, "playlist_id": playlist_id}
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to play playlist: {e}"}
    
    async def _open_channel(self, channel_name: str) -> Dict[str, Any]:
        """Open a YouTube channel"""
        try:
            if not channel_name:
                return {"success": False, "error": "No channel name provided"}
            
            # Create YouTube channel search URL
            channel_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(channel_name)}&sp=EgIQAg%253D%253D"
            
            # Open in browser
            webbrowser.open(channel_url)
            
            return {
                "success": True,
                "message": f"Opening YouTube channel: {channel_name}",
                "data": {"url": channel_url, "channel_name": channel_name}
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to open channel: {e}"}

# Export all executors
__all__ = [
    'WebSearchExecutor',
    'WebNavigationExecutor',
    'DataExtractionExecutor',
    'FormAutomationExecutor',
    'YouTubeExecutor'
]
