# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 23:19:59 2019

@author: ntbryant
"""

import pickle
import pandas as pd
from sklearn import preprocessing
import numpy as np
from math import pi, sin


def predict_ghi(df):
    
    # transforming hour and month
    df['hour_trig'] = df['hour'].apply(lambda x: sin((10 * x) / (23 * pi)))
    df['month_trig'] = df['month'].apply(lambda x: sin((10 * x) / (12 * pi)))
    
    # load the model
    gb = pickle.load(open('gb_model.sav', 'rb'))
    
    # standardize and hot code variables
    X = df.drop(['datetime',
                 'day',
                 'hour', 
                 'month',
                 'GHI_pvlib',
                 'DHI_pvlib',
                 'DNI_pvlib'], axis=1)
    
    # hot coding
    X = pd.get_dummies(X, sparse=True)
    
    # matching model variables with forecast data
    example_row = pd.read_csv('example_row.csv', index_col=0)
    X_joined = pd.merge(X, example_row, how='outer')
    cols = [col for col in example_row.columns]
    X_reduced = X_joined[cols]
    
    # dropping the added row
    X_reduced.drop(X_reduced.index[-1], inplace=True)
    
    # replacing NaN with 0
    X_reduced = X_reduced.fillna(0)
    
    # standardizing numeric features
    scaler = preprocessing.StandardScaler().fit(X_reduced)
    X_z = scaler.transform(X_reduced)
    X_z = pd.DataFrame(X_z, columns = X_reduced.columns)
    
    df['GHI_pred'] = gb.predict(X_z)[:,]
    df['GHI_pred'] = np.where(df['GHI_pred'] > df['GHI_clearsky'],
      df['GHI_clearsky'], df['GHI_pred'])

    return(df)

#df = pd.read_csv('solar_weather.csv',index_col=0)
#df = data

