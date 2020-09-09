# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 20:53:05 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Current test code for player style calculations and vis...
    
    Fuzzy clustering example:
        https://pythonhosted.org/scikit-fuzzy/auto_examples/plot_cmeans.html
        https://learning.oreilly.com/library/view/mastering-machine-learning/9781788621113/6967d36f-e04e-46d3-8c99-e30e2193d464.xhtml
    
"""

# %% Import packages

import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
import skfuzzy as fuzz
import pandas as pd
import os
from bokeh.io import curdoc, show
from bokeh.models import Circle, ColumnDataSource, Grid, ImageURL, LinearAxis, Plot, Range1d
from PIL import Image

#Navigate to supplementary directory and import helper scripts
os.chdir('..\\Supplementary')
import ssn2020DataHelper as dataHelper

# %% Load in player statistic data

#Navigate to data directory
os.chdir('..\\..\\..\\Data\\SuperNetball2020')

#Identify list of .json files
jsonFileList = list()
for file in os.listdir(os.getcwd()):
    if file.endswith('.json'):
        jsonFileList.append(file)
        
#Read in total squad lists as dataframe
df_squadLists = pd.read_csv('squadLists.csv')

#Create a variable for starting positions
starterPositions = ['GS','GA','WA','C','WD','GD','GK']

#Import data using helper function
dataImport = dataHelper.getMatchData(jsonFileList = jsonFileList,
                                     df_squadLists = df_squadLists,
                                     exportDict = True, exportDf = True,
                                     exportTeamData = True, exportPlayerData = True,
                                     exportMatchData = True, exportScoreData = True,
                                     exportLineUpData = True, exportPlayerStatsData = True,
                                     exportTeamStatsData = True)

#Unpack the imported data
teamInfo = dataImport['teamInfo']
matchInfo = dataImport['matchInfo']
playerInfo = dataImport['playerInfo']
scoreFlowData = dataImport['scoreFlowData']
lineUpData = dataImport['lineUpData']
individualLineUpData = dataImport['individualLineUpData']
playerStatsData = dataImport['playerStatsData']
teamStatsData = dataImport['teamStatsData']
df_teamInfo = dataImport['df_teamInfo']
df_matchInfo = dataImport['df_matchInfo']
df_playerInfo = dataImport['df_playerInfo']
df_scoreFlow = dataImport['df_scoreFlow']
df_lineUp = dataImport['df_lineUp']
df_individualLineUp = dataImport['df_individualLineUp']
df_playerStatsData = dataImport['df_playerStatsData']
df_teamStatsData = dataImport['df_teamStatsData']

# %% Calculate player summary and per 15 statistics

#Get unique list of players to examine
playerStatList = df_playerStatsData['playerId'].unique()

#Set the per divider
perDivider = 15

#Loop through ID's and get their playing duration
playerDurationSeconds = []
for pp in range(0,len(playerStatList)):
    #Get duration from lineup data
    playerDurationSeconds.append(df_individualLineUp.loc[(df_individualLineUp['playerId'] == playerStatList[pp]) &
                                                         (df_individualLineUp['playerPosition'] != 'S'),
                                                         ['durationSeconds']]['durationSeconds'].sum())

#Set up list of data to collate from player stats
playerStatsGrab = ['centrePassReceives', 'contactPenalties', 
                   'deflectionWithGain', 'deflectionWithNoGain',
                   'deflections', 'disposals', 'feedWithAttempt', 'feeds',
                   'gain', 'generalPlayTurnovers', 'goalAssists', 
                   'interceptPassThrown', 'intercepts', 'obstructionPenalties',
                   'penalties', 'pickups', 'possessions', 'rebounds',
                   'goalAttempts', 'goal_from_zone1','goal_from_zone2']
#Convert list to dictionary to store data in
playerStatsDictTotal = {'playerId': [], 'playerName': [], 'squadName': [], 'durationMins': [],
                        'centrePassReceives': [], 'contactPenalties': [], 
                        'deflectionWithGain': [], 'deflectionWithNoGain': [],
                        'deflections': [], 'disposals': [], 'feedWithAttempt': [], 'feeds': [],
                        'gain': [], 'generalPlayTurnovers': [], 'goalAssists': [], 
                        'interceptPassThrown': [], 'intercepts': [], 'obstructionPenalties': [],
                        'penalties': [], 'pickups': [], 'possessions': [],
                        'rebounds': [], 'goalAttempts': [], 'goal_from_zone1': [], 'goal_from_zone2': []}
playerStatsDictPer = {'playerId': [], 'playerName': [], 'squadName': [], 'durationMins': [],
                      'centrePassReceives': [], 'contactPenalties': [], 
                      'deflectionWithGain': [], 'deflectionWithNoGain': [],
                      'deflections': [], 'disposals': [], 'feedWithAttempt': [], 'feeds': [],
                      'gain': [], 'generalPlayTurnovers': [], 'goalAssists': [], 
                      'interceptPassThrown': [], 'intercepts': [], 'obstructionPenalties': [],
                      'penalties': [], 'pickups': [], 'possessions': [],
                      'rebounds': [], 'goalAttempts': [], 'goal_from_zone1': [], 'goal_from_zone2': []}

#Loop through players and extract statistics
for pp in range(0,len(playerStatList)):
    
    #First, check if player has played more than 15 mins total
    if playerDurationSeconds[pp]/60 > 15:
        
        #Extract player and squad details
        currPlayerId = playerStatList[pp]
        currPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(currPlayerId)]
        currPlayerSquadId = playerInfo['squadId'][playerInfo['playerId'].index(currPlayerId)]
        currSquadName = teamInfo['squadNickname'][teamInfo['squadId'].index(currPlayerSquadId)]
        
        #Append player and squad details to dictionary
        playerStatsDictTotal['playerId'].append(currPlayerId)
        playerStatsDictTotal['playerName'].append(currPlayerName)
        playerStatsDictTotal['squadName'].append(currSquadName)
        playerStatsDictTotal['durationMins'].append(playerDurationSeconds[pp]/60)
        playerStatsDictPer['playerId'].append(currPlayerId)
        playerStatsDictPer['playerName'].append(currPlayerName)
        playerStatsDictPer['squadName'].append(currSquadName)
        playerStatsDictPer['durationMins'].append(playerDurationSeconds[pp]/60)
        
        #Loop through and extract game statistics
        for ss in range(0,len(playerStatsGrab)):
            
            #Extract total stats number for the current player and stat
            statTotal = df_playerStatsData.loc[(df_playerStatsData['playerId'] == currPlayerId),
                                               [playerStatsGrab[ss]]][playerStatsGrab[ss]].sum()
            
            #Normalise to the per 15 minute
            perFac = perDivider / (playerDurationSeconds[pp]/60)
            statNormal = statTotal * perFac
            
            #Append to dictionary
            playerStatsDictTotal[playerStatsGrab[ss]].append(statTotal)
            playerStatsDictPer[playerStatsGrab[ss]].append(statNormal)
            
#Convert dictionary to dataframe
df_playerStatsMetricsTotal = pd.DataFrame.from_dict(playerStatsDictTotal)
df_playerStatsMetricsPer = pd.DataFrame.from_dict(playerStatsDictPer)

#Merge dataframes
df_playerStatsMetricsAll = pd.merge(left = df_playerStatsMetricsTotal, right = df_playerStatsMetricsPer,
                                    how = 'inner', left_on = 'playerId', right_on = 'playerId')

#Drop the second player and squad name, and duration columns
df_playerStatsMetricsAll.drop(['playerName_y','squadName_y','durationMins_y'],
                              axis = 1, inplace = True)

#Rename the original player and squad name columns
df_playerStatsMetricsAll.rename(columns = {'playerName_x': 'playerName',
                                           'squadName_x': 'squadName',
                                           'durationMins_x': 'durationMins'},
                                inplace = True)

#Loop through remaining columns and rename _x to totals and _y to per
for col in df_playerStatsMetricsAll.columns: 
    
    #Get current column name
    currColumn = col
    
    #Check if it contains one of the triggers for renaming
    if '_x' in currColumn:
        #Set the new column name
        newColumn = currColumn[0:-2]+'Total'        
        #Rename the dataframe column
        df_playerStatsMetricsAll.rename(columns = {currColumn: newColumn},
                                        inplace = True)
    if '_y' in currColumn:        
        #Set the new column name
        newColumn = currColumn[0:-2]+'Per'        
        #Rename the dataframe column
        df_playerStatsMetricsAll.rename(columns = {currColumn: newColumn},
                                        inplace = True)
        
#Split data into attacking and defensive categories
attackingCols = ['playerId', 'playerName', 'squadName', 'durationMins',
                 'centrePassReceivesTotal', 'centrePassReceivesPer',
                 'feedsTotal', 'feedsPer', 'feedWithAttemptTotal', 'feedWithAttemptPer',
                 'goalAssistsTotal', 'goalAssistsPer',
                 'generalPlayTurnoversTotal', 'generalPlayTurnoversPer',
                 'interceptPassThrownTotal', 'interceptPassThrownPer',
                 'goalAttemptsTotal','goalAttemptsPer',
                 'goal_from_zone1Total','goal_from_zone1Per',
                 'goal_from_zone1Total','goal_from_zone2Per']
defensiveCols = ['playerId', 'playerName', 'squadName', 'durationMins',
                 'gainTotal', 'gainPer',
                 'deflectionsTotal', 'deflectionsPer',
                 'deflectionWithGainTotal', 'deflectionWithGainPer',
                 'deflectionWithNoGainTotal', 'deflectionWithNoGainPer',
                 'contactPenaltiesTotal', 'contactPenaltiesPer',
                 'obstructionPenaltiesTotal','obstructionPenaltiesPer']

#Extract columns from dataframe
df_playerStatsMetricsAttacking = df_playerStatsMetricsAll[df_playerStatsMetricsAll.columns.intersection(attackingCols)]
df_playerStatsMetricsDefensive = df_playerStatsMetricsAll[df_playerStatsMetricsAll.columns.intersection(defensiveCols)]

#Sort by player name
df_playerStatsMetricsAttacking.sort_values('playerName', inplace = True)
df_playerStatsMetricsDefensive.sort_values('playerName', inplace = True)

# %% Run fuzzy clustering algorithm on per 15 metrics

#Extract data into individual arrays
cpReceives = df_playerStatsMetricsAll['centrePassReceivesPer'].to_numpy()
feeds = df_playerStatsMetricsAll['feedsPer'].to_numpy()
feedsAttempt = df_playerStatsMetricsAll['feedWithAttemptPer'].to_numpy()
goalAssists = df_playerStatsMetricsAll['goalAssistsPer'].to_numpy()
turnovers = df_playerStatsMetricsAll['generalPlayTurnoversPer'].to_numpy()
interceptsThrown = df_playerStatsMetricsAll['interceptPassThrownPer'].to_numpy()
gains = df_playerStatsMetricsAll['gainPer'].to_numpy()
deflections = df_playerStatsMetricsAll['deflectionsPer'].to_numpy()
deflectionsGain = df_playerStatsMetricsAll['deflectionWithGainPer'].to_numpy()
deflectionsNoGain = df_playerStatsMetricsAll['deflectionWithNoGainPer'].to_numpy()
contactPens = df_playerStatsMetricsAll['contactPenaltiesPer'].to_numpy()
obstructionPens = df_playerStatsMetricsAll['obstructionPenaltiesPer'].to_numpy()
goalAttempts = df_playerStatsMetricsAll['goalAttemptsPer'].to_numpy()
goalZone1 = df_playerStatsMetricsAll['goal_from_zone1Per'].to_numpy()
goalZone2 = df_playerStatsMetricsAll['goal_from_zone2Per'].to_numpy()

#Stack all data together
alldata = np.vstack((cpReceives, feeds, feedsAttempt, goalAssists, turnovers,
                     interceptsThrown, gains, deflections, deflectionsGain,
                     deflectionsNoGain, contactPens, obstructionPens,
                     goalAttempts, goalZone1, goalZone2))

#Test out varying cluster numbers to identify the most appropriate cluster number
#We'll test out 2 through 10 clusters here

#Initialise list to store fuzzy partition coefficient
fpcs = []

#Set array to test different cluster numbers
ncentres = np.array([2,3,4,5,6,7,8,9,10])

#Loop through centres
for nn in range(0,len(ncentres)):
    
    #Run the fuzzy c-means clustering with the current centre number
    cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(alldata,
                                                     c = ncentres[nn],
                                                     m = 2,
                                                     error = 1e-6,
                                                     maxiter = 10000,
                                                     seed = 123,
                                                     init = None)
    
    #Store fpc value
    fpcs.append(fpc)
    
#Visualise the fuzzy partition coefficient
#The FPC is defined in a range from 0 to 1, with 1 being the best. Therefore, 
#the highest FPC value indicates the most optimal clustering solution.
fig, ax = plt.subplots()
ax.plot(np.r_[2:11], fpcs)
ax.set_xlabel('Number of Cluster Centres')
ax.set_ylabel('Fuzzy Partition Coefficient (FPC)')

#The above plot suggests that a three cluster solution appears to be the best...
#Two clusters was without shooting stats, while with shooting stats we got 3 as best
nClusters = 3

#Run the cmeans fuzzy clustering using the final nClusters solution
clusterCentres, memberMatrix, _, _, _, _, fuzzyCoefficient = fuzz.cluster.cmeans(alldata,
                                                                                 c = nClusters,
                                                                                 m = 2,
                                                                                 error = 1e-6,
                                                                                 maxiter = 10000,
                                                                                 seed = 123,
                                                                                 init = None)

#Define a hard membership matrix depending on which cluster the players higher 
#fuzzy value sits in
clusteredPlayers = df_playerStatsMetricsAll['playerName'].values
memberCluster = list()
for pp in range(0,len(clusteredPlayers)):
    if memberMatrix[0,pp] > memberMatrix[1,pp] and memberMatrix[0,pp] > memberMatrix[2,pp]:
        memberCluster.append('Cluster 1')
    elif memberMatrix[1,pp] > memberMatrix[0,pp] and memberMatrix[1,pp] > memberMatrix[2,pp]:
        memberCluster.append('Cluster 2')
    elif memberMatrix[2,pp] > memberMatrix[0,pp] and memberMatrix[2,pp] > memberMatrix[1,pp]:
        memberCluster.append('Cluster 3')
        
#Create a new dataframe that has the per metrics
newData = np.transpose(alldata)
df_clusterData = pd.DataFrame(newData,
                              columns = ['cpReceives', 'feeds', 'feedsAttempt',
                                         'goalAssists', 'turnovers', 'interceptsThrown',
                                         'gains', 'deflections', 'deflectionsGain',
                                         'deflectionsNoGain', 'contactPens', 'obstructionPens',
                                         'goalAttempts', 'goalZone1', 'goalZone2'])

#Add the player and squad details columns
df_clusterData['playerId'] = df_playerStatsMetricsAll['playerId'].values
df_clusterData['playerName'] = df_playerStatsMetricsAll['playerName'].values
df_clusterData['squadName'] = df_playerStatsMetricsAll['squadName'].values
df_clusterData['durationMins'] = df_playerStatsMetricsAll['durationMins'].values

#Add the cluster membership details
df_clusterData['clusterMember'] = memberCluster
df_clusterData['clusterFuzz1'] = np.transpose(memberMatrix[0,:])
df_clusterData['clusterFuzz2'] = np.transpose(memberMatrix[1,:])
df_clusterData['clusterFuzz3'] = np.transpose(memberMatrix[2,:])

#Use the hard cluster member data to get a bit of an idea of the differences 
#between the clusters, by plotting the data from each of these. Note that these
#might be off a little bit given that certain players could sit in the middle
#of these two, but should give enough of an indication

#Set cluster variables
clusterVars = ['cpReceives', 'feeds', 'feedsAttempt',
               'goalAssists', 'turnovers', 'interceptsThrown',
               'gains', 'deflections', 'deflectionsGain',
               'deflectionsNoGain', 'contactPens', 'obstructionPens',
               'goalAttempts', 'goalZone1', 'goalZone2']

#Reconfigure dataframe to work with seaborn grouping plots
##### TODO: make this more efficient...
value = np.hstack((df_clusterData['cpReceives'].to_numpy(),
                   df_clusterData['feeds'].to_numpy(),
                   df_clusterData['feedsAttempt'].to_numpy(),
                   df_clusterData['goalAssists'].to_numpy(),
                   df_clusterData['turnovers'].to_numpy(),
                   df_clusterData['interceptsThrown'].to_numpy(),
                   df_clusterData['gains'].to_numpy(),
                   df_clusterData['deflections'].to_numpy(),
                   df_clusterData['deflectionsGain'].to_numpy(),
                   df_clusterData['deflectionsNoGain'].to_numpy(),
                   df_clusterData['contactPens'].to_numpy(),
                   df_clusterData['obstructionPens'].to_numpy(),
                   df_clusterData['goalAttempts'].to_numpy(),
                   df_clusterData['goalZone1'].to_numpy(),
                   df_clusterData['goalZone2'].to_numpy()))
var = np.hstack((['cpReceives'] * len(df_clusterData),
                 ['feeds'] * len(df_clusterData),
                 ['feedsAttempt'] * len(df_clusterData),
                 ['goalAssists'] * len(df_clusterData),
                 ['turnovers'] * len(df_clusterData),
                 ['interceptsThrown'] * len(df_clusterData),
                 ['gains'] * len(df_clusterData),
                 ['deflections'] * len(df_clusterData),
                 ['deflectionsGain'] * len(df_clusterData),
                 ['deflectionsNoGain'] * len(df_clusterData),
                 ['contactPens'] * len(df_clusterData),
                 ['obstructionPens'] * len(df_clusterData),
                 ['goalAttempts'] * len(df_clusterData),
                 ['goalZone1'] * len(df_clusterData),
                 ['goalZone2'] * len(df_clusterData)))
clusters = np.hstack((df_clusterData['clusterMember'].to_numpy(),
                      df_clusterData['clusterMember'].to_numpy(),
                      df_clusterData['clusterMember'].to_numpy(),
                      df_clusterData['clusterMember'].to_numpy(),
                      df_clusterData['clusterMember'].to_numpy(),
                      df_clusterData['clusterMember'].to_numpy(),
                      df_clusterData['clusterMember'].to_numpy(),
                      df_clusterData['clusterMember'].to_numpy(),
                      df_clusterData['clusterMember'].to_numpy(),
                      df_clusterData['clusterMember'].to_numpy(),
                      df_clusterData['clusterMember'].to_numpy(),
                      df_clusterData['clusterMember'].to_numpy(),
                      df_clusterData['clusterMember'].to_numpy(),
                      df_clusterData['clusterMember'].to_numpy(),
                      df_clusterData['clusterMember'].to_numpy()))
df_clusterDataTransform = pd.DataFrame(np.transpose(np.vstack((value,var,clusters))),
                                       columns = ['per15Value','variable','clusterMember'])
    
#Create boxplot to visualise clustered data
sns.boxplot(data = df_clusterDataTransform,
            x = 'variable', y = 'per15Value',
            hue = 'clusterMember')
    
# At a basic level, it seems like cluster 1 is the shooting cluster, with
# the goal attempts and a bit of attacking involvement (e.g. feeds, cp_receives,
# goal assist). Cluster 2 looks to be the defensive cluster, with low attacking
# variable data and high defensive data (e.g. gains, deflections, contact and
# obstruction penalties). Cluster 3 looks to be the attacking mid court group,
# with high values for centre pass receives, feeds, assists etc. (and some scoring).

# %% Test visualising player positioning in clusters

#Set players names to plot
plotPlayers = ['L.Watson', 'C.Koenen', 'R.Aiken', 'T.Dwan', 'J.Fowler']

#Set colours to plot circles based on player team
plotColours = ['#00a68e', '#fdb61c', '#4b2c69', '#4b2c69', '#00953b']

#Get each players fuzziness data
fuzzyData = np.zeros([3,len(plotPlayers)])
for pp in range(0,len(plotPlayers)):
    #Cluster 1 fuzzy metric
    fuzzyData[0,pp] = df_clusterData.loc[(df_clusterData['playerName'] == plotPlayers[pp]),
                                         ['clusterFuzz1']].to_numpy()[0][0]
    #Cluster 2 fuzzy metric
    fuzzyData[1,pp] = df_clusterData.loc[(df_clusterData['playerName'] == plotPlayers[pp]),
                                         ['clusterFuzz2']].to_numpy()[0][0]
    #Cluster 3 fuzzy metric
    fuzzyData[2,pp] = df_clusterData.loc[(df_clusterData['playerName'] == plotPlayers[pp]),
                                         ['clusterFuzz3']].to_numpy()[0][0]

# The visualisation we want to test involves an equilateral triangle, with the points
# representing a fuzzy value of 1 for the three different clusters. To figure out a players
# position in the triangle we run some calculations to determine how close the players
# point should be to each triangle point - and then take the average of these. This considers
# that 0.5 for each cluster sits in the middle, while a value of 1 sits at the point.

#Start with implementing a standard matplotlib implementation
fig, ax = plt.subplots(figsize=(10,8))

# #Figure out triangle height based on edge length of 1
# triHeight = math.sqrt(1 - (0.5*0.5))

#Create the triangle. This will have a bottom left corner at (0,0),
#a bottom right corner at (0,1), and the top point at (1,0.5)
ax.plot([0,1], [0,0], color = 'k', lw = 2)
# ax.plot([0,0.5], [0,triHeight], color = 'k', lw = 2)
# ax.plot([0.5,1], [triHeight,0], color = 'k', lw = 2)
ax.plot([0,0.5], [0,1], color = 'k', lw = 2)
ax.plot([0.5,1], [1,0], color = 'k', lw = 2)

#We'll set the top point as being cluster 1, the bottom left as
#cluster 2, and the bottom right as cluster 3. This means that 
#the bottom left to top of the triangle is 0-1 for cluster 1,
#the bottom right to bottom left is 0-1 for cluster 2, and the
#top to bottom right is 0-1 for cluster 3

#Calculate the player points (XY)
xyPoints = np.zeros([len(plotPlayers),2])
for pp in range(0,len(plotPlayers)):
    
    #Get current cluster data
    c1 = fuzzyData[0,pp]
    # c2 = fuzzyData[1,pp]
    c3 = fuzzyData[2,pp]
    
    #Calculate x and y position for plot and append to array
    xyPoints[pp,0] = c3 + (c1/2)
    xyPoints[pp,1] = c1
    
#Add xy points
ax.scatter(xyPoints[:,0], xyPoints[:,1],
           c = plotColours,
           marker = 'o')

# %%

##### Below Bokeh plot is a simple 2d line solution, not triangular...
    

# %% Test creating a bokeh plot

#Set players names to plot
# plotPlayers = ['L.Watson', 'C.Koenen', 'R.Aiken', 'T.Dwan', 'J.Fowler']
plotPlayers = list(clusteredPlayers)

#Set colours to plot circles based on player team
# plotColours = ['#00a68e', '#fdb61c', '#4b2c69', '#4b2c69', '#00953b']

#Get each players fuzziness data
fuzzyData = np.zeros([3,len(plotPlayers)])
for pp in range(0,len(plotPlayers)):
    #Cluster 1 fuzzy metric
    fuzzyData[0,pp] = df_clusterData.loc[(df_clusterData['playerName'] == plotPlayers[pp]),
                                         ['clusterFuzz1']].to_numpy()[0][0]
    #Cluster 2 fuzzy metric
    fuzzyData[1,pp] = df_clusterData.loc[(df_clusterData['playerName'] == plotPlayers[pp]),
                                         ['clusterFuzz2']].to_numpy()[0][0]
    #Cluster 3 fuzzy metric
    fuzzyData[2,pp] = df_clusterData.loc[(df_clusterData['playerName'] == plotPlayers[pp]),
                                         ['clusterFuzz3']].to_numpy()[0][0]

#Calculate the player points (XY)
xyPoints = np.zeros([len(plotPlayers),2])
for pp in range(0,len(plotPlayers)):
    
    #Get current cluster data
    c1 = fuzzyData[0,pp]
    # c2 = fuzzyData[1,pp]
    c3 = fuzzyData[2,pp]
    
    #Calculate x and y position for plot and append to array
    xyPoints[pp,0] = c3 + (c1/2)
    xyPoints[pp,1] = c1

#Add colour column
#Set colour dictionary
colourDict = {'Fever': '#00953b',
              'Firebirds': '#4b2c69',
              'GIANTS': '#f57921',
              'Lightning': '#fdb61c',
              'Magpies': '#494b4a',
              'Swifts': '#0082cd',
              'Thunderbirds': '#e54078',
              'Vixens': '#00a68e'}
#Get team list
#### TODO: clean up extraction using loc etc.
plotTeams = df_clusterData['squadName'].values
plotColours = list()
for tt in range(0,len(plotTeams)):
    plotColours.append(colourDict[plotTeams[tt]])

#Put data into dataframe
# df = pd.DataFrame(list(zip(plotPlayers, plotColours, xVal, yVal)), 
#                columns = ['playerName', 'plotColour', 'x', 'y'])
df = pd.DataFrame(list(zip(plotPlayers, xyPoints[:,0], xyPoints[:,1], plotColours)), 
               columns = ['playerName', 'x', 'y', 'teamColour'])

#Create bokeh figure
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, show
# from bokeh.transform import jitter
#Create figure
p = figure(plot_width = 700, plot_height = 500)
#Turn grids off
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

#Add a line renderer for triangle
p.line([0, 0.5, 1, 0], [0, 1, 0, 0],
       line_width = 2, line_color = 'black')

#Add circles
p.circle(x = 'x', y = 'y',
         #radius = 0.1/2,
         size = 10,
         # line_color = 'plotColour',
         line_color = 'teamColour',
         fill_color = 'white',
         fill_alpha = 0,
         line_width = 1.5,
         source = df)

#Show plot
show(p)

##### Above approach for plotting points works well enough
##### TODO: add hovertools, add images, consider team specific,
##### add icons for triangle points, turn off panning, turn off axes,
##### consider grid format with multiple team plots

# %%

# %%

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


