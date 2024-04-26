from dotenv import load_dotenv
import os
import requests
from twilio.rest import Client

def fetch_weather_data(api_key, location):
    """Fetches hourly weather forecast data from WeatherAPI.com."""
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        'key': api_key,
        'q': f"{location['latitude']},{location['longitude']}",
        'days': 3,  # Fetch forecast for 3 days
        'aqi': 'no',  # Do not include Air Quality Index
        'alerts': 'no'  # Do not include weather alerts
    }
    response = requests.get(url, params=params)
    return response.json()

def extract_relevant_data(weather_data):
    """Extracts relevant parameters for renewable energy predictions."""
    if 'forecast' not in weather_data or 'forecastday' not in weather_data['forecast']:
        return "No forecast data available."

    energy_data = []
    for day in weather_data['forecast']['forecastday']:
        for hour in day['hour']:
            sun_intensity = hour['uv']
            wind_speed = hour['wind_kph'] / 3.6  # Convert wind speed from kph to m/s
            cloud_cover = hour['cloud']
            energy_data.append({
                'time': hour['time'],
                'sun_intensity': sun_intensity,
                'wind_speed': wind_speed,
                'cloud_cover': cloud_cover
            })
    return energy_data

def analyze_energy_opportunities(energy_data):
    """Analyzes weather data to recommend optimal times for using renewable energy."""
    solar_recommendations = []
    wind_recommendations = []
    for data in energy_data:
        if data['sun_intensity'] > 3 and data['cloud_cover'] < 20:
            solar_recommendations.append(data['time'])
        if data['wind_speed'] > 5.5:  # Wind speed threshold in m/s
            wind_recommendations.append(data['time'])
    return solar_recommendations, wind_recommendations

def main():
    load_dotenv()
    api_key = os.getenv('WEATHER_API_KEY')
    location = {'latitude': 38.0293, 'longitude': -78.4767}  # Coordinates for Charlottesville, VA
    weather_data = fetch_weather_data(api_key, location)
    energy_data = extract_relevant_data(weather_data)
    if isinstance(energy_data, str):
        message = energy_data  # Handles the "No forecast data available" case
    else:
        solar_rec, wind_rec = analyze_energy_opportunities(energy_data)
        message = (f"Recommended times for solar energy usage: {solar_rec}\n"
                   f"Recommended times for wind energy usage: {wind_rec}")

    # Set up Twilio client and send SMS
    client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    client.messages.create(
        to=os.getenv('TO_NUMBER'),
        from_=os.getenv('TWILIO_NUMBER'),
        body=message
    )

if __name__ == '__main__':
    main()
