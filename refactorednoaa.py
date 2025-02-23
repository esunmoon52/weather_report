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
def populate_daily_data(data, daily_high, daily_low, daily_rain):
    for entry in data:
        date = entry['DATE'][5:]
        if date == '02-29':
            date = '02-28'
        
        try:
            daily_high[date].append(int(entry['TMAX']))
        except KeyError:
            daily_high[date].append(-1)
            #daily_high[date].append(np.mean(daily_high[date]))
        
        try:
            daily_low[date].append(int(entry['TMIN']))
        except KeyError:
            daily_low[date].append(-1)
            #daily_low[date].append(np.mean(daily_low[date]))
        
        try:
            daily_rain[date].append(float(entry['PRCP']))
        except KeyError:
            #daily_rain[date].append(np.mean(daily_rain[date]))
            daily_rain[date].append(np.mean(0))
    
# Filter data for plotting
def filter_data_for_plotting(daily_data, desired_length):
    filtered_data = [values[:desired_length] for values in daily_data.values()]
    return np.array(filtered_data).T

# Calculate average and percentiles
def calculate_statistics(daily_data):
    avg, perc90, perc10 = [], [], []
    for date in daily_data:
        try:
            avg.append(np.mean([data for data in daily_data[date] if data != -1 and data != 1]))
            perc90.append(np.percentile([data for data in daily_data[date] if data != -1 and data != 1], 90))
            perc10.append(np.percentile([data for data in daily_data[date] if data != -1 and data != 1], 10))
        except IndexError:
            raise Exception("No data collected for the date range provided.")
    return avg, perc90, perc10

# Calculate average and percentiles
def calculate_statistics_avg(daily_data):
    return [np.average(values) for values in daily_data.values()]

# Smooth data using Savitzky-Golay filter
def smooth_data(data, window_length=31, polyorder=1):
    return savgol_filter(data, window_length=window_length, polyorder=polyorder, mode='wrap')

# Calculate average
def calculate_average(values_list, length, is_max=True):
    total = 0
    subtract_count = 0

    new_values_list = [temp for row in values_list for temp in row if temp != -1]

    q1 = np.percentile(new_values_list, 25)
    q3 = np.percentile(new_values_list, 75)
    iqr = q3 - q1
    lower_bound = q1 - (4.5 * iqr)
    upper_bound = q3 + (4.5 * iqr)

    for i in range(length):
        current_values = [row[i] for row in values_list if row[i] != -1]
        if len(current_values) >= 183: #50% * 365 = 182.5
            value = max(current_values) if is_max else min(current_values)
        else:
            subtract_count += 1
            continue

        if (value >= lower_bound and value <= upper_bound) and (value != -1 or value != 1):
            total += value              
        else:     
            subtract_count += 1
    if length != subtract_count:           
        return total / (length - subtract_count)
    else:
        raise Exception("No years to calculate annual temperature extreme.")

# Annotate plot
def annotate_plot(ax, x, y, text, color, marker):
    ax.annotate(f'{x}: {y:.1f}°F', xy=(x, y), ha='center', weight='bold')
    ax.plot(x, y, color, marker=marker)

