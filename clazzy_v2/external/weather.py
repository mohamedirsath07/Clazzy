"""
Weather Service Integration
Provides weather context for outfit recommendations
"""

import httpx
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class WeatherCondition:
    """Current weather conditions"""
    temperature_celsius: float
    feels_like_celsius: float
    humidity: int
    description: str
    icon: str
    wind_speed_kmh: float
    rain_probability: int
    uv_index: int

    @property
    def category(self) -> str:
        """Categorize weather for outfit recommendations"""
        if self.temperature_celsius >= 30:
            return "hot"
        elif self.temperature_celsius >= 20:
            return "warm"
        elif self.temperature_celsius >= 10:
            return "mild"
        elif self.temperature_celsius >= 0:
            return "cold"
        else:
            return "freezing"

    @property
    def needs_layers(self) -> bool:
        """Whether outfit should include layers"""
        return self.temperature_celsius < 15 or self.wind_speed_kmh > 30

    @property
    def needs_rain_protection(self) -> bool:
        """Whether to recommend rain protection"""
        return self.rain_probability > 40

    def to_outfit_context(self) -> Dict:
        """Convert to outfit recommendation context"""
        return {
            "weather_category": self.category,
            "temperature_celsius": self.temperature_celsius,
            "needs_layers": self.needs_layers,
            "needs_rain_protection": self.needs_rain_protection,
            "recommended_fabrics": self._get_recommended_fabrics(),
            "avoid_fabrics": self._get_avoid_fabrics(),
            "style_tips": self._get_style_tips()
        }

    def _get_recommended_fabrics(self) -> list:
        """Get recommended fabrics for weather"""
        if self.category == "hot":
            return ["cotton", "linen", "rayon", "lightweight"]
        elif self.category == "warm":
            return ["cotton", "light wool", "breathable synthetics"]
        elif self.category == "mild":
            return ["cotton", "light wool", "denim"]
        elif self.category == "cold":
            return ["wool", "fleece", "cashmere", "down"]
        else:
            return ["wool", "down", "thermal", "insulated"]

    def _get_avoid_fabrics(self) -> list:
        """Get fabrics to avoid in current weather"""
        if self.category == "hot":
            return ["wool", "velvet", "heavy fabrics", "polyester"]
        elif self.category == "freezing":
            return ["cotton", "linen", "thin materials"]
        return []

    def _get_style_tips(self) -> list:
        """Get weather-specific style tips"""
        tips = []

        if self.needs_rain_protection:
            tips.append("Consider a water-resistant jacket or umbrella")

        if self.category == "hot" and self.uv_index > 5:
            tips.append("High UV - consider a hat and sunglasses")

        if self.needs_layers:
            tips.append("Layer up for temperature changes")

        if self.wind_speed_kmh > 40:
            tips.append("Strong winds - avoid loose, flowy items")

        return tips


class WeatherService:
    """
    Weather API integration service
    Supports OpenWeatherMap API
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_current(self, lat: float, lon: float) -> Dict:
        """
        Get current weather for location

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Weather condition context for outfit recommendations
        """
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            data = response.json()

            condition = WeatherCondition(
                temperature_celsius=data["main"]["temp"],
                feels_like_celsius=data["main"]["feels_like"],
                humidity=data["main"]["humidity"],
                description=data["weather"][0]["description"],
                icon=data["weather"][0]["icon"],
                wind_speed_kmh=data["wind"]["speed"] * 3.6,  # m/s to km/h
                rain_probability=data.get("pop", 0) * 100 if "pop" in data else 0,
                uv_index=0  # Not in basic endpoint
            )

            return condition.to_outfit_context()

        except httpx.HTTPStatusError as e:
            logger.error(f"Weather API error: {e}")
            return {"error": str(e), "default": "mild"}
        except Exception as e:
            logger.error(f"Weather fetch failed: {e}")
            return {"error": str(e), "default": "mild"}

    async def get_forecast(self, lat: float, lon: float, hours: int = 24) -> list:
        """Get weather forecast for planning"""
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/forecast",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric",
                    "cnt": hours // 3  # 3-hour intervals
                }
            )
            response.raise_for_status()
            data = response.json()

            forecasts = []
            for item in data["list"]:
                forecasts.append({
                    "time": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "description": item["weather"][0]["description"],
                    "rain_probability": item.get("pop", 0) * 100
                })

            return forecasts

        except Exception as e:
            logger.error(f"Forecast fetch failed: {e}")
            return []

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class MockWeatherService:
    """Mock weather service for development/testing"""

    def __init__(self):
        pass

    async def get_current(self, lat: float, lon: float) -> Dict:
        """Return mock weather data"""
        # Simulate based on month
        month = datetime.now().month

        if month in [12, 1, 2]:  # Winter
            temp = 5
            category = "cold"
        elif month in [3, 4, 5]:  # Spring
            temp = 15
            category = "mild"
        elif month in [6, 7, 8]:  # Summer
            temp = 28
            category = "warm"
        else:  # Fall
            temp = 12
            category = "mild"

        return {
            "weather_category": category,
            "temperature_celsius": temp,
            "needs_layers": temp < 15,
            "needs_rain_protection": False,
            "recommended_fabrics": ["cotton", "wool"],
            "avoid_fabrics": [],
            "style_tips": []
        }

    async def get_forecast(self, lat: float, lon: float, hours: int = 24) -> list:
        """Return mock forecast"""
        return []


def get_weather_service(api_key: Optional[str] = None) -> WeatherService:
    """Factory function for weather service"""
    if api_key:
        return WeatherService(api_key)
    return MockWeatherService()
