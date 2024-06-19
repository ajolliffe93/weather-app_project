#Import and install the following 
import openmeteo_requests #%pip install openmeteo-requests
import requests_cache #%pip install requests-cache retry-requests numpy pandas
import pandas as pd #%pip install ipympl
from retry_requests import retry
import matplotlib.pyplot as plt #necessary to plot data
import sys 

def select_variables(hourly_vars, daily_vars):

	params = {
		"latitude": 40.6613,
		"longitude": -73.9463,
		"current": "temperature_2m",
		"hourly": hourly_vars,
		"daily": daily_vars,
		"temperature_unit": "fahrenheit",
		"wind_speed_unit": "mph",
		"timezone": "America/New_York",
		"forecast_days": 1
	}
	
	return params

def get_response(params):

	# More setup
	# Setup the Open-Meteo API client with cache and retry on error
	cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
	retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
	openmeteo = openmeteo_requests.Client(session = retry_session)


	# Obtain user's coordinates. Ideally the user would allow the app to track their location upon opening of the app and this would be done automoatically without the user needing to input anything.
	# This app is tracking the following hourly: temperature, humditiy, precipitation probability and wind speed, and the following daily: temperature, sunrise, susnset, precipitation summary, rain summary, showers summary and snowfall summary. All of these variables are stated here in dictionary form.
	url = "https://api.open-meteo.com/v1/forecast"
	
	responses = openmeteo.weather_api(url, params=params)

	return responses[0]

def print_location_info(response):

	# Process location and get current values.
	print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
	print(f"Elevation {response.Elevation()} m asl")
	print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
	print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

	current = response.Current()
	current_temperature_2m = current.Variables(0).Value()

	print(f"Current time {current.Time()}")
	print(f"Current temperature_2m {current_temperature_2m}")


	# Process hourly data via array and feed data into a dataframe.

def process_hourly(response, hourly_vars):
	hourly = response.Hourly()

	hourly_arrays = []

	for i in range(0, len(hourly_vars)):
		ar = hourly.Variables(i).ValuesAsNumpy() 
		hourly_arrays.append(ar)
	
	hourly_data = {"date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)}
	#create a 4 loop that goes through hourly vars and creates new keys with new values
	hourly_data["temperature_2m"] = hourly_temperature_2m
	hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
	hourly_data["precipitation_probability"] = hourly_precipitation_probability
	hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

	hourly_dataframe = pd.DataFrame(data = hourly_data)
	print(hourly_dataframe)

	#Turn dataframe into a plot
	p = hourly_dataframe.plot(kind='line',
							x = 'date',
							y = ['temperature_2m', 'relative_humidity_2m', 'precipitation_probability', 'wind_speed_10m'])

	# Process daily data via an array
	daily = response.Daily()
	daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
	daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
	daily_sunrise = daily.Variables(2).ValuesAsNumpy()
	daily_sunset = daily.Variables(3).ValuesAsNumpy()
	daily_precipitation_sum = daily.Variables(4).ValuesAsNumpy()
	daily_rain_sum = daily.Variables(5).ValuesAsNumpy()
	daily_showers_sum = daily.Variables(6).ValuesAsNumpy()
	daily_snowfall_sum = daily.Variables(7).ValuesAsNumpy()

	daily_data = {"date": pd.date_range(
		start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
		end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = daily.Interval()),
		inclusive = "left"
	)}
	daily_data["temperature_2m_max"] = daily_temperature_2m_max
	daily_data["temperature_2m_min"] = daily_temperature_2m_min
	daily_data["sunrise"] = daily_sunrise
	daily_data["sunset"] = daily_sunset
	daily_data["precipitation_sum"] = daily_precipitation_sum
	daily_data["rain_sum"] = daily_rain_sum
	daily_data["showers_sum"] = daily_showers_sum
	daily_data["snowfall_sum"] = daily_snowfall_sum

	daily_dataframe = pd.DataFrame(data = daily_data)
	print(daily_dataframe)