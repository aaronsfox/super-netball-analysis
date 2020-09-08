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
                   'penalties', 'pickups', 'possessions', 'rebounds']
#Convert list to dictionary to store data in
playerStatsDictTotal = {'playerId': [], 'playerName': [], 'squadName': [], 'durationMins': [],
                        'centrePassReceives': [], 'contactPenalties': [], 
                        'deflectionWithGain': [], 'deflectionWithNoGain': [],
                        'deflections': [], 'disposals': [], 'feedWithAttempt': [], 'feeds': [],
                        'gain': [], 'generalPlayTurnovers': [], 'goalAssists': [], 
                        'interceptPassThrown': [], 'intercepts': [], 'obstructionPenalties': [],
                        'penalties': [], 'pickups': [], 'possessions': [],
                        'rebounds': []}
playerStatsDictPer = {'playerId': [], 'playerName': [], 'squadName': [], 'durationMins': [],
                      'centrePassReceives': [], 'contactPenalties': [], 
                      'deflectionWithGain': [], 'deflectionWithNoGain': [],
                      'deflections': [], 'disposals': [], 'feedWithAttempt': [], 'feeds': [],
                      'gain': [], 'generalPlayTurnovers': [], 'goalAssists': [], 
                      'interceptPassThrown': [], 'intercepts': [], 'obstructionPenalties': [],
                      'penalties': [], 'pickups': [], 'possessions': [],
                      'rebounds': []}

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
        newColumn = currColumn.split('_')[0]+'Total'        
        #Rename the dataframe column
        df_playerStatsMetricsAll.rename(columns = {currColumn: newColumn},
                                        inplace = True)
    if '_y' in currColumn:        
        #Set the new column name
        newColumn = currColumn.split('_')[0]+'Per'        
        #Rename the dataframe column
        df_playerStatsMetricsAll.rename(columns = {currColumn: newColumn},
                                        inplace = True)
        
#Split data into attacking and defensive categories
attackingCols = ['playerId', 'playerName', 'squadName', 'durationMins',
                 'centrePassReceivesTotal', 'centrePassReceivesPer',
                 'feedsTotal', 'feedsPer', 'feedWithAttemptTotal', 'feedWithAttemptPer',
                 'goalAssistsTotal', 'goalAssistsPer',
                 'generalPlayTurnoversTotal', 'generalPlayTurnoversPer',
                 'interceptPassThrownTotal', 'interceptPassThrownPer']
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


#Stack all data together
alldata = np.vstack((cpReceives, feeds, feedsAttempt, goalAssists, turnovers,
                     interceptsThrown, gains, deflections, deflectionsGain,
                     deflectionsNoGain, contactPens, obstructionPens))

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

#The above plot suggests that a two cluster solution appears to be the best...
nClusters = 2
##### NOTE: 3 cluster solution might produce some more interesting values...

#Run the cmeans fuzzy clustering using the final nClusters solution
clusterCentres, memberMatrix, _, _, _, _, fuzzyCoefficient = fuzz.cluster.cmeans(alldata,
                                                                                 c = nClusters,
                                                                                 m = 2,
                                                                                 error = 1e-6,
                                                                                 maxiter = 10000,
                                                                                 seed = 123,
                                                                                 init = None)

#Given only two clusters are used here, each players values in the membership
#matrix will simply be 1 - the other value, and so are evenly distributed between
#the two.

#Define a hard membership matrix depending on which cluster the players higher 
#fuzzy value sits in
clusteredPlayers = df_playerStatsMetricsAll['playerName'].values
memberCluster = list()
for pp in range(0,len(clusteredPlayers)):
    if memberMatrix[0,pp] >= memberMatrix[1,pp]:
        memberCluster.append('Cluster 1')
    else:
        memberCluster.append('Cluster 2')
        
#Create a new dataframe that has the per metrics
newData = np.transpose(alldata)
df_clusterData = pd.DataFrame(newData,
                              columns = ['cpReceives', 'feeds', 'feedsAttempt',
                                         'goalAssists', 'turnovers', 'interceptsThrown',
                                         'gains', 'deflections', 'deflectionsGain',
                                         'deflectionsNoGain', 'contactPens', 'obstructionPens'])

