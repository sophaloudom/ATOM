import json
from urllib.request import urlopen
from django.core.cache import cache

def weather(city='auckland'):
    latitude, longitude = (-41.29, 174.78) if city == 'wellington' else (-36.85, 174.76)
    key = f'weather_{city}'
    cached = cache.get(key)
    if cached: return cached
    try:
        with urlopen(f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,weather_code,wind_speed_10m&timezone=Pacific%2FAuckland', timeout=5) as response:
            current = json.load(response)['current']
        result = {'temperature': round(current['temperature_2m']), 'wind': current['wind_speed_10m'], 'live': True, 'description': 'Clear skies' if current['weather_code'] == 0 else ('Partly cloudy' if current['weather_code'] <= 3 else 'Foggy' if current['weather_code'] <= 48 else 'Rainy' if current['weather_code'] <= 67 else 'Snow / showers' if current['weather_code'] <= 86 else 'Thunderstorms'), 'warning': current['wind_speed_10m'] >= 50}
        cache.set(key, result, 600)
        return result
    except (OSError, ValueError, KeyError):
        return {'temperature': 19, 'wind': 14, 'live': False, 'description': 'Partly cloudy', 'warning': False}
