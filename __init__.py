# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 14:25:42 2019

@author: ntbryant
"""

from flask import Flask
app = Flask(__name__)
from powerpredictor import views
app.config.from_object('config')
app.config.from_pyfile('config.py')
