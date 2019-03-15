# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 16:57:16 2019
https://www.kaggle.com/jboysen/quick-tutorial-flatten-nested-json-in-pandas
@author: ntbryant
"""

from noaa_sdk import noaa
import pandas as pd
import json
from pandas.io.json import json_normalize

# get weather forecast
def get_forecast(latitude, longitude):

    n = noaa.NOAA()
    response = n.points_forecast(40.7314, -73.8656, hourly=True)
    forecast = json_normalize(data=response['properties'], record_path='periods')
    
    forecast['datetime'] = pd.to_datetime(forecast['startTime'])
    str.split(forecast['windSpeed'])
    
    forecast.rename(
            columns={
                    'temperature' : 'temp',
                    #'dewpoint.english' : 'dewPt',
                    #'mslp.english' : 'pressure',
                    #'humidity' : 'rh',
                    'windDirection' : 'wdir_cardinal',
                    'windSpeed' : 'wspd',
                    'qpf.english' : 'precip_hrly',
                    'feelslike.english' : 'feels_like',
                    'uvi' : 'uv_index',
                    'wx' : 'wx_phrase',
                    'FCTTIME.mon' : 'month',
                    'FCTTIME.hour' : 'hour',
                    'FCTTIME.mday' : 'day',
                    'FCTTIME.weekday_name' : 'weekday'
      },
      inplace=True
    )
    
    # return the simplified forecast
    forecast = forecast[['datetime', 'month', 'day', 'hour', 'temp', 'wx_phrase',
                        'dewPt','rh', 'pressure',
                        'wdir_cardinal', 'wspd', 'precip_hrly',
                        'feels_like']]
    
    # convert to numeric
    cols = forecast.columns.drop(['datetime', 'wx_phrase', 'wdir_cardinal'])
    forecast[cols] = forecast[cols].apply(pd.to_numeric, errors='coerce')
    
    return(forecast)


latitude = 40.866517
longitude = -124.08284
wund_data = get_forecast(latitude, longitude)