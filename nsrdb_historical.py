# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 16:25:17 2019
from: https://nsrdb.nrel.gov/api-instructions
@author: ntbryant
"""

import pandas as pd
import config as secret

def get_nsrdb_data(lat, lon, api_key):
    
    attributes = 'ghi,dhi,dni,solar_zenith_angle,clearsky_ghi'
    leap_year = 'true'
    interval = '60'
    utc = 'false'
    your_name = 'John+Smith'
    reason_for_use = 'beta+testing'
    your_affiliation = 'my+institution'
    your_email = 'john.smith@server.com'
    mailing_list = 'false'

    # access data from NSRDB
    df = pd.read_csv('http://developer.nrel.gov/api/solar/nsrdb_psm3_download.csv?wkt=POINT({lon}%20{lat})&names=2017&leap_day={leap}&interval={interval}&utc={utc}&full_name={name}&email={email}&affiliation={affiliation}&mailing_list={mailing_list}&reason={reason}&api_key={api}&attributes={attr}'.format(lat=lat, lon=lon, leap=leap_year, interval=interval, utc=utc, name=your_name, email=your_email, mailing_list=mailing_list, affiliation=your_affiliation, reason=reason_for_use, api=api_key, attr=attributes), skiprows=2)
    
    # Set the time index in the pandas dataframe:
    df = df.set_index(pd.date_range('1/1/2017', freq=interval+'Min', periods=525600/int(interval)))
    
    df.rename(
            columns={
                    'Month' : 'month',
                    'Day' : 'day',
                    'Hour' : 'hour',
                    'GHI' : 'GHI_nsrdb',
                    'DHI' : 'DHI_nsrdb',
                    'DNI' : 'DNI_nsrdb'
      },
      inplace=True
    )
    
    df = df[['month', 'day', 'hour',
             'GHI_nsrdb', 'DHI_nsrdb', 'DNI_nsrdb']]
    return(df)

#latitude = 40.8665166
#longitude = -124.0828396
#api_key = secret.nrel_api_key

#nrel_data = get_nsrdb_data(latitude, longitude, secret.nrel_api_key)
