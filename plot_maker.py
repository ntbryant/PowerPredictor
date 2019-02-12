# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 20:43:58 2019
from: https://github.com/avahoffman/Natural_parks/blob/master/make_yeartrendplot.py
@author: ntbryant
"""

def make_plot(energy):
    import numpy as np
    from bokeh.plotting import figure
    from bokeh.embed import components
    from bokeh.plotting import figure
    from bokeh.models import Range1d, LinearAxis, FactorRange
    import datetime

    # plot a yearly trend
    plot = figure(y_range=( 0 , max(energy['sys_energy']) + 50),
                  x_axis_type = 'datetime',
                  plot_width=650, plot_height=300)
    plot.xaxis.axis_label = 'Date'
    plot.yaxis.axis_label = 'Predicted System Output (Wh)'
    plot.line(energy.index, energy['sys_energy'], color="orangered", legend = 'Predicted Energy', line_width=3)
    # Create 2nd y-axis
    plot.extra_y_ranges['max_power'] = Range1d(start=0, end=1050)
    plot.add_layout(LinearAxis(y_range_name='max_power', axis_label='Max Irradiance (W/m2)'), 'right')
    plot.line(x = energy.index, y = energy['max_power'], legend = 'Max Irradiance', y_range_name = 'max_power', color = 'royalblue', line_width=3, line_dash='dotted')
    plot.toolbar_location = 'above'
    plot.legend.border_line_color = "black"
    plot.legend.border_line_alpha = 0.5
    script, div = components(plot)
    return script, div