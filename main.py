from dotenv import load_dotenv
import os
import requests
from twilio.rest import Client

# Load environment variables
load_dotenv()

# API and Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
TO_NUMBER = os.getenv('TO_NUMBER')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')


def fetch_weather_data(api_key, location):
    """Fetches current weather data and hourly forecast data for energy predictions."""
    current_url = "https://api.openweathermap.org/data/3.0/onecall"
    forecast_url = "http://api.weatherapi.com/v1/forecast.json"

    # Parameters for current weather
    current_params = {
        'lat': location['latitude'],
        'lon': location['longitude'],
        'appid': api_key,
        'exclude': 'minutely,hourly,daily,alerts',
        'units': 'metric'
    }
    # Parameters for forecast weather
    forecast_params = {
        'key': api_key,
        'q': f"{location['latitude']},{location['longitude']}",
        'days': 3,
        'aqi': 'no',
        'alerts': 'no'
    }

    current_response = requests.get(current_url, params=current_params)
    forecast_response = requests.get(forecast_url, params=forecast_params)
    return current_response.json(), forecast_response.json()


def analyze_energy_opportunities(weather_data):
    """Extracts relevant parameters for renewable energy predictions from hourly forecasts."""
    if 'forecast' not in weather_data or 'forecastday' not in weather_data['forecast']:
        print("No forecast data available.")
        return [], []

    solar_recommendations = []
    wind_recommendations = []
    for day in weather_data['forecast']['forecastday']:
        for hour in day['hour']:
            if hour['uv'] > 3 and hour['cloud'] < 20:
                solar_recommendations.append(hour['time'])
            if hour['wind_kph'] / 3.6 > 5.5:  # Converting km/h to m/s
                wind_recommendations.append(hour['time'])
    return solar_recommendations, wind_recommendations


def send_weather_sms(current_data, solar_rec, wind_rec):
    """Sends an SMS with current weather, UV index, and energy usage recommendations."""
    if 'current' in current_data:
        temp = current_data['current']['temp']
        weather_description = current_data['current']['weather'][0]['description']
        uvi = current_data['current']['uvi']
        sun_protection_advice = determine_sun_protection(uvi)

        message = (f"Current Weather in Charlottesville: {weather_description}, Temp: {temp}°C.\n"
                   f"UV Index: {uvi}. {sun_protection_advice}\n"
                   f"Optimal times for solar energy today: {', '.join(solar_rec)}\n"
                   f"Optimal times for wind energy today: {', '.join(wind_rec)}")

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_NUMBER,
            to=TO_NUMBER
        )
        print("SMS sent with weather, UV, and energy recommendations!")


def determine_sun_protection(uvi):
    if uvi < 3:
        return "Low UV index. No special protection needed."
    elif uvi < 6:
        return "Moderate UV index. Wear sunglasses on bright days."
    elif uvi < 8:
        return "High UV index. Wear sunscreen, a hat, and sunglasses."
    elif uvi < 11:
        return "Very high UV index. Avoid the sun within three hours of solar noon."
    else:
        return "Extreme UV index. Stay out of the sun, wear sunscreen, a hat, and sunglasses, and be very cautious."


def main():
    location = {'latitude': 38.0293, 'longitude': -78.4767}  # Charlottesville, VA coordinates
    current_weather, forecast_weather = fetch_weather_data(WEATHER_API_KEY, location)
    solar_rec, wind_rec = analyze_energy_opportunities(forecast_weather)
    send_weather_sms(current_weather, solar_rec, wind_rec)


if __name__ == '__main__':
    main()
