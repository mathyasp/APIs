import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/weather'


################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    # TODO: Use 'request.args' to retrieve the city & units from the query
    # parameters.
    city = request.args.get('city')
    units = request.args.get('units')

    params = {
        # TODO: Enter query parameters here for the 'appid' (your api key),
        # the city, and the units (metric or imperial).
        # See the documentation here: https://openweathermap.org/current
        'appid': API_KEY,
        'q': city,
        'units': units,
    }

    result_json = requests.get(API_URL, params=params).json()

    # Uncomment the line below to see the results of the API call!
    pp.pprint(result_json)

    # TODO: Replace the empty variables below with their appropriate values.
    # You'll need to retrieve these from the result_json object above.

    # For the sunrise & sunset variables, I would recommend to turn them into
    # datetime objects. You can do so using the `datetime.fromtimestamp()` 
    # function.
    context = {
        'date': datetime.now().strftime("%A, %B %d, %Y"),
        'city': result_json['name'],
        'description': result_json['weather'][0]['description'],
        'temp': result_json['main']['temp'],
        'humidity': result_json['main']['humidity'],
        'wind_speed': result_json['wind']['speed'],
        'sunrise': datetime.fromtimestamp(result_json['sys']['sunrise']).strftime("%I:%M %p"),
        'sunset': datetime.fromtimestamp(result_json['sys']['sunset']).strftime("%I:%M %p"),
        'units_letter': get_letter_for_units(units),
        'icon': 'https://openweathermap.org/img/wn/' + result_json['weather'][0]['icon'] + '@2x.png',
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    # TODO: Use 'request.args' to retrieve the cities & units from the query
    # parameters.
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units')

    # TODO: Make 2 API calls, one for each city. HINT: You may want to write a 
    # helper function for this!
    def api_call(city_input):
        params = {
            'appid': API_KEY,
            'q': city_input,
            'units': units,
        }
        result_json = requests.get(API_URL, params=params).json()
        return result_json

    city1_json = api_call(city1)
    city2_json = api_call(city2)

    # TODO: Pass the information for both cities in the context. Make sure to
    # pass info for the temperature, humidity, wind speed, and sunset time!
    # HINT: It may be useful to create 2 new dictionaries, `city1_info` and 
    # `city2_info`, to organize the data.
    city1_info = {
        'city': city1_json['name'],
        'description': city1_json['weather'][0]['description'],
        'temp': city1_json['main']['temp'],
        'humidity': city1_json['main']['humidity'],
        'wind_speed': city1_json['wind']['speed'],
        'sunrise': datetime.fromtimestamp(city1_json['sys']['sunrise']).strftime("%I:%M %p"),
        'sunset': datetime.fromtimestamp(city1_json['sys']['sunset']).strftime("%I:%M %p"),
        'icon': 'https://openweathermap.org/img/wn/' + city1_json['weather'][0]['icon'] + '@2x.png',
    }

    city2_info = {
        'city': city2_json['name'],
        'description': city2_json['weather'][0]['description'],
        'temp': city2_json['main']['temp'],
        'humidity': city2_json['main']['humidity'],
        'wind_speed': city2_json['wind']['speed'],
        'sunrise': datetime.fromtimestamp(city2_json['sys']['sunrise']).strftime("%I:%M %p"),
        'sunset': datetime.fromtimestamp(city2_json['sys']['sunset']).strftime("%I:%M %p"),
        'icon': 'https://openweathermap.org/img/wn/' + city2_json['weather'][0]['icon'] + '@2x.png',
    }

    context = {
        'date': datetime.now().strftime("%A, %B %d, %Y"),
        'units_letter': get_letter_for_units(units),
        'city1_info': city1_info,
        'city2_info': city2_info,
        'temp_diff': round(abs(city1_info['temp'] - city2_info['temp']), 2),
        'humidity_diff': abs(city1_info['humidity'] - city2_info['humidity']),
        'wind_diff': abs(city1_info['wind_speed'] - city2_info['wind_speed']),
        'sunset_diff': abs(datetime.strptime(city1_info['sunset'], "%I:%M %p") - datetime.strptime(city2_info['sunset'], "%I:%M %p")),
    }

    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
