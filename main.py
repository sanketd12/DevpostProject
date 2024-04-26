from dotenv import load_dotenv
import os
load_dotenv()
import requests
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID') ## put this and .env in readMe
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
TO_NUMBER = os.getenv('TO_NUMBER')  # You might want to set this per-user basis
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/weather'



# Function to get weather update
def get_weather_update():
    params = {
        'q': 'Charlottesville,us',  # City and country code
        'appid': WEATHER_API_KEY,
        'units': 'metric'
    }
    response = requests.get(WEATHER_API_URL, params=params)
    data = response.json()
    # Customize your message based on the data received
    weather_description = data['weather'][0]['description']
    return f"Current weather in Charlottesville: {weather_description}"

# Function to send SMS
def send_sms(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_NUMBER,
        to=TO_NUMBER
    )

# Main function to execute the script
def main():
    print(os.environ)
    weather_message = get_weather_update()
    send_sms(weather_message)
    print("SMS sent!")

if __name__ == '__main__':
    main()