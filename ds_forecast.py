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

def get_forecast(latitude, longitude, api_key):

    response = requests.get('https://api.darksky.net/forecast/{api_key}/{latitude},{longitude}?extend=hourly'.format(api_key=api_key, latitude=latitude, longitude=longitude)).json()
    forecast = json_normalize(data=response['hourly'], record_path='data')
    
    forecast.rename(
            columns={
                    'temperature' : 'temp',
                    'dewPoint' : 'dewPt',
                    'pressure' : 'pressure',
                    'humidity' : 'rh',
                    'windBearing' : 'wdir_degree',
                    'windSpeed' : 'wspd',
                    'precipProbability' : 'precip_hrly',
                    'apparentTemperature' : 'feels_like',
                    'uvIndex' : 'uv_index',
                    'summary' : 'wx_phrase',
                    'time' : 'time'
      },
      inplace=True
    )
    
    # adjusting for timezone offset
    offset = response['offset']
    forecast['datetime'] = pd.to_datetime(forecast['time'], unit='s')
    forecast['datetime'] = forecast['datetime'] + pd.Timedelta(hours=offset)
    
    # changing wind direction from degree to cardinal direction
    def degrees_to_cardinal(d):
        dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        ix = int((d + 11.25)/22.5 - 0.02)
        return dirs[ix % 16]
    forecast['wdir_cardinal'] = forecast['wdir_degree'].apply(degrees_to_cardinal)
    
    # return the simplified forecast
    forecast = forecast[['datetime', 'temp', 'wx_phrase',
                        'dewPt','rh', 'pressure',
                        'wdir_cardinal', 'wspd', 'precip_hrly',
                        'feels_like']]
    
    # convert to numeric
    cols = forecast.columns.drop(['datetime', 'wx_phrase', 'wdir_cardinal'])
    forecast[cols] = forecast[cols].apply(pd.to_numeric, errors='coerce')
    
    return(forecast)


#latitude = 40.866517
#longitude = -124.08284
#api_key = secret.ds_key
#ds_data = get_forecast(latitude, longitude, secret.ds_key)
