# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 20:53:05 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Current test code for player style calculations and vis...
    
"""

# %% Import packages

import numpy as np
import pandas as pd
import os
from bokeh.io import curdoc, show
from bokeh.models import Circle, ColumnDataSource, Grid, ImageURL, LinearAxis, Plot, Range1d
from PIL import Image

# %% Create some mock data that has XY variables for 5 players

#Random X-data
X = [0.2, -0.3, 0.5, 0.1, 0.2]

#Random Y-data
Y = [-0.7, 0.4, 0.5, 0.6, -0.4]

#Set player names to plot
players = ['L.Watson', 'C.Koenen', 'R.Aiken', 'T.Dwan', 'J.Fowler']

#Set colours to plot circles based on player team
colours = ['#00a68e', '#fdb61c', '#4b2c69', '#4b2c69', '#00953b']

#Concert to dataframe
df = pd.DataFrame(list(zip(players, colours, X, Y)), 
                  columns= ['players', 'colours', 'X', 'Y'])

#Get paths to local and online images
os.chdir('..\\..\\..\\Data\\SuperNetball2020\\Images')
localImagePaths = list()
onlineImagePaths = list()
for pp in range(0,len(players)):
    localImagePaths.append(os.getcwd()+'\\'+players[pp]+'.png')
    onlineImagePaths.append('https://aaronsfox.github.io/graphics/ssn-2020/player-images/'+players[pp]+'.png')

# %% Create Bokeh scatter plot

#Create plot
p = Plot(title = None,
         x_range = Range1d(start = -1, end = 1),
         y_range = Range1d(start = -1, end = 1),
         plot_width=500, plot_height=500,
         min_border=0, toolbar_location = None)

#Create the source for the plot
source = ColumnDataSource(dict(
    url = onlineImagePaths,
    playerName = list(df['players']),
    playerColour = list(df['colours']),
    xData = np.array(df['X']),
    yData = np.array(df['Y'])
))

#Add images at the appropriate centroids based on XY position
#We'll make the images cover a size of 0.3 each for now
imageSet = list()
scaleSize = 0.3
img = Image.open(localImagePaths[0]).convert('RGB')
w,h = img.size
scaleFac = scaleSize/h

#Add images
imagePlot = ImageURL(url = 'url',
                     x = 'xData', y = 'yData',
                     h = h*scaleFac,
                     w = w*scaleFac,
                     anchor = 'center')
p.add_glyph(source, imagePlot)

#Add the scatter point circles
circlePlot = Circle(x = 'xData',
                    y = 'yData',
                    radius = scaleSize/2,
                    line_color = 'playerColour',
                    fill_color = 'white',
                    fill_alpha = 0,
                    line_width = 1.5)
p.add_glyph(source, circlePlot)
    
#Set axes
xaxis = LinearAxis()
p.add_layout(xaxis, 'below')
yaxis = LinearAxis()
p.add_layout(yaxis,'left')

#Set layout
p.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
p.add_layout(Grid(dimension=1, ticker=yaxis.ticker))

#Update doc
curdoc().add_root(p)

#Show plot
show(p)


