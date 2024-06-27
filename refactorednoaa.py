import requests
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# Constants
DESIRED_ORDER = [f'{month:02d}-{day:02d}' for month in range(1, 13) for day in range(1, 32) if not (month == 2 and day > 28) and not ((month in {4, 6, 9, 11}) and day > 30)]
API_URL = 'https://www.ncei.noaa.gov/access/services/data/v1'

# Fetch data from API
def fetch_weather_data(url, params):
    response = requests.get(url, params=params)
    return response.json()

# Initialize dictionaries
def init_data_dicts():
    return {date: [] for date in DESIRED_ORDER}

# Populate daily data dictionaries
def populate_daily_data(data, daily_high, daily_low, daily_wind, monthly_dp):
    for entry in data:
        date = entry['DATE'][5:]
        if date == '02-29':
            date = '02-28'
        
        try:
            daily_high[date].append(int(entry['TMAX']))
            daily_low[date].append(int(entry['TMIN']))
            daily_wind[date].append(float(entry['AWND']))
            monthly_dp[date].append(int(entry['ADPT']))
        except KeyError:
            continue

# Filter data for plotting
def filter_data_for_plotting(daily_data, desired_length):
    filtered_data = [values[:desired_length] for values in daily_data.values()]
    return np.array(filtered_data).T

# Calculate average and percentiles
def calculate_statistics(daily_data):
    avg = [np.average(values) for values in daily_data.values()]
    perc90 = [np.percentile(values, 90) for values in daily_data.values()]
    perc10 = [np.percentile(values, 10) for values in daily_data.values()]
    return avg, perc90, perc10

# Smooth data using Savitzky-Golay filter
def smooth_data(data, window_length=31, polyorder=1):
    return savgol_filter(data, window_length=window_length, polyorder=polyorder, mode='wrap')

# Calculate average
def calculate_average(values_list, length, is_max=True):
    total = 0
    subtract_count = 0
    for i in range(length):
        current_values = [row[i] for row in values_list]
        value = max(current_values) if is_max else min(current_values)

        q1 = np.percentile(current_values, 25)
        q3 = np.percentile(current_values, 75)
        iqr = q3 - q1
        lower_bound = q1 - (3 * iqr)
        upper_bound = q3 + (3 * iqr)
        if value >= lower_bound and value <= upper_bound:
            total += value              
        else:     
            subtract_count += 1    
    return total / (length - subtract_count)

# Annotate plot
def annotate_plot(ax, x, y, text, color, marker):
    ax.annotate(f'{x}: {y:.1f}°F', xy=(x, y), ha='center', weight='bold')
    ax.plot(x, y, color, marker=marker)

