"""
Calendar Plugin for JARVIS Computer Assistant
Provides calendar management and scheduling
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, date
from dataclasses import dataclass

from ..base_plugin import BasePlugin, PluginInfo, PluginType, PluginConfig


@dataclass
class CalendarEvent:
    """Calendar event data"""
    title: str
    start_time: datetime
    end_time: datetime
    description: str = ""
    location: str = ""
    attendees: List[str] = None
    all_day: bool = False
    reminder_minutes: int = 15
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []


class CalendarPlugin(BasePlugin):
    """Calendar management plugin"""
    
    PLUGIN_INFO = PluginInfo(
        name="calendar",
        version="1.0.0",
        description="Calendar management and scheduling",
        author="JARVIS Team",
        plugin_type=PluginType.PRODUCTIVITY,
        dependencies=[],
        config_schema={
            "type": "object",
            "properties": {
                "default_reminder_minutes": {"type": "integer", "default": 15},
                "working_hours_start": {"type": "string", "default": "09:00"},
                "working_hours_end": {"type": "string", "default": "17:00"},
                "timezone": {"type": "string", "default": "UTC"}
            }
        }
    )
    
    PRIORITY = 60
    
    def __init__(self, plugin_info: PluginInfo, config: PluginConfig = None):
        super().__init__(plugin_info, config)
        self.default_reminder_minutes = 15
        self.working_hours_start = "09:00"
        self.working_hours_end = "17:00"
        self.timezone = "UTC"
        self._events: List[CalendarEvent] = []
        self._next_event_id = 1
        
    async def _initialize(self) -> bool:
        """Initialize calendar plugin"""
        try:
            # Load configuration
            settings = self.config.settings or {}
            self.default_reminder_minutes = settings.get("default_reminder_minutes", 15)
            self.working_hours_start = settings.get("working_hours_start", "09:00")
            self.working_hours_end = settings.get("working_hours_end", "17:00")
            self.timezone = settings.get("timezone", "UTC")
            
            # Load existing events (in real implementation, this would load from storage)
            await self._load_events()
            
            self.logger.info("Calendar plugin initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize calendar plugin: {e}")
            return False
    
    async def _cleanup(self) -> None:
        """Cleanup calendar plugin"""
        # Save events (in real implementation, this would save to storage)
        await self._save_events()
        self.logger.info("Calendar plugin cleaned up")
    
    async def _start(self) -> bool:
        """Start calendar plugin"""
        self.logger.info("Calendar plugin started")
        return True
    
    async def _stop(self) -> None:
        """Stop calendar plugin"""
        self.logger.info("Calendar plugin stopped")
    
    async def _load_events(self) -> None:
        """Load events from storage"""
        # In a real implementation, this would load from a database or file
        # For now, we'll just initialize with some sample events
        sample_events = [
            CalendarEvent(
                title="Team Meeting",
                start_time=datetime.now().replace(hour=10, minute=0, second=0, microsecond=0),
                end_time=datetime.now().replace(hour=11, minute=0, second=0, microsecond=0),
                description="Weekly team standup",
                location="Conference Room A"
            ),
            CalendarEvent(
                title="Project Deadline",
                start_time=datetime.now() + timedelta(days=7),
                end_time=datetime.now() + timedelta(days=7),
                description="Submit final project deliverables",
                all_day=True
            )
        ]
        
        self._events.extend(sample_events)
        self.logger.info(f"Loaded {len(sample_events)} sample events")
    
    async def _save_events(self) -> None:
        """Save events to storage"""
        # In a real implementation, this would save to a database or file
        self.logger.info(f"Saving {len(self._events)} events")
    
    async def handle_voice_command(self, command: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Handle calendar-related voice commands"""
        command_lower = command.lower()
        
        if any(keyword in command_lower for keyword in ["calendar", "takvim", "schedule", "appointment", "meeting", "toplantı"]):
            try:
                if "today" in command_lower or "bugün" in command_lower:
                    return await self._get_today_events()
                elif "tomorrow" in command_lower or "yarın" in command_lower:
                    return await self._get_tomorrow_events()
                elif "next" in command_lower or "sıradaki" in command_lower:
                    return await self._get_next_event()
                elif "add" in command_lower or "ekle" in command_lower:
                    return "I can help you add events. Please provide the event details."
                else:
                    return await self._get_upcoming_events()
                    
            except Exception as e:
                self.logger.error(f"Error handling calendar command: {e}")
                return "Sorry, I couldn't access your calendar right now."
        
        return None
    
    async def _get_today_events(self) -> str:
        """Get today's events"""
        today = date.today()
        today_events = [
            event for event in self._events
            if event.start_time.date() == today
        ]
        
        if not today_events:
            return "You have no events scheduled for today."
        
        response = f"You have {len(today_events)} event(s) today: "
        for event in sorted(today_events, key=lambda x: x.start_time):
            time_str = event.start_time.strftime("%H:%M")
            response += f"{event.title} at {time_str}, "
        
        return response.rstrip(", ")
    
    async def _get_tomorrow_events(self) -> str:
        """Get tomorrow's events"""
        tomorrow = date.today() + timedelta(days=1)
        tomorrow_events = [
            event for event in self._events
            if event.start_time.date() == tomorrow
        ]
        
        if not tomorrow_events:
            return "You have no events scheduled for tomorrow."
        
        response = f"You have {len(tomorrow_events)} event(s) tomorrow: "
        for event in sorted(tomorrow_events, key=lambda x: x.start_time):
            time_str = event.start_time.strftime("%H:%M")
            response += f"{event.title} at {time_str}, "
        
        return response.rstrip(", ")
    
    async def _get_next_event(self) -> str:
        """Get the next upcoming event"""
        now = datetime.now()
        upcoming_events = [
            event for event in self._events
            if event.start_time > now
        ]
        
        if not upcoming_events:
            return "You have no upcoming events."
        
        next_event = min(upcoming_events, key=lambda x: x.start_time)
        time_until = next_event.start_time - now
        
        if time_until.days > 0:
            time_str = f"in {time_until.days} day(s)"
        elif time_until.seconds > 3600:
            hours = time_until.seconds // 3600
            time_str = f"in {hours} hour(s)"
        else:
            minutes = time_until.seconds // 60
            time_str = f"in {minutes} minute(s)"
        
        return f"Your next event is {next_event.title} {time_str} at {next_event.start_time.strftime('%H:%M')}."
    
    async def _get_upcoming_events(self) -> str:
        """Get upcoming events for the next 7 days"""
        now = datetime.now()
        week_from_now = now + timedelta(days=7)
        
        upcoming_events = [
            event for event in self._events
            if now < event.start_time <= week_from_now
        ]
        
        if not upcoming_events:
            return "You have no events scheduled for the next 7 days."
        
        response = f"You have {len(upcoming_events)} event(s) in the next 7 days: "
        for event in sorted(upcoming_events, key=lambda x: x.start_time):
            date_str = event.start_time.strftime("%A, %B %d")
            time_str = event.start_time.strftime("%H:%M")
            response += f"{event.title} on {date_str} at {time_str}, "
        
        return response.rstrip(", ")
    
    async def add_event(self, title: str, start_time: datetime, end_time: datetime = None,
                       description: str = "", location: str = "", all_day: bool = False) -> bool:
        """Add a new calendar event"""
        try:
            if end_time is None:
                if all_day:
                    end_time = start_time.replace(hour=23, minute=59)
                else:
                    end_time = start_time + timedelta(hours=1)
            
            event = CalendarEvent(
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=description,
                location=location,
                all_day=all_day,
                reminder_minutes=self.default_reminder_minutes
            )
            
            self._events.append(event)
            self.logger.info(f"Added event: {title}")
            
            # Emit event
            self.emit_event("calendar_event_added", {
                "title": title,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding event: {e}")
            return False
    
    async def get_events(self, start_date: datetime = None, end_date: datetime = None) -> List[CalendarEvent]:
        """Get events within a date range"""
        try:
            if start_date is None:
                start_date = datetime.now()
            if end_date is None:
                end_date = start_date + timedelta(days=30)
            
            return [
                event for event in self._events
                if start_date <= event.start_time <= end_date
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting events: {e}")
            return []
    
    def get_commands(self) -> List[str]:
        """Get supported commands"""
        return [
            "calendar",
            "takvim",
            "schedule",
            "appointments",
            "meetings",
            "toplantılar",
            "today's events",
            "bugünkü etkinlikler",
            "tomorrow's events",
            "yarının etkinlikleri",
            "next event",
            "sıradaki etkinlik"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities"""
        return [
            "event_management",
            "schedule_viewing",
            "event_creation",
            "reminder_system",
            "calendar_integration"
        ]
