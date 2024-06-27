# Overview

This README file provides a comprehensive overview of the program, including its features, requirements, usage instructions, descriptions of functions, and an example plot. You can customize it further based on specific details or additional features of your program.

# Program

This program fetches weather data from the National Centers for Environmental Information (NCEI) API, processes the data to compute various statistical metrics, and plots the average annual temperature trends.

## Features

- Fetches weather data including daily maximum temperature (TMAX), minimum temperature (TMIN), wind speed (AWND), and dew point (ADPT) from the NCEI API.
- Computes daily averages, 90th and 10th percentiles of temperature data.
- Smooths the temperature data using the Savitzky-Golay filter.
- Calculates annual maximum and minimum temperatures.
- Plots the temperature trends using Matplotlib.

## Requirements

- Python 3.x
- `requests` library
- `numpy` library
- `matplotlib` library
- `scipy` library

You can install the required libraries using:
```sh
pip install requests numpy matplotlib scipy
```

## Usage
1. Set API Parameters:

Update the params dictionary in the main function with the desired start date, end date, data types, units, and station code. The default parameters are set to fetch data from January 1, 1991, to December 31, 2020, for station code 'USW00023169'.

2. Run the Program:

Execute the program by running the following steps:

sh
Copy code
python weather_data_analysis.py
View the Plot:

3. The program will generate a plot showing the average annual temperature trends, along with the 90th and 10th percentiles, and save it as a figure.

## Functions

fetch_weather_data(url, params): Fetches weather data from the NCEI API using the specified URL and parameters.
init_data_dicts(): Initializes dictionaries to store daily weather data.
populate_daily_data(data, daily_high, daily_low, daily_wind, monthly_dp): Populates the daily data dictionaries with the fetched weather data.
calculate_statistics(daily_data): Calculates the average, 90th percentile, and 10th percentile of daily data.
smooth_data(data, window_length=31, polyorder=1): Smooths the data using the Savitzky-Golay filter.
calculate_average(values_list, length, is_max=True): Calculates the average of maximum or minimum values from the provided list.
plot_temperature_data(dates, smoothed_highs, smoothed_lows, smoothed_avg_high, smoothed_avg_low, maxHigh, minHigh, maxLow, minLow, title): Plots the temperature data.