# Plot data
def plot_temperature_data(dates, smoothed_highs, smoothed_lows, smoothed_avg_high, smoothed_avg_low, maxHigh, minHigh, maxLow, minLow, title):
    plt.figure(figsize=(15, 7.5))
    plt.plot(dates, smoothed_highs['90th'], 'r--', label='90th high')
    plt.plot(dates, smoothed_highs['10th'], 'r--', label='10th high')
    plt.plot(dates, smoothed_lows['90th'], 'b--', label='90th low')
    plt.plot(dates, smoothed_lows['10th'], 'b--', label='10th low')
    plt.plot(dates, smoothed_avg_high, 'r', label='avg high')
    plt.plot(dates, smoothed_avg_low, 'b', label='avg low')

    plt.fill_between(dates, smoothed_avg_high, smoothed_highs['90th'], facecolor='lightcoral', alpha=0.5)
    plt.fill_between(dates, smoothed_avg_high, smoothed_highs['10th'], facecolor='lightcoral', alpha=0.5)
    plt.fill_between(dates, smoothed_avg_low, smoothed_lows['90th'], facecolor='lightskyblue', alpha=0.5)
    plt.fill_between(dates, smoothed_avg_low, smoothed_lows['10th'], facecolor='lightskyblue', alpha=0.5)

    xmaxhigh = dates[np.argmax(smoothed_highs['90th'])]
    ymaxhigh = smoothed_highs['90th'].max()

    xminhigh = dates[np.argmin(smoothed_highs['10th'])]
    yminhigh = smoothed_highs['10th'].min()

    xmaxlow = dates[np.argmax(smoothed_lows['90th'])]
    ymaxlow = smoothed_lows['90th'].max()

    xminlow = dates[np.argmin(smoothed_lows['10th'])]
    yminlow = smoothed_lows['10th'].min()

    xavgmaxhigh = dates[np.argmax(smoothed_avg_high)]
    yavgmaxhigh = smoothed_avg_high.max()

    xavgminhigh = dates[np.argmin(smoothed_avg_high)]
    yavgminhigh = smoothed_avg_high.min()

    xavgmaxlow = dates[np.argmax(smoothed_avg_low)]
    yavgmaxlow = smoothed_avg_low.max()

    xavgminlow = dates[np.argmin(smoothed_avg_low)]
    yavgminlow = smoothed_avg_low.min()

    plt.annotate(f'{xmaxhigh}: {ymaxhigh:.1f}°F', xy=(xmaxhigh, ymaxhigh+1), ha='center', weight='bold')
    plt.plot(xmaxhigh, ymaxhigh, 'r', marker='s')
    plt.annotate(f'{xminhigh}: {yminhigh:.1f}°F', xy=(xminhigh, yminhigh+1), ha='center', weight='bold')
    plt.plot(xminhigh, yminhigh, 'r', marker='s')
    plt.annotate(f'{xmaxlow}: {ymaxlow:.1f}°F', xy=(xmaxlow, ymaxlow-2), ha='center', weight='bold')
    plt.plot(xmaxlow, ymaxlow, 'b', marker='s')
    plt.annotate(f'{xminlow}: {yminlow:.1f}°F', xy=(xminlow, yminlow-2), ha='center', weight='bold')
    plt.plot(xminlow, yminlow, 'b', marker='s')

    plt.annotate(f'{xavgmaxhigh}: {yavgmaxhigh:.1f}°F', xy=(xavgmaxhigh, yavgmaxhigh+1), ha='center', weight='bold')
    plt.plot(xavgmaxhigh, yavgmaxhigh, 'r', marker='o')
    plt.annotate(f'{xavgminhigh}: {yavgminhigh:.1f}°F', xy=(xavgminhigh, yavgminhigh+1), ha='center', weight='bold')
    plt.plot(xavgminhigh, yavgminhigh, 'r', marker='o')
    plt.annotate(f'{xavgmaxlow}: {yavgmaxlow:.1f}°F', xy=(xavgmaxlow, yavgmaxlow-2), ha='center', weight='bold')
    plt.plot(xavgmaxlow, yavgmaxlow, 'b', marker='o')
    plt.annotate(f'{xavgminlow}: {yavgminlow:.1f}°F', xy=(xavgminlow, yavgminlow-2), ha='center', weight='bold')
    plt.plot(xavgminlow, yavgminlow, 'b', marker='o')

    plt.figtext(0.5, 0.01, f'Over the course of the year, the temperature typically varies from {yavgminlow:.0f}°F to {yavgmaxhigh:.0f}°F and is rarely below {yminlow:.0f}°F or above {ymaxhigh:.0f}°F.\nThe mean annual maximum is {maxHigh:.0f}°F and the mean annual minimum is {minLow:.0f}°F.\nThe mean annual cold maximum is {minHigh:.0f}°F and the mean annual warm minimum is {maxLow:.0f}°F.', fontsize=10, ha="center", wrap=True)

    plt.title(title)
    plt.xlabel('Day')
    plt.ylabel('Temperature')
    plt.legend(loc=1)
    plt.tick_params(labelbottom=False)
    plt.show()

# Main function
def main():
    params = {
        'dataset': 'daily-summaries',
        'startDate': '1991-01-01',
        'endDate': '2020-12-31',
        'dataTypes': 'TMAX,TMIN,PRCP,AWND,ADPT',
        'units': 'standard',
        'format': 'json',
        'stations': 'USW00023169' #insert station code here
    }

    weather_data = fetch_weather_data(API_URL, params)
    daily_high, daily_low, daily_wind, monthly_dp = init_data_dicts(), init_data_dicts(), init_data_dicts(), init_data_dicts()
    
    populate_daily_data(weather_data, daily_high, daily_low, daily_wind, monthly_dp)

    daily_high_avg, high_90th, high_10th = calculate_statistics(daily_high)
    daily_low_avg, low_90th, low_10th = calculate_statistics(daily_low)

    dailyHighList = list(daily_high.values())
    dailyLowList = list(daily_low.values())
    
    highLength = min(30, *(len(day) for day in dailyHighList if len(day) != 365))
    lowLength = min(30, *(len(day) for day in dailyLowList if len(day) != 365))

    maxHigh = calculate_average(dailyHighList, highLength, is_max=True)
    minHigh = calculate_average(dailyHighList, highLength, is_max=False)
    maxLow = calculate_average(dailyLowList, lowLength, is_max=True)
    minLow = calculate_average(dailyLowList, lowLength, is_max=False)

    smoothed_highs = {'90th': smooth_data(high_90th), '10th': smooth_data(high_10th)}
    smoothed_lows = {'90th': smooth_data(low_90th), '10th': smooth_data(low_10th)}
    smoothed_avg_high = smooth_data(daily_high_avg)
    smoothed_avg_low = smooth_data(daily_low_avg)

    title = f"Average Annual Temperatures for {weather_data[0]['STATION']}"
    plot_temperature_data(DESIRED_ORDER, smoothed_highs, smoothed_lows, smoothed_avg_high, smoothed_avg_low, maxHigh, minHigh, maxLow, minLow, title)

if __name__ == "__main__":
    main()
