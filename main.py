from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta
from twilio.rest import Client

def fetch_weather_data(api_key, location):
    #gets hourly weather forecast data from WeatherAPI.com
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        'key': api_key,
        'q': f"{location['latitude']},{location['longitude']}",
        'days': 3,
        'aqi': 'no',
        'alerts': 'no'
    }
    response = requests.get(url, params=params)
    return response.json()

def extract_relevant_data(weather_data):
    if 'forecast' not in weather_data or 'forecastday' not in weather_data['forecast']:
        return None

    energy_data = []
    for day in weather_data['forecast']['forecastday']:
        for hour in day['hour']:
            sun_intensity = hour['uv']
            wind_speed = hour['wind_kph'] / 3.6
            cloud_cover = hour['cloud']
            energy_data.append({
                'time': hour['time'],
                'sun_intensity': sun_intensity,
                'wind_speed': wind_speed,
                'cloud_cover': cloud_cover
            })
    return energy_data

def analyze_energy_opportunities(energy_data):
    daily_recommendations = {}
    last_solar_time = None
    solar_period = []

    for data in energy_data:
        current_time = datetime.strptime(data['time'], '%Y-%m-%d %H:%M')
        formatted_time = current_time.strftime('%I:%M %p')
        day_key = current_time.strftime('%B %d, %Y')

        if day_key not in daily_recommendations:
            daily_recommendations[day_key] = []

        if data['sun_intensity'] > 3 and data['cloud_cover'] < 20:
            if last_solar_time and (current_time - last_solar_time <= timedelta(hours=1)):
                solar_period.append(formatted_time)
            else:
                if solar_period:
                    append_period(daily_recommendations, day_key, solar_period)
                solar_period = [formatted_time]
            last_solar_time = current_time
        else:
            if solar_period:
                append_period(daily_recommendations, day_key, solar_period)
                solar_period = []
            last_solar_time = None

    if solar_period:
        append_period(daily_recommendations, day_key, solar_period)

    #make sure days w/ no optimal times of energy still have a msg
    for day in daily_recommendations:
        if not daily_recommendations[day]:
            daily_recommendations[day].append("No optimal times for renewable energy usage.")

    return daily_recommendations

def append_period(daily_recommendations, day_key, solar_period):
    if solar_period[0] == solar_period[-1]:
        daily_recommendations[day_key].append(f"At {solar_period[0]}, solar energy is highly recommended.")
    else:
        daily_recommendations[day_key].append(f"Between {solar_period[0]} and {solar_period[-1]}, solar energy is highly recommended.")

def main():
    load_dotenv()
    api_key = os.getenv('WEATHER_API_KEY')
    location = {'latitude': 38.0293, 'longitude': -78.4767}
    weather_data = fetch_weather_data(api_key, location)
    energy_data = extract_relevant_data(weather_data)

    if energy_data:
        daily_recommendations = analyze_energy_opportunities(energy_data)
        if daily_recommendations:
            messages = ["Here are your energy usage recommendations for the next few days:"]
            for day, recommendations in daily_recommendations.items():
                day_message = f"\n{day}:"
                for rec in recommendations:
                    day_message += f"\n{rec}"
                messages.append(day_message)
            final_message = "\n".join(messages)
        else:
            final_message = "No optimal times for renewable energy usage found based on current weather forecasts."
    else:
        final_message = "No forecast data available."

    #twilio msg setup
    client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    client.messages.create(
        to=os.getenv('TO_NUMBER'),
        from_=os.getenv('TWILIO_NUMBER'),
        body=final_message
    )

if __name__ == '__main__':
    main()
