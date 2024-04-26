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


# Function to fetch current weather data including UV index
def fetch_weather_data(api_key, location):
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        'lat': location['latitude'],
        'lon': location['longitude'],
        'appid': api_key,
        'exclude': 'minutely,hourly,daily,alerts',
        'units': 'metric'
    }
    response = requests.get(url, params=params)
    return response.json()


# Function to send SMS with weather and sun protection advice
def send_weather_sms(weather_data):
    if 'current' in weather_data:
        temp = weather_data['current']['temp']
        weather_description = weather_data['current']['weather'][0]['description']
        uvi = weather_data['current']['uvi']
        sun_protection_advice = determine_sun_protection(uvi)

        message = (f"Current Weather in Charlottesville: {weather_description}, Temp: {temp}°C.\n"
                   f"UV Index: {uvi}. {sun_protection_advice}")

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_NUMBER,
            to=TO_NUMBER
        )
        print("SMS sent with current weather update and sun protection advice!")


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


# Main function to execute the script
def main():
    location = {'latitude': 38.0293, 'longitude': -78.4767}  # Charlottesville, VA coordinates
    weather_data = fetch_weather_data(WEATHER_API_KEY, location)
    send_weather_sms(weather_data)


if __name__ == '__main__':
    main()
