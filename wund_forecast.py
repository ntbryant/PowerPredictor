# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 16:49:58 2019
from: https://www.wunderground.com/weather/api/d/docs
@author: ntbryant
"""

import pandas as pd
from pandas.io.json import json_normalize
import requests
import config as secret

# get weather forecast
def get_forecast(city, state, api_key):
    
    response = requests.get('http://api.wunderground.com/api/{api_key}/hourly10day/q/{state}/{city}.json'.format(api_key=api_key, state=state, city=city)).json()
    
    forecast = json_normalize(data=response['hourly_forecast'],
                              meta=[['FCTTIME','year', 'mon_padded', 'mday_padded', 'weekday_name_abrev'],
                                    'condition', 
                                    ['dewpoint','english'],
                                    ['feels_like', 'english'],
                                    ['heatindex', 'english'],
                                    'humidity','sky',
                                    ['temp', 'english'],
                                    'uvi',
                                    ['wdir', 'dir'],
                                    ['wspd', 'english'],
                                    'season'])
    
    forecast['datetime'] = pd.to_datetime(forecast['FCTTIME.year'] + forecast['FCTTIME.mon_padded'] + \
            forecast['FCTTIME.mday_padded'] + forecast['FCTTIME.hour_padded'], format='%Y%m%d%H')
    forecast.rename(
            columns={
                    'temp.english' : 'temp',
                    'dewpoint.english' : 'dewPt',
                    'mslp.english' : 'pressure',
                    'humidity' : 'rh',
                    'wdir.dir' : 'wdir_cardinal',
                    'wspd.english' : 'wspd',
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
    
#city = 'Arcata'
#state = 'CA'
#api_key = secret.wund_api_key
#wund_data = get_forecast(city, state, secret.wund_api_key)