# Plot data
def plot_temperature_data(dates, smoothed_highs, smoothed_lows, smoothed_avg_high, smoothed_avg_low, maxHigh, minHigh, maxLow, minLow, title):
    fig, ax1 = plt.subplots(figsize=(15,7.5))

    ax1.set_xlabel('Day')
    ax1.set_ylabel('Temperature')

    ax1.plot(dates, smoothed_highs['90th'], 'r--', label='90th high')
    ax1.plot(dates, smoothed_highs['10th'], 'r--', label='10th high')
    ax1.plot(dates, smoothed_lows['90th'], 'b--', label='90th low')
    ax1.plot(dates, smoothed_lows['10th'], 'b--', label='10th low')
    ax1.plot(dates, smoothed_avg_high, 'r', label='avg high')
    ax1.plot(dates, smoothed_avg_low, 'b', label='avg low')

    ax1.fill_between(dates, smoothed_avg_high, smoothed_highs['90th'], facecolor='lightcoral', alpha=0.5)
    ax1.fill_between(dates, smoothed_avg_high, smoothed_highs['10th'], facecolor='lightcoral', alpha=0.5)
    ax1.fill_between(dates, smoothed_avg_low, smoothed_lows['90th'], facecolor='lightskyblue', alpha=0.5)
    ax1.fill_between(dates, smoothed_avg_low, smoothed_lows['10th'], facecolor='lightskyblue', alpha=0.5)

    xmaxhigh = dates[np.argmax(smoothed_highs['90th'])]
    ymaxhigh = smoothed_highs['90th'].max()

    xminhigh = dates[np.argmin(smoothed_highs['10th'])]
    yminhigh = smoothed_highs['10th'].min()

    xmaxcoolhigh = dates[np.argmin(smoothed_highs['90th'])]
    ymaxcoolhigh = smoothed_highs['90th'].min()

    xminwarmhigh = dates[np.argmax(smoothed_highs['10th'])]
    yminwarmhigh = smoothed_highs['10th'].max()

    xmaxlow = dates[np.argmax(smoothed_lows['90th'])]
    ymaxlow = smoothed_lows['90th'].max()

    xminlow = dates[np.argmin(smoothed_lows['10th'])]
    yminlow = smoothed_lows['10th'].min()

    xmaxcoollow = dates[np.argmin(smoothed_lows['90th'])]
    ymaxcoollow = smoothed_lows['90th'].min()

    xminwarmlow = dates[np.argmax(smoothed_lows['10th'])]
    yminwarmlow = smoothed_lows['10th'].max()

    xavgmaxhigh = dates[np.argmax(smoothed_avg_high)]
    yavgmaxhigh = smoothed_avg_high.max()

    xavgminhigh = dates[np.argmin(smoothed_avg_high)]
    yavgminhigh = smoothed_avg_high.min()

    xavgmaxlow = dates[np.argmax(smoothed_avg_low)]
    yavgmaxlow = smoothed_avg_low.max()

    xavgminlow = dates[np.argmin(smoothed_avg_low)]
    yavgminlow = smoothed_avg_low.min()

    #xrainmax = dates[np.argmax(smoothed_avg_rain)]
    #yrainmax = smoothed_avg_rain.max()

    #ax1.set_ylabel('Precipitation')
    #ax1.plot(dates, smoothed_avg_rain, 'g', label='avg prcp')
    #ax1.annotate(f'{xrainmax}: {yrainmax:.3f} in.', xy=(xrainmax, yrainmax+0.002), ha='center', weight='bold')
    #ax1.plot(xrainmax, yrainmax, 'g', marker='^')
    ax1.tick_params(labelbottom=False)
    ax1.set_ylim([yminlow-5, ymaxhigh+5])

    ax1.annotate(f'{xmaxhigh}: {ymaxhigh:.1f}°F', xy=(xmaxhigh, ymaxhigh+1.5), ha='center', weight='bold')
    ax1.plot(xmaxhigh, ymaxhigh, 'r', marker='s')
    ax1.annotate(f'{xminhigh}: {yminhigh:.1f}°F', xy=(xminhigh, yminhigh+1.5), ha='center', weight='bold')
    ax1.plot(xminhigh, yminhigh, 'r', marker='s')
    ax1.annotate(f'{xmaxlow}: {ymaxlow:.1f}°F', xy=(xmaxlow, ymaxlow-2.5), ha='center', weight='bold')
    ax1.plot(xmaxlow, ymaxlow, 'b', marker='s')
    ax1.annotate(f'{xminlow}: {yminlow:.1f}°F', xy=(xminlow, yminlow-2.5), ha='center', weight='bold')
    ax1.plot(xminlow, yminlow, 'b', marker='s')

    ax1.annotate(f'{xmaxcoolhigh}: {ymaxcoolhigh:.1f}°F', xy=(xmaxcoolhigh, ymaxcoolhigh+1.5), ha='center', weight='bold')
    ax1.plot(xmaxcoolhigh, ymaxcoolhigh, 'r', marker='s')
    ax1.annotate(f'{xminwarmhigh}: {yminwarmhigh:.1f}°F', xy=(xminwarmhigh, yminwarmhigh+1.5), ha='center', weight='bold')
    ax1.plot(xminwarmhigh, yminwarmhigh, 'r', marker='s')
    ax1.annotate(f'{xmaxcoollow}: {ymaxcoollow:.1f}°F', xy=(xmaxcoollow, ymaxcoollow-2.5), ha='center', weight='bold')
    ax1.plot(xmaxcoollow, ymaxcoollow, 'b', marker='s')
    ax1.annotate(f'{xminwarmlow}: {yminwarmlow:.1f}°F', xy=(xminwarmlow, yminwarmlow-2.5), ha='center', weight='bold')
    ax1.plot(xminwarmlow, yminwarmlow, 'b', marker='s')

    ax1.annotate(f'{xavgmaxhigh}: {yavgmaxhigh:.1f}°F', xy=(xavgmaxhigh, yavgmaxhigh+1.5), ha='center', weight='bold')
    ax1.plot(xavgmaxhigh, yavgmaxhigh, 'r', marker='o')
    ax1.annotate(f'{xavgminhigh}: {yavgminhigh:.1f}°F', xy=(xavgminhigh, yavgminhigh+1.5), ha='center', weight='bold')
    ax1.plot(xavgminhigh, yavgminhigh, 'r', marker='o')
    ax1.annotate(f'{xavgmaxlow}: {yavgmaxlow:.1f}°F', xy=(xavgmaxlow, yavgmaxlow-2.5), ha='center', weight='bold')
    ax1.plot(xavgmaxlow, yavgmaxlow, 'b', marker='o')
    ax1.annotate(f'{xavgminlow}: {yavgminlow:.1f}°F', xy=(xavgminlow, yavgminlow-2.5), ha='center', weight='bold')
    ax1.plot(xavgminlow, yavgminlow, 'b', marker='o')

    plt.figtext(0.5, 0.01, f'Over the course of the year, the temperature typically varies from {yavgminlow:.0f}°F to {yavgmaxhigh:.0f}°F and is rarely below {yminlow:.0f}°F or above {ymaxhigh:.0f}°F.\nThe mean annual maximum is {maxHigh:.0f}°F and the mean annual minimum is {minLow:.0f}°F.\nThe mean annual cool maximum is {minHigh:.0f}°F and the mean annual warm minimum is {maxLow:.0f}°F.', fontsize=10, ha="center", wrap=True)
    plt.title(title)
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
        'stations': 'USW00023169' #insert station code here, example used is Station: SAN JOSE, CA US
    }

    weather_data = fetch_weather_data(API_URL, params)
    daily_high, daily_low, daily_rain = init_data_dicts(), init_data_dicts(), init_data_dicts()
    
    populate_daily_data(weather_data, daily_high, daily_low, daily_rain)

    daily_high_avg, high_90th, high_10th = calculate_statistics(daily_high)
    daily_low_avg, low_90th, low_10th = calculate_statistics(daily_low)
    #daily_rain_avg = calculate_statistics_avg(daily_rain)

    dailyHighList = list(daily_high.values())
    dailyLowList = list(daily_low.values())

    years = int(params['endDate'][0:4])-int(params['startDate'][0:4])+1
    
    highLength = min(years, *(len(day) for day in dailyHighList if len(day) != 365))
    lowLength = min(years, *(len(day) for day in dailyLowList if len(day) != 365))

    maxHigh = calculate_average(dailyHighList, highLength, is_max=True)
    minHigh = calculate_average(dailyHighList, highLength, is_max=False)
    maxLow = calculate_average(dailyLowList, lowLength, is_max=True)
    minLow = calculate_average(dailyLowList, lowLength, is_max=False)

    smoothed_highs = {'90th': smooth_data(high_90th), '10th': smooth_data(high_10th)}
    smoothed_lows = {'90th': smooth_data(low_90th), '10th': smooth_data(low_10th)}

    smoothed_avg_high = smooth_data(daily_high_avg)
    smoothed_avg_low = smooth_data(daily_low_avg)
    #smoothed_avg_rain = smooth_data(daily_rain_avg)

    title = f"Average Annual Temperatures for {weather_data[0]['STATION']}"
    plot_temperature_data(DESIRED_ORDER, smoothed_highs, smoothed_lows, smoothed_avg_high, smoothed_avg_low, maxHigh, minHigh, maxLow, minLow, title)

if __name__ == "__main__":
    main()
