# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 14:27:32 2019

@author: ntbryant
"""

from flask import Flask, request, render_template
#from powerpredictor import app
import pandas as pd

import geopy
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pytz import timezone
from scipy.integrate import simps
from numpy import trapz
import config
import nsrdb_historical as nsrdb
import wund_forecast as wund
import pvlib_irradiances as pv
import predict_irradiance as pred
import plot_maker as pm

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home',
       )

@app.route('/results', methods=['GET','POST'])
def results():
    try:
        location_input = request.form.get('location')
    except:
        location_input = "Portland, OR"

    try:
        size_input = float(request.form.get('size_input'))
    except:
        size_input = 5

    # creating location characteristics
    city, state = location_input.split(',')
    city.strip()
    state.strip()

    tf = TimezoneFinder()

    # convert location to latitude and longitude
    geolocator = Nominatim(user_agent="powerpredictor")
    geopy.geocoders.options.default_timeout = 15
    location = geolocator.geocode(location_input)
    latitude = location.latitude
    longitude = location.longitude
    tzone = tf.timezone_at(lng=longitude, lat=latitude)
    altitude = location.altitude

    # get NSRDB data for 2017
    nsrdb_data = nsrdb.get_nsrdb_data(latitude, longitude, config.nrel_api_key)

    # get weather forecast
    wund_data = wund.get_forecast(city, state, config.wund_api_key)

    # get pvlib irradiances
    start_time = wund_data['datetime'].min()
    end_time = wund_data['datetime'].max()
    pvlib_data = pv.get_pvlib_data(latitude,
                                    longitude,
                                    tzone,
                                    altitude,
                                    city,
                                    start_time,
                                    end_time)

    # merging forecast and nsrdb data
    wund_data[['month', 'day', 'hour']] = wund_data[['month', 'day', 'hour']].apply(pd.to_numeric)
    data = pd.merge(wund_data, nsrdb_data,
                    on=['month', 'day', 'hour'],
                    how='left')

    # merging data with pvlib data
    pvlib_data['datetime'] = pvlib_data.index
    pvlib_data['datetime'] = pvlib_data['datetime'].dt.tz_localize(None)
    data = pd.merge(data, pvlib_data[['datetime', 'GHI_pvlib', 'DNI_pvlib', 'DHI_pvlib',
                                      'GHI_clearsky']], on='datetime')

    # getting predicted GHI
    results = pred.predict_ghi(data)

    # barchart with power available
    results['date'] = results['datetime'].dt.date
    results_by_date = results.groupby('date')
    
    # calculating energy as integral of power curve
    solar_energy = results_by_date.apply(lambda x: -trapz(x['hour'], x['GHI_pred']))
    max_power = results_by_date.apply(lambda x: max(x['GHI_pred']))
    power_values = results_by_date.apply(lambda x: x[x['GHI_pred'] > 0])
    power_values.index = pd.to_datetime(power_values['datetime'])
    power_by_date = power_values.groupby('date')
    avg_power = power_by_date['GHI_pred'].mean()
    sys_energy = solar_energy * size_input * 0.77
    energy = pd.DataFrame({
            'solar_energy' : solar_energy,
            'max_power' : max_power,
            'avg_power' : avg_power,
            'sys_energy' : sys_energy})
    energy.index = pd.to_datetime(energy.index)
    energy['day_name'] = energy.index.day_name()
    energy['short_day'] = energy.index.strftime("%a").astype(str)
    
    # getting rid of erroneous values
    energy = energy.drop(energy.index[-1])
    energy = energy.drop(energy.index[0])
    
    # getting the plot
    plotscript, plotdiv = pm.make_plot(energy)
    
    # average power per day
    power_average = (energy['sys_energy'].mean() / 1000).round(2)

    return render_template('results.html', MESSAGE_MID=power_average,
                           size_input=size_input,
                           plotscript=plotscript,
                           plotdiv=plotdiv,
                           latitude=latitude,
                           longitude=longitude)

#if __name__ == '__main__':
#    app.run()
#    gunicorn_logger = logging.getLogger('gunicorn.error')
#    app.logger.handlers = gunicorn_logger.handlers
#    app.logger.setLevel(gunicorn_logger.level)
    
if __name__ == '__main__':
    #this runs your app locally
    app.run(host='0.0.0.0', port=8080, debug=True)

