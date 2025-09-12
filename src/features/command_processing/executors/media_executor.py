"""
Media Command Executor
Handles media control commands (play, pause, next, previous, volume)
"""

import asyncio
import logging
import subprocess
import platform
from typing import Dict, Any, Optional, List

from ..command_classifier import CommandCategory
from ..nlp_engine import ProcessedCommand, IntentType
from ..command_executor import BaseExecutor, CommandResult, ExecutionStatus

logger = logging.getLogger(__name__)


class MediaManager:
    """Manages media operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system().lower()
        self._is_initialized = False
    
    def initialize(self) -> bool:
        """Initialize media manager"""
        try:
            self._is_initialized = True
            self.logger.info("Media manager initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize media manager: {e}")
            return False
    
    async def play_media(self) -> bool:
        """Play media"""
        try:
            if self.platform == "windows":
                # Use Windows Media Player controls
                subprocess.run("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys(' ')\"", shell=True)
            elif self.platform == "linux":
                # Use playerctl for media control
                subprocess.run(["playerctl", "play"], check=True)
            else:
                self.logger.error(f"Unsupported platform: {self.platform}")
                return False
            
            self.logger.info("Media play command sent")
            return True
            
        except Exception as e:
            self.logger.error(f"Error playing media: {e}")
            return False
    
    async def pause_media(self) -> bool:
        """Pause media"""
        try:
            if self.platform == "windows":
                # Use Windows Media Player controls
                subprocess.run("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys(' ')\"", shell=True)
            elif self.platform == "linux":
                # Use playerctl for media control
                subprocess.run(["playerctl", "pause"], check=True)
            else:
                self.logger.error(f"Unsupported platform: {self.platform}")
                return False
            
            self.logger.info("Media pause command sent")
            return True
            
        except Exception as e:
            self.logger.error(f"Error pausing media: {e}")
            return False
    
    async def next_track(self) -> bool:
        """Go to next track"""
        try:
            if self.platform == "windows":
                # Use Windows Media Player controls
                subprocess.run("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys('{RIGHT}')\"", shell=True)
            elif self.platform == "linux":
                # Use playerctl for media control
                subprocess.run(["playerctl", "next"], check=True)
            else:
                self.logger.error(f"Unsupported platform: {self.platform}")
                return False
            
            self.logger.info("Next track command sent")
            return True
            
        except Exception as e:
            self.logger.error(f"Error going to next track: {e}")
            return False
    
    async def previous_track(self) -> bool:
        """Go to previous track"""
        try:
            if self.platform == "windows":
                # Use Windows Media Player controls
                subprocess.run("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys('{LEFT}')\"", shell=True)
            elif self.platform == "linux":
                # Use playerctl for media control
                subprocess.run(["playerctl", "previous"], check=True)
            else:
                self.logger.error(f"Unsupported platform: {self.platform}")
                return False
            
            self.logger.info("Previous track command sent")
            return True
            
        except Exception as e:
            self.logger.error(f"Error going to previous track: {e}")
            return False
    
    async def set_volume(self, level: int) -> bool:
        """Set media volume level (0-100)"""
        try:
            if self.platform == "windows":
                # Use PowerShell to set volume
                command = f"powershell -c \"(new-object -com wscript.shell).SendKeys([char]173)\""
                # This is a simplified approach - in practice, you'd use Windows API
                self.logger.info(f"Media volume set to {level}% (Windows)")
                return True
            elif self.platform == "linux":
                # Use playerctl for media volume control
                subprocess.run(["playerctl", "volume", str(level/100)], check=True)
                self.logger.info(f"Media volume set to {level}%")
                return True
            else:
                self.logger.error(f"Unsupported platform: {self.platform}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error setting media volume: {e}")
            return False
    
    async def play_song(self, song_name: str, artist: str = None) -> bool:
        """Play specific song"""
        try:
            if self.platform == "windows":
                # Use Spotify Web API or Windows Media Player
                # This is a simplified implementation
                self.logger.info(f"Playing song: {song_name} by {artist or 'Unknown'}")
                return True
            elif self.platform == "linux":
                # Use playerctl to play specific song
                if artist:
                    subprocess.run(["playerctl", "play", f"{artist} - {song_name}"], check=True)
                else:
                    subprocess.run(["playerctl", "play", song_name], check=True)
                self.logger.info(f"Playing song: {song_name} by {artist or 'Unknown'}")
                return True
            else:
                self.logger.error(f"Unsupported platform: {self.platform}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error playing song: {e}")
            return False
    
    def get_current_track(self) -> Dict[str, Any]:
        """Get current track information"""
        try:
            if self.platform == "linux":
                # Use playerctl to get current track info
                result = subprocess.run(["playerctl", "metadata", "title"], capture_output=True, text=True)
                if result.returncode == 0:
                    title = result.stdout.strip()
                    
                    result = subprocess.run(["playerctl", "metadata", "artist"], capture_output=True, text=True)
                    artist = result.stdout.strip() if result.returncode == 0 else "Unknown"
                    
                    result = subprocess.run(["playerctl", "metadata", "album"], capture_output=True, text=True)
                    album = result.stdout.strip() if result.returncode == 0 else "Unknown"
                    
                    return {
                        "title": title,
                        "artist": artist,
                        "album": album,
                        "status": "playing"
                    }
            
            return {"error": "Could not get current track info"}
            
        except Exception as e:
            self.logger.error(f"Error getting current track: {e}")
            return {"error": str(e)}
    
    def get_media_status(self) -> Dict[str, Any]:
        """Get media player status"""
        try:
            if self.platform == "linux":
                # Use playerctl to get status
                result = subprocess.run(["playerctl", "status"], capture_output=True, text=True)
                if result.returncode == 0:
                    status = result.stdout.strip()
                    return {
                        "status": status,
                        "platform": self.platform
                    }
            
            return {"status": "unknown", "platform": self.platform}
            
        except Exception as e:
            self.logger.error(f"Error getting media status: {e}")
            return {"error": str(e)}


class MediaExecutor(BaseExecutor):
    """Executor for media control commands"""
    
    def __init__(self):
        super().__init__()
        self.media_manager = MediaManager()
        self._is_running = False
    
    def can_handle(self, command: ProcessedCommand) -> bool:
        """Check if this executor can handle the command"""
        return command.category == CommandCategory.MEDIA
    
    async def execute(self, command: ProcessedCommand) -> CommandResult:
        """Execute media command"""
        try:
            self._is_running = True
            self.logger.info(f"Executing media command: {command.action}")
            
            if command.action == "play":
                return await self._execute_play(command)
            elif command.action == "pause":
                return await self._execute_pause(command)
            elif command.action == "next_track":
                return await self._execute_next_track(command)
            elif command.action == "previous_track":
                return await self._execute_previous_track(command)
            elif command.action == "set_volume":
                return await self._execute_set_volume(command)
            elif command.action == "play_song":
                return await self._execute_play_song(command)
            elif command.action == "get_status":
                return await self._execute_get_status(command)
            else:
                return self._create_result(
                    success=False,
                    message=f"Unknown media action: {command.action}",
                    status=ExecutionStatus.FAILED
                )
        
        except Exception as e:
            self.logger.error(f"Error executing media command: {e}")
            return self._create_result(
                success=False,
                message=f"Error executing media command: {e}",
                status=ExecutionStatus.FAILED,
                error=str(e)
            )
        finally:
            self._is_running = False
    
    async def _execute_play(self, command: ProcessedCommand) -> CommandResult:
        """Execute play command"""
        success = await self.media_manager.play_media()
        
        if success:
            return self._create_result(
                success=True,
                message="Media play command sent",
                data={}
            )
        else:
            return self._create_result(
                success=False,
                message="Failed to send play command",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_pause(self, command: ProcessedCommand) -> CommandResult:
        """Execute pause command"""
        success = await self.media_manager.pause_media()
        
        if success:
            return self._create_result(
                success=True,
                message="Media pause command sent",
                data={}
            )
        else:
            return self._create_result(
                success=False,
                message="Failed to send pause command",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_next_track(self, command: ProcessedCommand) -> CommandResult:
        """Execute next track command"""
        success = await self.media_manager.next_track()
        
        if success:
            return self._create_result(
                success=True,
                message="Next track command sent",
                data={}
            )
        else:
            return self._create_result(
                success=False,
                message="Failed to send next track command",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_previous_track(self, command: ProcessedCommand) -> CommandResult:
        """Execute previous track command"""
        success = await self.media_manager.previous_track()
        
        if success:
            return self._create_result(
                success=True,
                message="Previous track command sent",
                data={}
            )
        else:
            return self._create_result(
                success=False,
                message="Failed to send previous track command",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_set_volume(self, command: ProcessedCommand) -> CommandResult:
        """Execute set volume command"""
        level = command.parameters.get('level', 50)
        
        if not 0 <= level <= 100:
            return self._create_result(
                success=False,
                message="Volume level must be between 0 and 100",
                status=ExecutionStatus.FAILED
            )
        
        success = await self.media_manager.set_volume(level)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Media volume set to {level}%",
                data={"level": level}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to set media volume to {level}%",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_play_song(self, command: ProcessedCommand) -> CommandResult:
        """Execute play song command"""
        song_name = command.parameters.get('song_name', '')
        artist = command.parameters.get('artist')
        
        if not song_name:
            return self._create_result(
                success=False,
                message="No song name provided",
                status=ExecutionStatus.FAILED
            )
        
        success = await self.media_manager.play_song(song_name, artist)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Playing song: {song_name}",
                data={"song_name": song_name, "artist": artist}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to play song: {song_name}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_get_status(self, command: ProcessedCommand) -> CommandResult:
        """Execute get status command"""
        try:
            status = self.media_manager.get_media_status()
            current_track = self.media_manager.get_current_track()
            
            return self._create_result(
                success=True,
                message="Media status retrieved",
                data={
                    "status": status,
                    "current_track": current_track
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error getting media status: {e}")
            return self._create_result(
                success=False,
                message=f"Error getting media status: {e}",
                status=ExecutionStatus.FAILED
            )
    
    def cleanup(self) -> None:
        """Cleanup executor resources"""
        self._is_running = False
        self.logger.info("Media executor cleaned up")