#Add the player and squad details columns
df_clusterData['playerId'] = df_playerStatsMetricsAll['playerId'].values
df_clusterData['playerName'] = df_playerStatsMetricsAll['playerName'].values
df_clusterData['squadName'] = df_playerStatsMetricsAll['squadName'].values
df_clusterData['durationMins'] = df_playerStatsMetricsAll['durationMins'].values

#Add the cluster membership details
df_clusterData['clusterMember'] = memberCluster
df_clusterData['clusterFuzz1'] = np.transpose(memberMatrix[0,:])
df_clusterData['clusterFuzz2'] = np.transpose(memberMatrix[1,:])

#Use the hard cluster member data to get a bit of an idea of the differences 
#between the clusters, by plotting the data from each of these. Note that these
#might be off a little bit given that certain players could sit in the middle
#of these two, but should give enough of an indication

#Set cluster variables
clusterVars = ['cpReceives', 'feeds', 'feedsAttempt',
               'goalAssists', 'turnovers', 'interceptsThrown',
               'gains', 'deflections', 'deflectionsGain',
               'deflectionsNoGain', 'contactPens', 'obstructionPens']

#Reconfigure dataframe to work with seaborn grouping plots
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
                   df_clusterData['obstructionPens'].to_numpy()))
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
                 ['obstructionPens'] * len(df_clusterData)))
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
                      df_clusterData['clusterMember'].to_numpy()))
df_clusterDataTransform = pd.DataFrame(np.transpose(np.vstack((value,var,clusters))),
                                       columns = ['per15Value','variable','clusterMember'])
    
#Create boxplot to visualise clustered data
sns.boxplot(data = df_clusterDataTransform,
            x = 'variable', y = 'per15Value',
            hue = 'clusterMember')
    
##### At a basic level, it seems that cluster 1 relates to attacking play, with
##### higher centre pass receives, feeds, feeds with attempts, goal assists,
##### turnovers and intercepts thrown. Cluster 2 seems more like defensive play,
##### with more gains, deflections (all categories) contact and obstruction 
##### penalties (Cluster 2 is less clear in these increases, but still seem there)

##### There's probably a lack of distinction here, as goal shooters are getting
##### put in the defensive category, as they don't have receives and feeds etc.
##### Adding scoring data might lead to more clusters and better separation

# %% Test creating a bokeh plot that places players on a line

#Set players names to plot
# plotPlayers = ['L.Watson', 'C.Koenen', 'R.Aiken', 'T.Dwan', 'J.Fowler']
plotPlayers = list(clusteredPlayers)

#Set colours to plot circles based on player team
# plotColours = ['#00a68e', '#fdb61c', '#4b2c69', '#4b2c69', '#00953b']

#Get each players 'attacking' (i.e. cluster 1) fuzzy membership value
xVal = list()
for pp in range(0,len(plotPlayers)):
    xVal.append(df_clusterData.loc[(df_clusterData['playerName'] == plotPlayers[pp]),
                                   ['clusterFuzz1']].to_numpy()[0][0])
    
#Create consistent y-value of 1
yVal = [1] * len(xVal)

#Put data into dataframe
# df = pd.DataFrame(list(zip(plotPlayers, plotColours, xVal, yVal)), 
#                columns = ['playerName', 'plotColour', 'x', 'y'])
df = pd.DataFrame(list(zip(plotPlayers, xVal, yVal)), 
               columns = ['playerName', 'x', 'y'])

#Create bokeh figure
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, show
from bokeh.transform import jitter
#Create figure
p = figure(plot_width = 600, plot_height = 200,
           title = 'Plot with jitter')
#Turn grids off
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

#ADd circles
p.circle(x = 'x', y = jitter('y',0.01),
         #radius = 0.1/2,
         size = 20,
         # line_color = 'plotColour',
         line_color = 'blue',
         fill_color = 'white',
         fill_alpha = 0,
         line_width = 1.5,
         source = df)

#Show plot
show(p)

##### The above approach works OK, although some data gets cut-off.
##### Need to tweak around the jotter, size parameters etc. to get it right
##### Also turn off axis, add the line at y = 1 or some sort of directional axes

##### More players may also change the above - certainly gets overlap, but get
##### a result more like you'd expect (still cut-off though)...

##### Also need to consider other statistics with respect to maybe having more clusters...


# %%

# %%

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


