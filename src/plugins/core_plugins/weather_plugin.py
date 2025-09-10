"""
Weather Plugin for JARVIS Computer Assistant
Provides weather information and forecasts
"""

import asyncio
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from ..base_plugin import BasePlugin, PluginInfo, PluginType, PluginConfig


class WeatherPlugin(BasePlugin):
    """Weather information plugin"""
    
    PLUGIN_INFO = PluginInfo(
        name="weather",
        version="1.0.0",
        description="Provides weather information and forecasts",
        author="JARVIS Team",
        plugin_type=PluginType.UTILITY,
        dependencies=[],
        config_schema={
            "type": "object",
            "properties": {
                "api_key": {"type": "string", "description": "OpenWeatherMap API key"},
                "default_city": {"type": "string", "description": "Default city for weather"},
                "units": {"type": "string", "enum": ["metric", "imperial", "kelvin"], "default": "metric"},
                "language": {"type": "string", "default": "en"}
            },
            "required": ["api_key"]
        }
    )
    
    PRIORITY = 50
    
    def __init__(self, plugin_info: PluginInfo, config: PluginConfig = None):
        super().__init__(plugin_info, config)
        self.api_key = None
        self.default_city = "Istanbul"
        self.units = "metric"
        self.language = "en"
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self._cache = {}
        self._cache_duration = 300  # 5 minutes
        
    async def _initialize(self) -> bool:
        """Initialize weather plugin"""
        try:
            # Load configuration
            settings = self.config.settings or {}
            self.api_key = settings.get("api_key")
            self.default_city = settings.get("default_city", "Istanbul")
            self.units = settings.get("units", "metric")
            self.language = settings.get("language", "en")
            
            if not self.api_key:
                self.logger.warning("No API key provided for weather plugin")
                return False
            
            self.logger.info(f"Weather plugin initialized for {self.default_city}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize weather plugin: {e}")
            return False
    
    async def _cleanup(self) -> None:
        """Cleanup weather plugin"""
        self._cache.clear()
        self.logger.info("Weather plugin cleaned up")
    
    async def _start(self) -> bool:
        """Start weather plugin"""
        self.logger.info("Weather plugin started")
        return True
    
    async def _stop(self) -> None:
        """Stop weather plugin"""
        self.logger.info("Weather plugin stopped")
    
    async def handle_voice_command(self, command: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Handle weather-related voice commands"""
        command_lower = command.lower()
        
        if any(keyword in command_lower for keyword in ["weather", "hava", "temperature", "sıcaklık"]):
            try:
                city = self._extract_city_from_command(command)
                weather_data = await self.get_current_weather(city)
                
                if weather_data:
                    return self._format_weather_response(weather_data)
                else:
                    return "Sorry, I couldn't get weather information right now."
                    
            except Exception as e:
                self.logger.error(f"Error handling weather command: {e}")
                return "Sorry, there was an error getting weather information."
        
        return None
    
    def _extract_city_from_command(self, command: str) -> str:
        """Extract city name from voice command"""
        # Simple city extraction - can be improved with NLP
        cities = ["istanbul", "ankara", "izmir", "london", "paris", "new york", "tokyo"]
        
        command_lower = command.lower()
        for city in cities:
            if city in command_lower:
                return city.title()
        
        return self.default_city
    
    async def get_current_weather(self, city: str = None) -> Optional[Dict[str, Any]]:
        """Get current weather for a city"""
        try:
            city = city or self.default_city
            cache_key = f"current_{city}"
            
            # Check cache
            if cache_key in self._cache:
                cached_data, timestamp = self._cache[cache_key]
                if datetime.now().timestamp() - timestamp < self._cache_duration:
                    return cached_data
            
            # Make API request
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": self.units,
                "lang": self.language
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process and cache data
            weather_data = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"].get("deg", 0),
                "visibility": data.get("visibility", 0),
                "cloudiness": data["clouds"]["all"],
                "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
                "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the data
            self._cache[cache_key] = (weather_data, datetime.now().timestamp())
            
            return weather_data
            
        except Exception as e:
            self.logger.error(f"Error getting weather data for {city}: {e}")
            return None
    
    async def get_weather_forecast(self, city: str = None, days: int = 5) -> Optional[Dict[str, Any]]:
        """Get weather forecast for a city"""
        try:
            city = city or self.default_city
            cache_key = f"forecast_{city}_{days}"
            
            # Check cache
            if cache_key in self._cache:
                cached_data, timestamp = self._cache[cache_key]
                if datetime.now().timestamp() - timestamp < self._cache_duration:
                    return cached_data
            
            # Make API request
            url = f"{self.base_url}/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": self.units,
                "lang": self.language,
                "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process forecast data
            forecast_data = {
                "city": data["city"]["name"],
                "country": data["city"]["country"],
                "forecasts": []
            }
            
            for item in data["list"][:days * 8]:
                forecast_item = {
                    "datetime": datetime.fromtimestamp(item["dt"]).isoformat(),
                    "temperature": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "humidity": item["main"]["humidity"],
                    "pressure": item["main"]["pressure"],
                    "description": item["weather"][0]["description"],
                    "wind_speed": item["wind"]["speed"],
                    "wind_direction": item["wind"].get("deg", 0),
                    "cloudiness": item["clouds"]["all"],
                    "precipitation": item.get("rain", {}).get("3h", 0)
                }
                forecast_data["forecasts"].append(forecast_item)
            
            # Cache the data
            self._cache[cache_key] = (forecast_data, datetime.now().timestamp())
            
            return forecast_data
            
        except Exception as e:
            self.logger.error(f"Error getting weather forecast for {city}: {e}")
            return None
    
    def _format_weather_response(self, weather_data: Dict[str, Any]) -> str:
        """Format weather data for voice response"""
        try:
            temp = weather_data["temperature"]
            description = weather_data["description"]
            city = weather_data["city"]
            humidity = weather_data["humidity"]
            wind_speed = weather_data["wind_speed"]
            
            unit = "°C" if self.units == "metric" else "°F"
            speed_unit = "m/s" if self.units == "metric" else "mph"
            
            response = f"The weather in {city} is {temp}{unit} with {description}. "
            response += f"Humidity is {humidity}% and wind speed is {wind_speed} {speed_unit}."
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error formatting weather response: {e}")
            return "Weather information is available but couldn't be formatted properly."
    
    def get_commands(self) -> List[str]:
        """Get supported commands"""
        return [
            "what's the weather",
            "hava durumu",
            "temperature",
            "sıcaklık",
            "weather forecast",
            "hava tahmini"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities"""
        return [
            "current_weather",
            "weather_forecast",
            "weather_alerts",
            "city_weather"
        ]
