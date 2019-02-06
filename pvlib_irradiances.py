# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 20:15:17 2019
from: https://pvlib-python.readthedocs.io/en/latest/forecasts.html
@author: ntbryant
"""

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime
from pytz import timezone
import matplotlib.pyplot as plt
import pandas as pd
import pvlib
from pvlib import clearsky, atmosphere, solarposition
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.modelchain import ModelChain
from pvlib.forecast import GFS, NAM, NDFD, HRRR, RAP

import itertools
import matplotlib.pyplot as plt
import pandas as pd
import pvlib
import calendar
import os
import tables


def get_pvlib_data(latitude, longitude, tz, altitude, city, start_time, end_time):
    
    # getting turbidity tables
    pvlib_path = os.path.dirname(os.path.abspath(pvlib.clearsky.__file__))
    filepath = os.path.join(pvlib_path, 'data', 'LinkeTurbidities.h5')
    
    def plot_turbidity_map(month, vmin=1, vmax=100):
        plt.figure();
        with tables.open_file(filepath) as lt_h5_file:
            ltdata = lt_h5_file.root.LinkeTurbidity[:, :, month-1]
        plt.imshow(ltdata, vmin=vmin, vmax=vmax);
        # data is in units of 20 x turbidity
        plt.title('Linke turbidity x 20, ' + calendar.month_name[month]);
        plt.colorbar(shrink=0.5);
        plt.tight_layout();

    plot_turbidity_map(1)
    
    plot_turbidity_map(7)
    
    # getting clearsky estimates
    loc = Location(latitude, longitude, tz, altitude, city)
    times = pd.DatetimeIndex(start=start_time, end=end_time, freq='H', tz=loc.tz)
    cs = loc.get_clearsky(times)
    
    # getting pvlib forecasted irradiance based on cloud_cover
    #irrad_vars = ['ghi', 'dni', 'dhi']
    model = GFS()
    raw_data = model.get_data(latitude, longitude, start_time, end_time)
    data = raw_data
    
    # rename the columns according the key/value pairs in model.variables.
    data = model.rename(data)

    # convert temperature
    data['temp_air'] = model.kelvin_to_celsius(data['temp_air'])
    
    # convert wind components to wind speed
    data['wind_speed'] = model.uv_to_speed(data)
    
    # calculate irradiance estimates from cloud cover.
    # uses a cloud_cover to ghi to dni model or a
    # uses a cloud cover to transmittance to irradiance model.
    irrad_data = model.cloud_cover_to_irradiance(data['total_clouds'])
    
    # correcting timezone
    data.index = data.index.tz_convert('America/Los_Angeles')
    irrad_data.index = irrad_data.index.tz_convert('America/Los_Angeles')
    
    # joining cloud_cover and irradiance data frames
    data = data.join(irrad_data, how='outer')
    
    # renaming irradiance estimates
    cs.rename(
            columns={
                    'ghi' : 'GHI_clearsky',
                    'dhi' : 'DHI_clearsky',
                    'dni' : 'DNI_clearsky'
      },
      inplace=True
    )
    
    data.rename(
            columns={
                    'ghi' : 'GHI_pvlib',
                    'dhi' : 'DHI_pvlib',
                    'dni' : 'DNI_pvlib'
      },
      inplace=True
    )
    
    # joining clearsky with cloud_cover irradiances
    data = data.join(cs, how='outer')
    return(data)


#location_input = 'Arcata, CA'
#
## convert location to latitude and longitude
#geolocator = Nominatim(user_agent="powerpredictor")
#location = geolocator.geocode(location_input)
#
#city, state = location_input.split(',')
#city.strip()
#state.strip()
#
#tf = TimezoneFinder()
#
#latitude = location.latitude
#longitude = location.longitude
#tz = tf.timezone_at(lng=location.longitude, lat=location.latitude)
#altitude = location.altitude
#city = city
#start_time = pd.Timestamp('2019-01-30 21:00:00')
#end_time = pd.Timestamp('2019-02-09 20:00:00')
#
#pvlib_data = get_pvlib_data(latitude, longitude, tz, altitude, city, start_time, end_time)
