"""
Media Capability Executors

Implements concrete executors for media control operations including
music/video playback, browser automation, and YouTube integration.
"""

import asyncio
import logging
import platform
import subprocess
import webbrowser
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..capability_system import BaseCapabilityExecutor

logger = logging.getLogger(__name__)

class MusicPlaybackExecutor(BaseCapabilityExecutor):
    """Executor for music playback operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute music playback operation"""
        try:
            action = parameters.get('action', 'play')
            song = parameters.get('song', '')
            artist = parameters.get('artist', '')
            playlist = parameters.get('playlist', '')
            source = parameters.get('source', 'youtube')
            
            if action == "play":
                return await self._play_music(song, artist, playlist, source)
            elif action == "pause":
                return await self._pause_music()
            elif action == "stop":
                return await self._stop_music()
            elif action == "next":
                return await self._next_track()
            elif action == "previous":
                return await self._previous_track()
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing music playback: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if music playback can be executed"""
        action = parameters.get('action', 'play')
        return action in ['play', 'pause', 'stop', 'next', 'previous']
    
    async def _play_music(self, song: str, artist: str, playlist: str, source: str) -> Dict[str, Any]:
        """Play music from specified source"""
        try:
            if source == "youtube" and song:
                # Use youtube-dl to play from YouTube
                search_query = f"{song} {artist}".strip()
                cmd = [
                    "youtube-dl", "--extract-audio", "--audio-format", "mp3",
                    f"ytsearch1:{search_query}", "--exec", "mpv {}"
                ]
                subprocess.Popen(cmd)
                return {"success": True, "message": f"Playing {song} by {artist} from YouTube"}
            
            elif source == "local" and song:
                # Play local file
                cmd = ["mpv", song]
                subprocess.Popen(cmd)
                return {"success": True, "message": f"Playing local file: {song}"}
            
            else:
                # Use playerctl for general media control
                cmd = ["playerctl", "play"]
                subprocess.run(cmd, check=True)
                return {"success": True, "message": "Resumed music playback"}
                
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to play music: {e}"}
    
    async def _pause_music(self) -> Dict[str, Any]:
        """Pause music playback"""
        try:
            cmd = ["playerctl", "pause"]
            subprocess.run(cmd, check=True)
            return {"success": True, "message": "Music paused"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to pause music: {e}"}
    
    async def _stop_music(self) -> Dict[str, Any]:
        """Stop music playback"""
        try:
            cmd = ["playerctl", "stop"]
            subprocess.run(cmd, check=True)
            return {"success": True, "message": "Music stopped"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to stop music: {e}"}
    
    async def _next_track(self) -> Dict[str, Any]:
        """Skip to next track"""
        try:
            cmd = ["playerctl", "next"]
            subprocess.run(cmd, check=True)
            return {"success": True, "message": "Skipped to next track"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to skip track: {e}"}
    
    async def _previous_track(self) -> Dict[str, Any]:
        """Skip to previous track"""
        try:
            cmd = ["playerctl", "previous"]
            subprocess.run(cmd, check=True)
            return {"success": True, "message": "Skipped to previous track"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to skip track: {e}"}

class VideoPlaybackExecutor(BaseCapabilityExecutor):
    """Executor for video playback operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute video playback operation"""
        try:
            action = parameters.get('action', 'play')
            video_url = parameters.get('video_url', '')
            file_path = parameters.get('file_path', '')
            quality = parameters.get('quality', 'best')
            
            if action == "play":
                if video_url:
                    return await self._play_video_url(video_url, quality)
                elif file_path:
                    return await self._play_video_file(file_path)
                else:
                    return {"success": False, "error": "No video URL or file path provided"}
            elif action == "pause":
                return await self._pause_video()
            elif action == "stop":
                return await self._stop_video()
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing video playback: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if video playback can be executed"""
        action = parameters.get('action', 'play')
        return action in ['play', 'pause', 'stop']
    
    async def _play_video_url(self, video_url: str, quality: str) -> Dict[str, Any]:
        """Play video from URL"""
        try:
            if "youtube.com" in video_url or "youtu.be" in video_url:
                # Use youtube-dl for YouTube videos
                cmd = ["youtube-dl", "-f", quality, video_url, "--exec", "mpv {}"]
                subprocess.Popen(cmd)
                return {"success": True, "message": f"Playing YouTube video: {video_url}"}
            else:
                # Use mpv for direct video URLs
                cmd = ["mpv", video_url]
                subprocess.Popen(cmd)
                return {"success": True, "message": f"Playing video: {video_url}"}
                
        except Exception as e:
            return {"success": False, "error": f"Failed to play video URL: {e}"}
    
    async def _play_video_file(self, file_path: str) -> Dict[str, Any]:
        """Play video from local file"""
        try:
            cmd = ["mpv", file_path]
            subprocess.Popen(cmd)
            return {"success": True, "message": f"Playing video file: {file_path}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to play video file: {e}"}
    
    async def _pause_video(self) -> Dict[str, Any]:
        """Pause video playback"""
        try:
            cmd = ["playerctl", "pause"]
            subprocess.run(cmd, check=True)
            return {"success": True, "message": "Video paused"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to pause video: {e}"}
    
    async def _stop_video(self) -> Dict[str, Any]:
        """Stop video playback"""
        try:
            cmd = ["playerctl", "stop"]
            subprocess.run(cmd, check=True)
            return {"success": True, "message": "Video stopped"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to stop video: {e}"}

class BrowserControlExecutor(BaseCapabilityExecutor):
    """Executor for browser control operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute browser control operation"""
        try:
            action = parameters.get('action', 'open')
            url = parameters.get('url', '')
            query = parameters.get('query', '')
            browser = parameters.get('browser', 'chrome')
            incognito = parameters.get('incognito', False)
            
            if action == "open":
                if url:
                    return await self._open_url(url, browser, incognito)
                elif query:
                    return await self._search_web(query, browser)
                else:
                    return {"success": False, "error": "No URL or search query provided"}
            elif action == "close":
                return await self._close_browser()
            elif action == "new_tab":
                return await self._new_tab(url, browser)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing browser control: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if browser control can be executed"""
        action = parameters.get('action', 'open')
        
        if action not in ['open', 'close', 'new_tab']:
            return False
        
        # For open action, require either URL or query
        if action == 'open':
            url = parameters.get('url', '')
            query = parameters.get('query', '')
            return bool(url or query)
        
        return True
    
    async def _open_url(self, url: str, browser: str, incognito: bool) -> Dict[str, Any]:
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
                    # Use default browser
                    webbrowser.open(url)
                    return {"success": True, "message": f"Opened {url} in default browser"}
            else:
                if browser == "chrome":
                    cmd = ["google-chrome", url]
                elif browser == "firefox":
                    cmd = ["firefox", url]
                else:
                    # Use default browser
                    webbrowser.open(url)
                    return {"success": True, "message": f"Opened {url} in default browser"}
            
            if incognito and browser == "chrome":
                cmd.append("--incognito")
            elif incognito and browser == "firefox":
                cmd.append("--private-window")
            
            subprocess.Popen(cmd)
            return {"success": True, "message": f"Opened {url} in {browser}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to open URL: {e}"}
    
    async def _search_web(self, query: str, browser: str) -> Dict[str, Any]:
        """Search the web"""
        try:
            search_url = f"https://www.google.com/search?q={query}"
            return await self._open_url(search_url, browser, False)
        except Exception as e:
            return {"success": False, "error": f"Failed to search web: {e}"}
    
    async def _close_browser(self) -> Dict[str, Any]:
        """Close browser"""
        try:
            if platform.system() == "Windows":
                subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], check=False)
                subprocess.run(["taskkill", "/f", "/im", "firefox.exe"], check=False)
            else:
                subprocess.run(["pkill", "chrome"], check=False)
                subprocess.run(["pkill", "firefox"], check=False)
            
            return {"success": True, "message": "Browser closed"}
        except Exception as e:
            return {"success": False, "error": f"Failed to close browser: {e}"}
    
    async def _new_tab(self, url: str, browser: str) -> Dict[str, Any]:
        """Open new tab"""
        try:
            if url:
                return await self._open_url(url, browser, False)
            else:
                # Open new tab with default page
                if platform.system() == "Windows":
                    if browser == "chrome":
                        subprocess.run(["start", "chrome", "--new-tab"], check=True)
                    elif browser == "firefox":
                        subprocess.run(["start", "firefox", "--new-tab"], check=True)
                else:
                    if browser == "chrome":
                        subprocess.run(["google-chrome", "--new-tab"], check=True)
                    elif browser == "firefox":
                        subprocess.run(["firefox", "--new-tab"], check=True)
                
                return {"success": True, "message": f"Opened new tab in {browser}"}
                
        except Exception as e:
            return {"success": False, "error": f"Failed to open new tab: {e}"}

class YouTubeControlExecutor(BaseCapabilityExecutor):
    """Executor for YouTube-specific operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute YouTube operation"""
        try:
            action = parameters.get('action', 'search')
            query = parameters.get('query', '')
            video_url = parameters.get('video_url', '')
            quality = parameters.get('quality', 'best')
            audio_only = parameters.get('audio_only', False)
            
            if action == "search":
                return await self._search_youtube(query)
            elif action == "play":
                return await self._play_youtube_video(video_url, quality, audio_only)
            elif action == "download":
                return await self._download_youtube_video(video_url, quality, audio_only)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing YouTube control: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if YouTube operation can be executed"""
        action = parameters.get('action', 'search')
        return action in ['search', 'play', 'download']
    
    async def _search_youtube(self, query: str) -> Dict[str, Any]:
        """Search YouTube for videos"""
        try:
            cmd = [
                "youtube-dl", "--get-title", "--get-url",
                f"ytsearch5:{query}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            lines = result.stdout.strip().split('\n')
            videos = []
            
            for i in range(0, len(lines), 2):
                if i + 1 < len(lines):
                    videos.append({
                        "title": lines[i],
                        "url": lines[i + 1]
                    })
            
            return {"success": True, "data": videos, "message": f"Found {len(videos)} videos for '{query}'"}
            
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to search YouTube: {e}"}
    
    async def _play_youtube_video(self, video_url: str, quality: str, audio_only: bool) -> Dict[str, Any]:
        """Play YouTube video"""
        try:
            if audio_only:
                cmd = [
                    "youtube-dl", "--extract-audio", "--audio-format", "mp3",
                    video_url, "--exec", "mpv {}"
                ]
            else:
                cmd = [
                    "youtube-dl", "-f", quality, video_url, "--exec", "mpv {}"
                ]
            
            subprocess.Popen(cmd)
            return {"success": True, "message": f"Playing YouTube video: {video_url}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to play YouTube video: {e}"}
    
    async def _download_youtube_video(self, video_url: str, quality: str, audio_only: bool) -> Dict[str, Any]:
        """Download YouTube video"""
        try:
            output_path = parameters.get('output_path', './downloads')
            
            if audio_only:
                cmd = [
                    "youtube-dl", "--extract-audio", "--audio-format", "mp3",
                    "-o", f"{output_path}/%(title)s.%(ext)s", video_url
                ]
            else:
                cmd = [
                    "youtube-dl", "-f", quality,
                    "-o", f"{output_path}/%(title)s.%(ext)s", video_url
                ]
            
            subprocess.run(cmd, check=True)
            return {"success": True, "message": f"Downloaded YouTube video to {output_path}"}
            
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to download YouTube video: {e}"}

class MediaFileExecutor(BaseCapabilityExecutor):
    """Executor for media file operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute media file operation"""
        try:
            action = parameters.get('action', 'convert')
            input_file = parameters.get('input_file', '')
            output_format = parameters.get('output_format', 'mp4')
            output_file = parameters.get('output_file', '')
            
            if action == "convert":
                return await self._convert_media(input_file, output_format, output_file)
            elif action == "extract_audio":
                return await self._extract_audio(input_file, output_file)
            elif action == "get_info":
                return await self._get_media_info(input_file)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing media file operation: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if media file operation can be executed"""
        action = parameters.get('action', 'convert')
        return action in ['convert', 'extract_audio', 'get_info']
    
    async def _convert_media(self, input_file: str, output_format: str, output_file: str) -> Dict[str, Any]:
        """Convert media file format"""
        try:
            if not output_file:
                output_file = input_file.rsplit('.', 1)[0] + f'.{output_format}'
            
            cmd = [
                "ffmpeg", "-i", input_file,
                "-c:v", "libx264", "-crf", "23",
                output_file
            ]
            
            subprocess.run(cmd, check=True)
            return {"success": True, "message": f"Converted {input_file} to {output_file}"}
            
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to convert media: {e}"}
    
    async def _extract_audio(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """Extract audio from video file"""
        try:
            if not output_file:
                output_file = input_file.rsplit('.', 1)[0] + '.mp3'
            
            cmd = [
                "ffmpeg", "-i", input_file,
                "-vn", "-acodec", "mp3",
                output_file
            ]
            
            subprocess.run(cmd, check=True)
            return {"success": True, "message": f"Extracted audio to {output_file}"}
            
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to extract audio: {e}"}
    
    async def _get_media_info(self, input_file: str) -> Dict[str, Any]:
        """Get media file information"""
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", input_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            info = json.loads(result.stdout)
            
            return {"success": True, "data": info, "message": f"Retrieved info for {input_file}"}
            
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to get media info: {e}"}

# Export all executors
__all__ = [
    'MusicPlaybackExecutor',
    'VideoPlaybackExecutor',
    'BrowserControlExecutor',
    'YouTubeControlExecutor',
    'MediaFileExecutor'
]
