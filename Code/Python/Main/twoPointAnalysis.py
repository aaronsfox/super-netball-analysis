# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 20:07:40 2020

Author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
This script takes in the .json files grabbed using the superNetballR package and
collates the data into a Pandas dataframe format to analyse and visualise.

TODO: add more specific notes for script
    
"""

# %% Import packages

import pandas as pd
import os
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import gridplot
from bokeh.models import FactorRange, ColumnDataSource, HoverTool
from bokeh.transform import factor_cmap
from bokeh.io import show
from bokeh.io import export_png
from bokeh.resources import CDN
from bokeh.embed import file_html
import json

# %% Load in match data

#Navigate to data directory
os.chdir('..\\Data\\SuperNetball2020')

#Identify list of .json files
jsonFileList = list()
for file in os.listdir(os.getcwd()):
    if file.endswith('.json'):
        jsonFileList.append(file)
        
#Create blank dictionaries to store data in

#Match info
matchInfo = {'id': [], 'homeSquadId': [], 'awaySquadId': [],
             'startTime': [], 'roundNo': [], 'matchNo': [],
             'venueId': [], 'venueName': []}

#Team info
teamInfo = {'squadCode': [], 'squadId': [],
            'squadName': [], 'squadNickname': []}

#Player info
playerInfo = {'playerId': [], 'displayName': [],
              'firstName': [], 'surname': [],
              'shortDisplayName': [], 'squadId': []}

#Score flow data
scoreFlowData = {'roundNo': [], 'matchNo': [],
                 'period': [], 'periodSeconds': [], 'periodCategory': [],
                 'playerId': [],'squadId': [], 'scoreName': [], 'shotOutcome': [], 'scorePoints': [],
                 'distanceCode': [], 'positionCode': [], 'shotCircle': []}

#Loop through file list and extract data
for ff in range(0,len(jsonFileList)):
    
    #Load the .json data
    with open(jsonFileList[ff]) as json_file:
        data = json.load(json_file)
        
    #Extract match details
    matchInfo['id'].append(data['matchInfo']['matchId'][0])
    matchInfo['homeSquadId'].append(data['matchInfo']['homeSquadId'][0])
    matchInfo['awaySquadId'].append(data['matchInfo']['awaySquadId'][0])
    matchInfo['startTime'].append(data['matchInfo']['localStartTime'][0])
    matchInfo['roundNo'].append(data['matchInfo']['roundNumber'][0])
    matchInfo['matchNo'].append(data['matchInfo']['matchNumber'][0])
    matchInfo['venueId'].append(data['matchInfo']['venueId'][0])
    matchInfo['venueName'].append(data['matchInfo']['venueName'][0])

    #If round 1, extract the league team details to lists
    if data['matchInfo']['roundNumber'][0] == 1:
        #Append the two teams details
        teamInfo['squadCode'].append(data['teamInfo']['team'][0]['squadCode'][0])
        teamInfo['squadId'].append(data['teamInfo']['team'][0]['squadId'][0])
        teamInfo['squadName'].append(data['teamInfo']['team'][0]['squadName'][0])
        teamInfo['squadNickname'].append(data['teamInfo']['team'][0]['squadNickname'][0])
        teamInfo['squadCode'].append(data['teamInfo']['team'][1]['squadCode'][0])
        teamInfo['squadId'].append(data['teamInfo']['team'][1]['squadId'][0])
        teamInfo['squadName'].append(data['teamInfo']['team'][1]['squadName'][0])
        teamInfo['squadNickname'].append(data['teamInfo']['team'][1]['squadNickname'][0])
    
    #Extract player details from each team   
    for pp in range(1,len(data['playerInfo']['player'])):
        #First, check if the player ID is in the current id list
        currPlayerId = playerInfo['playerId']
        if data['playerInfo']['player'][pp]['playerId'][0] not in currPlayerId:
            #Grab the new player details
            playerInfo['playerId'].append(data['playerInfo']['player'][pp]['playerId'][0])
            playerInfo['displayName'].append(data['playerInfo']['player'][pp]['displayName'][0])
            playerInfo['firstName'].append(data['playerInfo']['player'][pp]['firstname'][0])
            playerInfo['surname'].append(data['playerInfo']['player'][pp]['surname'][0])
            playerInfo['shortDisplayName'].append(data['playerInfo']['player'][pp]['shortDisplayName'][0])
            ##### TODO: check if it is consistent that first 12 players are team0 in data
            if pp < 12:
                playerInfo['squadId'].append(data['teamInfo']['team'][0]['squadId'][0])
            else:
                playerInfo['squadId'].append(data['teamInfo']['team'][1]['squadId'][0])
    
    #Extract score flow data
    for ss in range(1,len(data['scoreFlow']['score'])):
        scoreFlowData['roundNo'].append(data['matchInfo']['roundNumber'][0])
        scoreFlowData['matchNo'].append(data['matchInfo']['matchNumber'][0])
        scoreFlowData['period'].append(data['scoreFlow']['score'][ss]['period'][0])
        scoreFlowData['periodSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0])
        ##### TODO: check that this period seconds check holds up to rules...
        if data['scoreFlow']['score'][ss]['periodSeconds'][0] > 600:
            scoreFlowData['periodCategory'].append('twoPoint')
        else:
            scoreFlowData['periodCategory'].append('standard')
        scoreFlowData['playerId'].append(data['scoreFlow']['score'][ss]['playerId'][0])
        scoreFlowData['squadId'].append(data['scoreFlow']['score'][ss]['squadId'][0])
        scoreFlowData['scoreName'].append(data['scoreFlow']['score'][ss]['scoreName'][0])
        scoreFlowData['scorePoints'].append(data['scoreFlow']['score'][ss]['scorepoints'][0])
        scoreFlowData['distanceCode'].append(data['scoreFlow']['score'][ss]['distanceCode'][0])
        scoreFlowData['positionCode'].append(data['scoreFlow']['score'][ss]['positionCode'][0])
        ##### TODO: check and document this better from Mitch's twitter sample image
        #Get current distance and position code in one variable
        currCode = [data['scoreFlow']['score'][ss]['positionCode'][0],
                    data['scoreFlow']['score'][ss]['distanceCode'][0]]
        if currCode == [2,3] or currCode == [2,1] or currCode == [1,1] or currCode == [0,1] or currCode == [0,3]:
            scoreFlowData['shotCircle'].append('outerCircle')
        else:
            scoreFlowData['shotCircle'].append('innerCircle')
        if data['scoreFlow']['score'][ss]['scorepoints'][0] == 0:
            scoreFlowData['shotOutcome'].append(False)
        else:
            scoreFlowData['shotOutcome'].append(True)
    
    ##### TODO: extract game statistics data

#Convert filled dictionaries to dataframes

#Team info
df_teamInfo = pd.DataFrame.from_dict(teamInfo)

#Player info
df_playerInfo = pd.DataFrame.from_dict(playerInfo)

#Match info
df_matchInfo = pd.DataFrame.from_dict(matchInfo)

#Score flow data
df_scoreFlow = pd.DataFrame.from_dict(scoreFlowData)

##### TODO: other dataframes once extracted
    
# %%

# %% Test plots from round 1

#There's a number of plot options I want to test:
    # - 2 x 2 plots for each match for a number of variables
        # > Points during standard and two point period
        # > Point rate during standard and two point period
        # > Shot proportion in inner vs. outer during standard and two point period
        # > ??? There was a fourth one I can't remember
    # - 2 x 2 plots for the above variables but pack them all from the same game
    # - Total points from two point shots, shooting players along x-axis, sorted for most to least
    # - Two vs. one point shot point differential (i.e. +ve for more points from 2pt), shooting players along x-axis, sorted most to least
    # - Change in shooting percentage from two vs. one point shot (i.e. +ve for increased %), shooting players along x-axis, sorted from highest to lowest

#Colour settings for teams
colours = ['#00953b', #fever
           '#4b2c69', #firebirds
           '#f57921', #giants
           '#fdb61c', #lightning
           '#494b4a', #magpies
           '#0082cd', #swifts
           '#e54078', #thunderbirds
           '#00a68e'] #vixens
colourDict = {'Fever': '#00953b',
              'Firebirds': '#4b2c69',
              'GIANTS': '#f57921',
              'Lightning': '#fdb61c',
              'Magpies': '#494b4a',
              'Swifts': '#0082cd',
              'Thunderbirds': '#e54078',
              'Vixens': '#00a68e'}

#Set bokeh figure options
bokehOptions = dict(tools = 'wheel_zoom,box_zoom')

#Test out creating a bokeh bar plot for points from round 1, game 1 form one vs. two point shot
#See for sample: https://nbviewer.jupyter.org/github/bokeh/bokeh-notebooks/blob/master/tutorial/07%20-%20Bar%20and%20Categorical%20Data%20Plots.ipynb

#Loop through the four games from round 1
##### TODO: This won't work for matches above round 1

#Set blank lists to fill with plots and source
figPlot = list()
figSource = list()

#Run loop to create plots
for gg in range(0,4):
    
    #Get team ID's for this match
    teamId1 = matchInfo['homeSquadId'][gg]
    teamId2 = matchInfo['awaySquadId'][gg]
    
    #Get team names for these ID's
    teamInd1 = [i for i,x in enumerate(teamInfo['squadId']) if x == teamId1]
    teamName1 = teamInfo['squadNickname'][teamInd1[0]]
    teamInd2 = [i for i,x in enumerate(teamInfo['squadId']) if x == teamId2]
    teamName2 = teamInfo['squadNickname'][teamInd2[0]]
    
    #Set colour palette based on team names
    palette = tuple([colourDict[teamName1],
                     colourDict[teamName2]])
    
    #Set up categorical variables for current game
    goalTypes = ['One Point Shots', 'Two Point Shots']
    teams = [teamName1, teamName2]
    
    #Extract total points scored by the two teams in each category
    
    #Team 1
    standardTeam1 = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                     (df_scoreFlow['scoreName'] == 'goal') & 
                                     (df_scoreFlow['squadId'] == teamId1),
                                     ['scorePoints']].sum()
    twoPointTeam1 = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                     (df_scoreFlow['scoreName'] == '2pt Goal') & 
                                     (df_scoreFlow['squadId'] == teamId1),
                                     ['scorePoints']].sum()
    
    #Team 2
    standardTeam2 = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                     (df_scoreFlow['scoreName'] == 'goal') & 
                                     (df_scoreFlow['squadId'] == teamId2),
                                     ['scorePoints']].sum()
    twoPointTeam2 = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                     (df_scoreFlow['scoreName'] == '2pt Goal') & 
                                     (df_scoreFlow['squadId'] == teamId2),
                                     ['scorePoints']].sum()
    
    #Collate data into dictionary
    dataDict = {'Goal Type' : goalTypes,
                'Team 1'   : [standardTeam1[0], twoPointTeam2[0]],
                'Team 2'   : [standardTeam2[0], twoPointTeam2[0]]}
    
    #Construct data into bokeh friendly format for current bar plotting technique
    x = [(goalType, team) for goalType in goalTypes for team in teams]
    counts = tuple([standardTeam1[0],standardTeam2[0],twoPointTeam1[0],twoPointTeam2[0]])
    
    #Create source for figure
    figSource.append(ColumnDataSource(data = dict(x = x, counts = counts)))
    
    #Create figure
    figPlot.append(figure(x_range = FactorRange(*x),
                          plot_height = 300, plot_width = 300,
                          title = teamName1+' vs. '+teamName2,
                          **bokehOptions))
    
    #Set the bar glyphs
    figPlot[gg].vbar(x = 'x', top = 'counts', width = 1.0, source = figSource[gg], line_color = 'white',
                     fill_color = factor_cmap('x', palette = palette, factors = teams, start = 1, end = 2))
    
    #Set the hover parameter
    figPlot[gg].add_tools(HoverTool(tooltips=[('Category', '@x'), ('Points Scored', '@counts')]))
    
    #Set figure parameters
    figPlot[gg].y_range.start = 0
    figPlot[gg].x_range.range_padding = 0.1
    figPlot[gg].xaxis.major_label_orientation = 1
    figPlot[gg].xgrid.grid_line_color = None
    figPlot[gg].title.align = 'center'
    figPlot[gg].yaxis.axis_label = 'Points Scored'
    
    # #Show figure
    # show(figPlot[gg])

#Create the gridplot
grid = gridplot([[figPlot[0], figPlot[1]],
                 [figPlot[2], figPlot[3]]],
                plot_width = 300, plot_height = 300,
                toolbar_location = 'right')

#Show grid
show(grid)

#Export grid as both .png and .html

##### TODO: set better location for figures

#PNG
export_png(grid, filename = 'Round1_Points.png')

#HTML
output_file('Round1_Points.html')
save(grid)

##### FIGURE OUT HOW TO SHARE --- GITHUB MAyBE???

# %%


# p = gridplot([[p1,p2],
#               [p3,p4]],
#              toolbar_location = 'right')

show(p)
