# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 20:07:40 2020

Author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au

This script serves to analyse various aspects of the Super Netball 2021 season.
It will be continuously updated with different aspects depending on what analysis 
is of interest, and leverages a number of functions in the supplementart code folder
of this repo. The script uses the .json files grabbed using the superNetballR package
and collates data into Pandas dataframe format to analyse and visualise.

"""

# %% Import packages

import pandas as pd
pd.options.mode.chained_assignment = None #turn off pandas chained warnings
import numpy as np
import scipy.stats as stats
import random
import seaborn as sns
import matplotlib.pyplot as plt
import os
# from bokeh.plotting import figure, output_file, save
# from bokeh.layouts import gridplot
# from bokeh.models import FactorRange, ColumnDataSource, Legend, HoverTool
# from bokeh.transform import factor_cmap
# from bokeh.io import show
# from bokeh.io import export_png
# import json

#Set plot parameters
from matplotlib import rcParams
# rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = 'Arial'
rcParams['font.weight'] = 'bold'
rcParams['axes.labelsize'] = 12
rcParams['axes.titlesize'] = 16
rcParams['axes.linewidth'] = 1.5
rcParams['axes.labelweight'] = 'bold'
rcParams['legend.fontsize'] = 10
rcParams['xtick.major.width'] = 1.5
rcParams['ytick.major.width'] = 1.5
rcParams['legend.framealpha'] = 0.0
rcParams['savefig.dpi'] = 300
rcParams['savefig.format'] = 'pdf'

#Navigate to supplementary directory and import helper scripts
os.chdir('..\\Supplementary')
import ssn2021FigHelper as figHelper
import ssn2021DataHelper as dataHelper

# %% Load in match data

#Navigate to data directory
os.chdir('..\\..\\..\\Data\\SuperNetball2021')

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

# %% Plots to consider...

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
bokehOptions = dict(tools = ['wheel_zoom,box_zoom'])

# %% Team-based data two-point shot figures

#Shift to round by round figure directory
os.chdir('..\\..\\Figures\\TwoPointAnalysis\\RoundByRound')

#Set round to plot
round2Plot = 1

#Total one vs. two point shots
figHelper.totalPointsOneVsTwo(round2Plot = round2Plot, matchInfo = matchInfo,
                              teamInfo = teamInfo, df_scoreFlow = df_scoreFlow,
                              colourDict = colourDict, bokehOptions = bokehOptions,
                              showPlot = False, exportPNG = True, exportHTML = True)

#Quarter by quarter one vs. two point shots
figHelper.quarterPointsOneVsTwo(round2Plot = round2Plot, matchInfo = matchInfo,
                                teamInfo = teamInfo, df_scoreFlow = df_scoreFlow,
                                colourDict = colourDict, bokehOptions = bokehOptions,
                                showPlot = False, exportPNG = True, exportHTML = True)

#Ratio of inner vs. outer shots in different periods
figHelper.teamShotRatiosInnerVsOuter(round2Plot = round2Plot, matchInfo = matchInfo,
                                     teamInfo = teamInfo, df_scoreFlow = df_scoreFlow,
                                     colourDict = colourDict, bokehOptions = bokehOptions,
                                     showPlot = False, exportPNG = True, exportHTML = True)

# %% Individual player two-point scoring

#Set round to plot
round2Plot = 1

#Total two-point score
figHelper.playerTwoPointTotals(round2Plot = round2Plot, df_scoreFlow = df_scoreFlow,
                               df_playerInfo = df_playerInfo, df_teamInfo = df_teamInfo,
                               colourDict = colourDict, showPlot = False,
                               exportPNG = True, exportHTML = True)

#Differential between two and one point scoring
figHelper.playerTwoPointDifferentials(round2Plot = round2Plot, df_scoreFlow = df_scoreFlow,
                                      df_playerInfo = df_playerInfo, df_teamInfo = df_teamInfo,
                                      colourDict = colourDict, showPlot = False,
                                      exportPNG = True, exportHTML = True)

#Relative differential for two vs. one point totals
figHelper.playerTwoPointRelativeDifferentials(round2Plot = round2Plot, df_scoreFlow = df_scoreFlow,
                                              df_playerInfo = df_playerInfo, df_teamInfo = df_teamInfo,
                                              colourDict = colourDict, showPlot = False,
                                              exportPNG = True, exportHTML = True)

# %% Calculate some basic season statistics

#Calculate total proportion of score for each team from super vs. standard shots

#Get unique squad ID's from score flow data
squadIds = df_scoreFlow['squadId'].unique()

#Print heading
print('Proportion of total score from Super Shots:')

#Loop through squads
for tt in range(0,len(squadIds)):
    
    #Get the current squads total points
    totalPts = df_scoreFlow.loc[(df_scoreFlow['squadId'] == squadIds[tt]),
                     ['scorePoints']].sum()[0]
    
    #Get the current squads super shot points
    superPts = df_scoreFlow.loc[(df_scoreFlow['squadId'] == squadIds[tt]) & 
                                (df_scoreFlow['scoreName'] == '2pt Goal'),
                                ['scorePoints']].sum()[0]
    
    #Calculate proportion
    currProp = superPts / totalPts * 100
    
    #Get the current team name
    currTeamName = df_teamInfo.squadName[df_teamInfo['squadId'] == squadIds[tt]].reset_index()['squadName'][0]
    
    #Print results
    print(currTeamName+': '+str(round(currProp,2))+'%')

#Calculate total proportion of score for each team from super vs. standard shots
#but in the Rebel Power 5

#Print heading
print('Proportion of total score from Super Shots during Rebel Power 5:')

#Loop through squads
for tt in range(0,len(squadIds)):
    
    #Get the current squads total points
    totalPts = df_scoreFlow.loc[(df_scoreFlow['squadId'] == squadIds[tt]) &
                                (df_scoreFlow['periodCategory'] == 'twoPoint'),
                                ['scorePoints']].sum()[0]
    
    #Get the current squads super shot points
    superPts = df_scoreFlow.loc[(df_scoreFlow['squadId'] == squadIds[tt]) & 
                                (df_scoreFlow['periodCategory'] == 'twoPoint') &
                                (df_scoreFlow['scoreName'] == '2pt Goal'),
                                ['scorePoints']].sum()[0]
    
    #Calculate proportion
    currProp = superPts / totalPts * 100
    
    #Get the current team name
    currTeamName = df_teamInfo.squadName[df_teamInfo['squadId'] == squadIds[tt]].reset_index()['squadName'][0]
    
    #Print results
    print(currTeamName+': '+str(round(currProp,2))+'%')

#Calculate the average score for each team from both super and standard
#shots in power 5 periods

#Print heading
print('Average score in Rebel Power 5 period:')

#Loop through squads
for tt in range(0,len(squadIds)):
    
    #Get the current squads total points in Power 5 periods
    totalPts = df_scoreFlow.loc[(df_scoreFlow['squadId'] == squadIds[tt]) &
                                (df_scoreFlow['periodCategory'] == 'twoPoint'),
                                ['scorePoints']].sum()[0]
    
    #Divide the total points by the number of rounds and 4 quarters
    nRounds = max(df_scoreFlow['roundNo'])
    avgPts = totalPts / nRounds / 4
    
    #Get the current team name
    currTeamName = df_teamInfo.squadName[df_teamInfo['squadId'] == squadIds[tt]].reset_index()['squadName'][0]
    
    #Print results
    print(currTeamName+': '+str(round(avgPts,2))+' per period')

#Contrast scoring rate per minute in standard vs. Rebel Power 5
#Note that values above 1 indicate elevated scoring rate
#Also note that this just uses 10 vs. 5 mins rather than actual seconds here

#Print heading
print('Relative scoring rate in Power 5 vs. standard period:')

#Loop through squads
for tt in range(0,len(squadIds)):
    
    #Get the current squads total points in Power 5 periods
    totalPtsPower = df_scoreFlow.loc[(df_scoreFlow['squadId'] == squadIds[tt]) &
                                     (df_scoreFlow['periodCategory'] == 'twoPoint'),
                                     ['scorePoints']].sum()[0]
    
    #Calculate power 5 scoring rate per minute
    nRounds = max(df_scoreFlow['roundNo'])
    powerRate = totalPtsPower / (nRounds * 5 * 4)
    
    #Get the current squads total points in standard period
    totalPtsStandard = df_scoreFlow.loc[(df_scoreFlow['squadId'] == squadIds[tt]) &
                                     (df_scoreFlow['periodCategory'] == 'standard'),
                                     ['scorePoints']].sum()[0]
    
    #Calculate power 5 scoring rate per minute
    standardRate = totalPtsStandard / (nRounds * 10 * 4)
    
    #Get the relative rate for Power 5 vs. standard
    relRate = powerRate / standardRate
    
    #Get the current team name
    currTeamName = df_teamInfo.squadName[df_teamInfo['squadId'] == squadIds[tt]].reset_index()['squadName'][0]
    
    #Print results
    print(currTeamName+': '+str(round(relRate,2)))

#Calculate the number of super shot attempts vs. standard attempts
#Do this for the standard and Power 5 periods

#Print heading
print('Number of close vs. long-range shots in different periods:')

#Loop through squads
for tt in range(0,len(squadIds)):
    
    #Get the current squads long and close shots in the power 5 period
    totalLongPower = len(df_scoreFlow.loc[(df_scoreFlow['squadId'] == squadIds[tt]) &
                                          (df_scoreFlow['periodCategory'] == 'twoPoint') &
                                          (df_scoreFlow['shotCircle'] == 'outerCircle'),])
    totalClosePower = len(df_scoreFlow.loc[(df_scoreFlow['squadId'] == squadIds[tt]) &
                                           (df_scoreFlow['periodCategory'] == 'twoPoint') &
                                           (df_scoreFlow['shotCircle'] == 'innerCircle'),])
    
    #Get the current squads long and close shots in the standard period
    totalLongStandard = len(df_scoreFlow.loc[(df_scoreFlow['squadId'] == squadIds[tt]) &
                                             (df_scoreFlow['periodCategory'] == 'standard') &
                                              (df_scoreFlow['shotCircle'] == 'outerCircle'),])
    totalCloseStandard = len(df_scoreFlow.loc[(df_scoreFlow['squadId'] == squadIds[tt]) &
                                              (df_scoreFlow['periodCategory'] == 'standard') &
                                              (df_scoreFlow['shotCircle'] == 'innerCircle'),])
    
    #Get the current team name
    currTeamName = df_teamInfo.squadName[df_teamInfo['squadId'] == squadIds[tt]].reset_index()['squadName'][0]
    
    #Print results
    print(currTeamName+': '+str(totalCloseStandard)+' vs. '+str(totalLongStandard)+' inner vs. outer circle shots, respectively, in standard scoring period')
    print(currTeamName+': '+str(totalClosePower)+' vs. '+str(totalLongPower)+' inner vs. outer circle shots, respectively, in Power 5 period')

#Calculate average success of super shots for each team

#Print heading
print('Team shooting percentage for Super Shots:')

#Loop through squads
for tt in range(0,len(squadIds)):
    
    #Get the current squads total made and missed super shots
    totalMade = len(df_scoreFlow.loc[(df_scoreFlow['squadId'] == squadIds[tt]) &
                                     (df_scoreFlow['periodCategory'] == 'twoPoint') &
                                     (df_scoreFlow['shotCircle'] == 'outerCircle') &
                                     (df_scoreFlow['shotOutcome'] == True),])
    totalMissed = len(df_scoreFlow.loc[(df_scoreFlow['squadId'] == squadIds[tt]) &
                                       (df_scoreFlow['periodCategory'] == 'twoPoint') &
                                       (df_scoreFlow['shotCircle'] == 'outerCircle') &
                                       (df_scoreFlow['shotOutcome'] == False),])
    
    #Calculate shooting percentage
    shootingPer = totalMade / (totalMade + totalMissed) * 100

    #Get the current team name
    currTeamName = df_teamInfo.squadName[df_teamInfo['squadId'] == squadIds[tt]].reset_index()['squadName'][0]
    
    #Print results
    print(currTeamName+': '+str(round(shootingPer,2))+'%')

#Calculate some player related numbers

#Extract the super shots into their own dataframe
df_superShots = df_scoreFlow.loc[(df_scoreFlow['periodCategory'] == 'twoPoint') &
                                 (df_scoreFlow['shotCircle'] == 'outerCircle'),]

#Group by player ID and shot outcome to get some summary stats
df_superPlayerCounts = df_superShots.groupby(['playerId','shotOutcome'])[['scoreName']].count()

#Get the unique player ID's who took super shots
superShotPlayers = list()
for pp in range(0,len(df_superPlayerCounts.index)):
    superShotPlayers.append(df_superPlayerCounts.index[pp][0])
superShotPlayers = list(set(superShotPlayers))

#Create dictionary for players, and counts of makes and misses
superCounts = {'playerId': [], 'playerName': [], 'made': [], 'missed': [],
               'total': [], 'shootingPer': []}

#Loop through and extract data from count dataframe
for pp in range(0,len(superShotPlayers)):
    
    #Get current player name and append id and name to dictionary
    currPlayerName = df_playerInfo.displayName[df_playerInfo['playerId'] == superShotPlayers[pp]].reset_index()['displayName'][0]
    superCounts['playerId'].append(superShotPlayers[pp])
    superCounts['playerName'].append(currPlayerName)
    
    #Get True and False counts for current player
    #Check for made values for current player ID    
    try:
        made = df_superPlayerCounts.loc[(superShotPlayers[pp], True), 'scoreName']
    except KeyError:
        #Set made to 0
        made = 0
    #Check for miss values for current player ID    
    try:
        missed = df_superPlayerCounts.loc[(superShotPlayers[pp], False), 'scoreName']
    except KeyError:
        #Set made to 0
        missed = 0
        
    #Append values to dictionary
    superCounts['made'].append(made)
    superCounts['missed'].append(missed)
    superCounts['total'].append(made+missed)
    superCounts['shootingPer'].append(made/(made+missed)*100)

#Convert to dataframe
df_superCounts = pd.DataFrame.from_dict(superCounts)

# %% Create some clutch shooting-based numbers

# This analysis defines the 'clutch' period as the final 5 minutes of the match
# when the margin is less than 5.
#
# An extra element added here is when the score is within the same bounds as 
# above, but in any overtime period
#
# We also only include players who have taken > 5 'clutch' shots
#
# 'Go ahead' shots are counted as those that could tie or put their team in front

#First, look at go ahead shots in the 'clutch' period.
#This considers both the number and success rate

#Extract shots from scoreflow that meet the 'clutch' criteria
df_clutchScore1 = df_scoreFlow.loc[(df_scoreFlow['period'] == 4) &
                                  (df_scoreFlow['periodSeconds'] > 60*(15-5)) &
                                  (df_scoreFlow['preShotMargin'].between(-5,5)),]

#Extract shots from scoreflow for overtime period 'clutch' criteria
df_clutchScore2 = df_scoreFlow.loc[(df_scoreFlow['period'] == 5) &
                                  (df_scoreFlow['preShotMargin'].between(-5,5)),]

#Concatenate dataframes
df_clutchScore = pd.concat([df_clutchScore1,df_clutchScore2])

#Get number of clutch shots per player
clutchShootersNo = list(zip(*np.unique(df_clutchScore['playerId'],
                                       return_counts=True)))

#Identify shooters that meet the criteria
clutchShooters = list()
for cc in range(0,len(clutchShootersNo)):
    if clutchShootersNo[cc][1] > 5:
        clutchShooters.append(clutchShootersNo[cc][0])
        
#Create dictionary to store data in
clutchData = {'displayName': [], 'squadId': [],
              'nClutchShots': [], 'nClutchStandard': [], 'nClutchSuper': [],
              'nGoAheadTotal': [], 'nGoAheadStandard': [], 'nGoAheadSuper': [],
              'totalAccuracy': [], 'standardAccuracy': [], 'superAccuracy': [],
              'goAheadAccuracy': []}

#Loop through players and count clutch shooting numbers
for pp in range(0,len(clutchShooters)):
    
    #Extract current players name & squad
    currPlayer = df_playerInfo['displayName'][df_playerInfo.index[df_playerInfo['playerId'] == clutchShooters[pp]][0]]
    currSquad = df_playerInfo['squadId'][df_playerInfo.index[df_playerInfo['playerId'] == clutchShooters[pp]][0]]
    
    #Extract current players dataframe
    df_currClutch = df_clutchScore.loc[(df_clutchScore['playerId'] == clutchShooters[pp]),]
    
    #Calculate some basic shot number metrics
    nClutchShots = len(df_currClutch)
    nClutchStandard = len(df_currClutch.loc[(df_currClutch['shotCircle'] == 'innerCircle'),])
    nClutchSuper = len(df_currClutch.loc[(df_currClutch['shotCircle'] == 'outerCircle'),])
    nGoAheadStandard = len(df_currClutch.loc[(df_currClutch['preShotAhead'] != currSquad) &
                                             (df_currClutch['shotCircle'] == 'innerCircle') &
                                             (df_currClutch['preShotMargin'].between(-1,1))])
    nGoAheadSuper = len(df_currClutch.loc[(df_currClutch['preShotAhead'] != currSquad) &
                                          (df_currClutch['shotCircle'] == 'outerCircle') &
                                          (df_currClutch['preShotMargin'].between(-2,2))])
    nGoAheadTotal = nGoAheadStandard + nGoAheadSuper
    
    #Calculate total shot accuracy
    totalAccuracy = sum(df_currClutch['shotOutcome']) / nClutchShots
    
    #Calculate standard vs. super shot accuracy
    if nClutchStandard > 0:
        standardAccuracy = sum(df_currClutch.loc[(df_currClutch['shotCircle'] == 'innerCircle'),
                                                 ['shotOutcome']]['shotOutcome']) / nClutchStandard
    else:
        standardAccuracy = np.nan
    if nClutchSuper > 0:            
        superAccuracy = sum(df_currClutch.loc[(df_currClutch['shotCircle'] == 'outerCircle'),
                                              ['shotOutcome']]['shotOutcome']) / nClutchSuper
    else:
        superAccuracy = np.nan
    
    #Calculate go ahead shot accuracy
    if nGoAheadTotal > 0:
        goAheadAccuracy = (sum(df_currClutch.loc[(df_currClutch['preShotAhead'] != currSquad) &
                                                 (df_currClutch['shotCircle'] == 'innerCircle') &
                                                 (df_currClutch['preShotMargin'].between(-1,1)),
                                                 ['shotOutcome']]['shotOutcome']) + \
                           sum(df_currClutch.loc[(df_currClutch['preShotAhead'] != currSquad) &
                                                 (df_currClutch['shotCircle'] == 'outerCircle') &
                                                 (df_currClutch['preShotMargin'].between(-2,2)),
                                                 ['shotOutcome']]['shotOutcome'])) / nGoAheadTotal
    else:
        goAheadAccuracy = np.nan
        
    #Append to dictionary
    clutchData['displayName'].append(currPlayer)
    clutchData['squadId'].append(currSquad)
    clutchData['nClutchShots'].append(nClutchShots)
    clutchData['nClutchStandard'].append(nClutchStandard)
    clutchData['nClutchSuper'].append(nClutchSuper)
    clutchData['nGoAheadTotal'].append(nGoAheadTotal)
    clutchData['nGoAheadStandard'].append(nGoAheadStandard)
    clutchData['nGoAheadSuper'].append(nGoAheadSuper)
    clutchData['totalAccuracy'].append(totalAccuracy)
    clutchData['standardAccuracy'].append(standardAccuracy)
    clutchData['superAccuracy'].append(superAccuracy)
    clutchData['goAheadAccuracy'].append(goAheadAccuracy)
    
#Convert clutch data to dataframe
df_clutchData = pd.DataFrame.from_dict(clutchData)    

# %% Plus/minus figures

#Navigate to appropriate directory
os.chdir('..\\..\\PlusMinusAnalysis')

#Team line-up total plus minus
figHelper.totalPlusMinusLineUps(teamInfo = teamInfo, df_lineUp = df_lineUp,
                                absPlusMinus = True, perPlusMinus = True,
                                perDivider = 15, minLineUpDuration = 15,
                                colourDict = colourDict, showPlot = False,
                                exportPNG = True, exportHTML = True)

#Individual player total plus minus
figHelper.playerPlusMinus(teamInfo = teamInfo, playerInfo = playerInfo,
                          df_individualLineUp = df_individualLineUp,
                          absPlusMinus = True, perPlusMinus = True,
                          perDivider = 15, minDuration = 15, nPlayers = 20,
                          colourDict = colourDict, showPlot = False,
                          exportPNG = True, exportHTML = True)

#Differential between player plus/minus on vs. off court
figHelper.relativePlayerPlusMinus(teamInfo = teamInfo, playerInfo = playerInfo,
                                  df_individualLineUp = df_individualLineUp ,
                                  perDivider = 15, minDurationOn = 15, minDurationOff = 5, nPlayers = 20,
                                  colourDict = colourDict, showPlot = False,
                                  exportPNG = True, exportHTML = True)

# %% Export data for plus/minus HTML tables

# %% Team line-up data

# This will export the unique line-up data for all teams as a .csv file to convert
# to a HTML table in R via reactable. Each row of data will be a unique line-up
# with the columns relating to team, GS, ..., GK, ABS +/-, PER15 +/-, duration.
# We'll limit the line-ups to those that have had 15 minutes on court together
# for now. 

#Append the combined lineup name to the line up dataframecombinedLineUpName = list()
combinedLineUpName = list()
for dd in range(0,len(df_lineUp)):
    #Get lineup
    currLineUp = df_lineUp['lineUpName'][dd]
    #Check for empty slot in lineup
    for pp in range(0,len(currLineUp)):
        if not currLineUp[pp]:
            #Replace with an 'N/A'
            currLineUp[pp] = 'N/A'
    #Combine player names
    combinedLineUpName.append(", ".join(currLineUp))
#Append to dataframe
df_lineUp['combinedLineUpName'] = combinedLineUpName

#Extract the unique line-ups
uniqueLineUps = df_lineUp['combinedLineUpName'].unique()

#Loop through unique lineups and sum the duration and plus/minus data
lineUpDuration = list()
lineUpPlusMinus = list()
analyseLineUps = list()
squadLineUps = list()
minLineUpDuration = 15
for uu in range(0,len(uniqueLineUps)):
    #Get a separated dataframe
    df_currLineUp = df_lineUp.loc[(df_lineUp['combinedLineUpName'] == uniqueLineUps[uu]),]
    #Sum data and append to list if greater than specified minutes (converted to seconds here)
    if sum(df_currLineUp['durationSeconds']) >= (minLineUpDuration*60):
        analyseLineUps.append(uniqueLineUps[uu])
        lineUpDuration.append(sum(df_currLineUp['durationSeconds']) / 60)
        lineUpPlusMinus.append(sum(df_currLineUp['plusMinus']))
        squadLineUps.append(teamInfo['squadNickname'][teamInfo['squadId'].index(df_currLineUp['squadId'].unique()[0])])
                
#Split the string of the lineups to put in the columns
lineUpGS = list()
lineUpGA = list()
lineUpWA = list()
lineUpC = list()
lineUpWD = list()
lineUpGD = list()
lineUpGK = list()
for aa in range(0,len(analyseLineUps)):
    #Split and allocate
    splitLineUp = analyseLineUps[aa].split(', ')
    lineUpGS.append(splitLineUp[0])
    lineUpGA.append(splitLineUp[1])
    lineUpWA.append(splitLineUp[2])
    lineUpC.append(splitLineUp[3])
    lineUpWD.append(splitLineUp[4])
    lineUpGD.append(splitLineUp[5])
    lineUpGK.append(splitLineUp[6])
    
#Convert to dataframe
df_lineUpPlusMinus = pd.DataFrame(list(zip(squadLineUps,lineUpGS,lineUpGA,lineUpWA,
                                           lineUpC,lineUpWD,lineUpGD,lineUpGK,
                                           lineUpDuration,lineUpPlusMinus)),
                                  columns = ['team','GS','GA','WA','C','WD','GD','GK',
                                             'duration','absPlusMinus'])

#Add the per 15 plus minus column
perPlusMinusVal = list()
perDivider = 15
for mm in range(0,len(df_lineUpPlusMinus)):
    perFac = perDivider / df_lineUpPlusMinus['duration'][mm]
    perPlusMinusVal.append(df_lineUpPlusMinus['absPlusMinus'][mm]*perFac)
#Append to dataframe
df_lineUpPlusMinus['per15PlusMinus'] = perPlusMinusVal

#Sort values
df_lineUpPlusMinus.sort_values(by = 'per15PlusMinus', inplace = True,
                               ascending = False, ignore_index = True)

#Export data to csv file
#Navigate to directory
os.chdir('..\\..\\Code\\R\\htmlTables\\plusMinus')
#Export
df_lineUpPlusMinus.to_csv('teamLineUps_plusMinus.csv', index = False)

# %% Player plus/minus data

# This will export the unique players across the competition as a .csv file to
# convert to a HTML in R via reactable. Each row of data will be a unique player
# with the columns relating to team, player, duration on, duration off,
# ABS +/- on court, ABS +/- off, ABS +/- diff, PER15 +/- on court, PER15 +/- off
# court, PER15 +/- diff

#Get unique list of players
uniquePlayers = list(df_individualLineUp['playerId'].unique())

#Loop through players and extract total plus minus data
#Set blank lists to store data in
playerDurationOn = list()
playerDurationOff = list()
playerPlusMinusOn = list()
playerPlusMinusOff = list()
playerPlusMinusOnPer15 = list()
playerPlusMinusOffPer15 = list()
analysePlayer = list()
analyseSquad = list()
minPlayerDurationOn = 15
minPlayerDurationOff = 15
perDivider = 15
for pp in range(0,len(uniquePlayers)):
    
    #Extract current player to dataframe for on and off
    df_currPlayerOn = df_individualLineUp.loc[(df_individualLineUp['playerId'] == uniquePlayers[pp]) &
                                              (df_individualLineUp['playerPosition'] != 'S'),
                                              ['playerId','durationSeconds','plusMinus']]
    df_currPlayerOn.reset_index(drop=True, inplace=True)
    df_currPlayerOff = df_individualLineUp.loc[(df_individualLineUp['playerId'] == uniquePlayers[pp]) &
                                               (df_individualLineUp['playerPosition'] == 'S'),
                                               ['playerId','durationSeconds','plusMinus']]
    df_currPlayerOff.reset_index(drop=True, inplace=True)
    
    #Check if player total is greater than specified minutes and get data if so
    if sum(df_currPlayerOn['durationSeconds']) > minPlayerDurationOn*60 and sum(df_currPlayerOff['durationSeconds']) > minPlayerDurationOff*60:
        #Append duration and plus/minus when on vs. off
        playerDurationOn.append(sum(df_currPlayerOn['durationSeconds'])/60)
        playerPlusMinusOn.append(sum(df_currPlayerOn['plusMinus']))
        playerDurationOff.append(sum(df_currPlayerOff['durationSeconds'])/60)
        playerPlusMinusOff.append(sum(df_currPlayerOff['plusMinus']))
        #On
        perFac = perDivider / (sum(df_currPlayerOn['durationSeconds']/60))
        playerPlusMinusOnPer15.append(sum(df_currPlayerOn['plusMinus'])*perFac)
        #Off
        perFac = perDivider / (sum(df_currPlayerOff['durationSeconds']/60))
        playerPlusMinusOffPer15.append(sum(df_currPlayerOff['plusMinus'])*perFac)
        #Get current player and append
        analysePlayer.append(playerInfo['displayName'][playerInfo['playerId'].index(uniquePlayers[pp])])
        #Get squad ID colour for player
        currSquadId = playerInfo['squadId'][playerInfo['playerId'].index(uniquePlayers[pp])]
        analyseSquad.append(teamInfo['squadNickname'][teamInfo['squadId'].index(currSquadId)])
        
        
        
#Place player plus minus data in dataframe and sort
df_playerPlusMinusRel = pd.DataFrame(list(zip(analyseSquad,analysePlayer,
                                              playerDurationOn,playerDurationOff,
                                              playerPlusMinusOn,playerPlusMinusOff,
                                              playerPlusMinusOnPer15,playerPlusMinusOffPer15)),
                                     columns = ['team','player','durationOn','durationOff',
                                                'absPlusMinusOn','absPlusMinusOff',
                                                'perPlusMinusOn','perPlusMinusOff'])

#Calculate the relative difference between when the player is off vs. on
#This calculation means positive and negative values mean the team does better
#versus worse when the player is on, respectively
relPerformanceAbs = list()
relPerformancePer = list()
for dd in range(0,len(df_playerPlusMinusRel)):
    relPerformanceAbs.append(df_playerPlusMinusRel['absPlusMinusOn'][dd] - df_playerPlusMinusRel['absPlusMinusOff'][dd])
    relPerformancePer.append(df_playerPlusMinusRel['perPlusMinusOn'][dd] - df_playerPlusMinusRel['perPlusMinusOff'][dd])
#Append to dataframe
df_playerPlusMinusRel['relAbsPlusMinus'] = relPerformanceAbs
df_playerPlusMinusRel['relPerPlusMinus'] = relPerformancePer
#Resort by relative per 15 performance
df_playerPlusMinusRel.sort_values(by = 'relPerPlusMinus', inplace = True,
                                  ascending = False, ignore_index = True)
 
#Export to CSV
df_playerPlusMinusRel.to_csv('individualPlayer_plusMinus.csv', index = False)

# %% Calculate player summary and per 15 statistics

##### TODO: add shooting stats to output dataframe

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
                   'deflections',
                   # 'disposals',
                   'feedWithAttempt', 'feeds',
                   'gain', 'generalPlayTurnovers', 'goalAssists', 
                   'interceptPassThrown', 'intercepts', 'obstructionPenalties',
                   'penalties', 'pickups',
                   # 'possessions',
                   'rebounds',
                   'goalAttempts', 'goals']
#Convert list to dictionary to store data in
playerStatsDictTotal = {'playerId': [], 'playerName': [], 'squadName': [], 'durationMins': [],
                        'centrePassReceives': [], 'contactPenalties': [], 
                        'deflectionWithGain': [], 'deflectionWithNoGain': [],
                        'deflections': [],
                        # 'disposals': [],
                        'feedWithAttempt': [], 'feeds': [],
                        'gain': [], 'generalPlayTurnovers': [], 'goalAssists': [], 
                        'interceptPassThrown': [], 'intercepts': [], 'obstructionPenalties': [],
                        'penalties': [], 'pickups': [],
                        # 'possessions': [],
                        'rebounds': [],
                        'goalAttempts': [], 'goals': []}
playerStatsDictPer = {'playerId': [], 'playerName': [], 'squadName': [], 'durationMins': [],
                      'centrePassReceives': [], 'contactPenalties': [], 
                      'deflectionWithGain': [], 'deflectionWithNoGain': [],
                      'deflections': [],
                      # 'disposals': [],
                      'feedWithAttempt': [], 'feeds': [],
                      'gain': [], 'generalPlayTurnovers': [], 'goalAssists': [], 
                      'interceptPassThrown': [], 'intercepts': [], 'obstructionPenalties': [],
                      'penalties': [], 'pickups': [],
                      # 'possessions': [],
                      'rebounds': [],
                      'goalAttempts': [], 'goals': []}

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

#Export data
os.chdir('..\\playerStats')
df_playerStatsMetricsAttacking.to_csv('individualPlayerStats_Attacking.csv', index = False)
df_playerStatsMetricsDefensive.to_csv('individualPlayerStats_Defensive.csv', index = False)

# %% Time in front data

#Create dictionary to store basic home and away numbers in
timeInFront = {'homeInFront': [], 'awayInFront': [], 'timeTied': []}

#Loop through matches
for mm in range(0,len(df_matchInfo)):
    
    #Set starting variables for home and away seconds in front
    homeInFront = 0
    awayInFront = 0
    
    #Get current match info
    roundNo = df_matchInfo['roundNo'][mm]
    matchNo = df_matchInfo['matchNo'][mm]
    
    #Get total match seconds
    totalMatchSeconds = sum(df_matchInfo['periodSeconds'][mm])
    
    #Get home and away squad ID for current match
    homeId = df_matchInfo['homeSquadId'][mm]
    awayId = df_matchInfo['awaySquadId'][mm]
    
    #Extract current match
    df_currMatch = df_scoreFlow.loc[(df_scoreFlow['roundNo'] == roundNo) &
                                    (df_scoreFlow['matchNo'] == matchNo),]
    
    #Reindex score flow dataframe
    df_currMatch.reset_index(drop = True, inplace = True)
    
    #Loop through score flow points
    for pp in range(0,len(df_currMatch)):
        
        #Check for first score and don't calculate as nobody is in front
        if pp > 0:
            
            #Check the pre shot margin
            preMargin = df_currMatch['preShotMargin'][pp]
            
            #If margin is > 1, home has been in front
            if preMargin > 1:
                
                #Calculate seconds this margin has been present
                timeMargin = df_currMatch['matchSeconds'][pp] - df_currMatch['matchSeconds'][pp-1]
                
                #Add to home margin time
                homeInFront = homeInFront + timeMargin
                
            elif preMargin < 1:
                
                #Calculate seconds this margin has been present
                timeMargin = df_currMatch['matchSeconds'][pp] - df_currMatch['matchSeconds'][pp-1]
                
                #Add to away margin time
                awayInFront = awayInFront + timeMargin
                
    #Do one more addition for the period between the last score and match end
    if df_currMatch['preShotMargin'][len(df_currMatch)-1] > 0:
        
        #Calculate seconds this margin was present
        timeMargin = totalMatchSeconds - df_currMatch['matchSeconds'][len(df_currMatch)-1]
        
        #Add to home margin time
        homeInFront = homeInFront + timeMargin
        
    elif df_currMatch['preShotMargin'][len(df_currMatch)-1] < 0:
        
        #Calculate seconds this margin was present
        timeMargin = totalMatchSeconds - df_currMatch['matchSeconds'][len(df_currMatch)-1]
        
        #Add to away margin time
        awayInFront = awayInFront + timeMargin
        
    #Calculate time tied
    timeTied = totalMatchSeconds - (homeInFront + awayInFront)
    
    #Add to data dictionary
    timeInFront['homeInFront'].append(homeInFront)  
    timeInFront['awayInFront'].append(awayInFront)
    timeInFront['timeTied'].append(timeTied)
    
#Convert the home/away team data to squad ID's

#Set up dictionary to store data in
squadInFront = {'squadId': [], 'timeInFront': [], 'timeBehind': [],
                'timeTied': [], 'totalMatchTime': [],
                'proportionInFront': [], 'proportionBehind': [],
                'proportionTied': []}

#Loop through squads
for ss in range(0,len(squadIds)):
    
    #Set variable for current time in front and behind
    currInFront = 0
    currBehind = 0
    
    #Set variable for time tied
    currTied = 0
    
    #Set variable for total match time
    matchTime = 0
    
    #Extract current squads home match info
    df_currHome = df_matchInfo.loc[(df_matchInfo['homeSquadId'] == squadIds[ss]),]
    
    #Add to total match time from this squads home games
    matchTime = matchTime + sum([sum(i) for i in zip(*list(df_currHome['periodSeconds']))])
    
    #Get the index values of the current 
    matchRows = np.array(df_currHome.index)
    
    #Extract the home and time tied for these matches for in front, away for behind
    currInFront = currInFront + sum(np.array(timeInFront['homeInFront'])[matchRows])
    currBehind = currBehind + sum(np.array(timeInFront['awayInFront'])[matchRows])
    currTied = currTied + sum(np.array(timeInFront['timeTied'])[matchRows])
    
    #Extract current squads awway match info
    df_currAway = df_matchInfo.loc[(df_matchInfo['awaySquadId'] == squadIds[ss]),]
    
    #Add to total match time from this squads home games
    matchTime = matchTime + sum([sum(i) for i in zip(*list(df_currAway['periodSeconds']))])
    
    #Get the index values of the current 
    matchRows = np.array(df_currAway.index)
    
    #Extract the away and time tied for these matches, home for behind
    currInFront = currInFront + sum(np.array(timeInFront['awayInFront'])[matchRows])
    currBehind = currBehind + sum(np.array(timeInFront['homeInFront'])[matchRows])
    currTied = currTied + sum(np.array(timeInFront['timeTied'])[matchRows])
    
    #Calculate proportions
    currProportionInFront = currInFront / matchTime
    currProportionBehind = currBehind / matchTime
    currProportionTied = currTied / matchTime
    
    #Append to dictionary
    squadInFront['squadId'].append(squadIds[ss])
    squadInFront['timeInFront'].append(currInFront)
    squadInFront['timeBehind'].append(currBehind)
    squadInFront['timeTied'].append(currTied)
    squadInFront['totalMatchTime'].append(matchTime)
    squadInFront['proportionInFront'].append(currProportionInFront)
    squadInFront['proportionBehind'].append(currProportionBehind)
    squadInFront['proportionTied'].append(currProportionTied)
    
#Convert dictionary to dataframe
df_squadInFront = pd.DataFrame.from_dict(squadInFront)

#Print output
print('Proportions in front, behind and tied:')
for ss in range(0,len(squadIds)):
    
    #Get current squad nickname
    currSquadName = teamInfo['squadNickname'][teamInfo['squadId'].index(squadIds[ss])]
    
    #Get current data for this team
    lead = df_squadInFront['proportionInFront'][squadInFront['squadId'].index(squadIds[ss])]
    behind = df_squadInFront['proportionBehind'][squadInFront['squadId'].index(squadIds[ss])]
    tied = df_squadInFront['proportionTied'][squadInFront['squadId'].index(squadIds[ss])]
    
    #Print out
    print(currSquadName+':',
          round(lead*100,1),'% in front /',
          round(behind*100,1),'% behind /',
          round(tied*100,1),'% tied')
    
#Calculate and print time in front in each quarter
#NOTE: this only prints, rather than stores data anywhere
for qq in range(0,4):
    
    #Create dictionary to store basic home and away numbers in
    timeInFrontQ = {'homeInFront': [], 'awayInFront': [], 'timeTied': []}
    
    #Loop through matches
    for mm in range(0,len(df_matchInfo)):
        
        #Set starting variables for home and away seconds in front
        homeInFront = 0
        awayInFront = 0
        
        #Get current match info
        roundNo = df_matchInfo['roundNo'][mm]
        matchNo = df_matchInfo['matchNo'][mm]
        
        #Get total match seconds
        totalMatchSeconds = df_matchInfo['periodSeconds'][mm][qq]
        
        #Get home and away squad ID for current match
        homeId = df_matchInfo['homeSquadId'][mm]
        awayId = df_matchInfo['awaySquadId'][mm]
        
        #Extract current match
        df_currMatch = df_scoreFlow.loc[(df_scoreFlow['roundNo'] == roundNo) &
                                        (df_scoreFlow['matchNo'] == matchNo) &
                                        (df_scoreFlow['period'] == qq+1),]
        
        #Reindex score flow dataframe
        df_currMatch.reset_index(drop = True, inplace = True)
        
        #Loop through score flow points
        for pp in range(0,len(df_currMatch)):
            
            #Check for first score and don't calculate as nobody is in front
            if pp > 0:
                
                #Check the pre shot margin
                preMargin = df_currMatch['preShotMargin'][pp]
                
                #If margin is > 1, home has been in front
                if preMargin > 1:
                    
                    #Calculate seconds this margin has been present
                    timeMargin = df_currMatch['matchSeconds'][pp] - df_currMatch['matchSeconds'][pp-1]
                    
                    #Add to home margin time
                    homeInFront = homeInFront + timeMargin
                    
                elif preMargin < 1:
                    
                    #Calculate seconds this margin has been present
                    timeMargin = df_currMatch['matchSeconds'][pp] - df_currMatch['matchSeconds'][pp-1]
                    
                    #Add to away margin time
                    awayInFront = awayInFront + timeMargin
                    
        #Do one more addition for the period between the last score and match end
        if df_currMatch['preShotMargin'][len(df_currMatch)-1] > 0:
            
            #Calculate seconds this margin was present
            timeMargin = totalMatchSeconds - df_currMatch['periodSeconds'][len(df_currMatch)-1]
            
            #Add to home margin time
            homeInFront = homeInFront + timeMargin
            
        elif df_currMatch['preShotMargin'][len(df_currMatch)-1] < 0:
            
            #Calculate seconds this margin was present
            timeMargin = totalMatchSeconds - df_currMatch['periodSeconds'][len(df_currMatch)-1]
            
            #Add to away margin time
            awayInFront = awayInFront + timeMargin
            
        #Calculate time tied
        timeTied = totalMatchSeconds - (homeInFront + awayInFront)
        
        #Add to data dictionary
        timeInFrontQ['homeInFront'].append(homeInFront)  
        timeInFrontQ['awayInFront'].append(awayInFront)
        timeInFrontQ['timeTied'].append(timeTied)
    
    #Print starting header
    print('% Time in front for quarter '+str(qq+1)+':')
    
    #Loop through squads
    for ss in range(0,len(squadIds)):
        
        #Set variable for current time in front and behind
        currInFront = 0
        currBehind = 0
        
        #Set variable for time tied
        currTied = 0
        
        #Set variable for total match time
        matchTime = 0
        
        #Extract current squads home match info
        df_currHome = df_matchInfo.loc[(df_matchInfo['homeSquadId'] == squadIds[ss]),]
        
        #Add to total match time from this squads home games
        matchTime = matchTime + [sum(i) for i in zip(*list(df_currHome['periodSeconds']))][qq]
        
        #Get the index values of the current 
        matchRows = np.array(df_currHome.index)
        
        #Extract the home and time tied for these matches for in front, away for behind
        currInFront = currInFront + sum(np.array(timeInFrontQ['homeInFront'])[matchRows])
        currBehind = currBehind + sum(np.array(timeInFrontQ['awayInFront'])[matchRows])
        currTied = currTied + sum(np.array(timeInFrontQ['timeTied'])[matchRows])
        
        #Extract current squads awway match info
        df_currAway = df_matchInfo.loc[(df_matchInfo['awaySquadId'] == squadIds[ss]),]
        
        #Add to total match time from this squads home games
        matchTime = matchTime + [sum(i) for i in zip(*list(df_currAway['periodSeconds']))][qq]
        
        #Get the index values of the current 
        matchRows = np.array(df_currAway.index)
        
        #Extract the away and time tied for these matches, home for behind
        currInFront = currInFront + sum(np.array(timeInFrontQ['awayInFront'])[matchRows])
        currBehind = currBehind + sum(np.array(timeInFrontQ['homeInFront'])[matchRows])
        currTied = currTied + sum(np.array(timeInFrontQ['timeTied'])[matchRows])
        
        #Calculate proportions
        currProportionInFront = currInFront / matchTime
        currProportionBehind = currBehind / matchTime
        currProportionTied = currTied / matchTime
        
        #Get current squad nickname
        currSquadName = teamInfo['squadNickname'][teamInfo['squadId'].index(squadIds[ss])]
        
        #Print results
        print(currSquadName+':',
              round(currProportionInFront*100,1),'% in front /',
              round(currProportionBehind*100,1),'% behind /',
              round(currProportionTied*100,1),'% tied')
        
# %% Match-up comparisons

# This section looks to extract data from specific match-ups for comparison
# This was driven by the Vixens looking for info on their finals opponents, and
# currently focuses on that - but could equally be applied to other match-ups

#Set the two teams of interest
squadId1 = 804
squadId2 = 810

#Get the squad names
squadName1 = teamInfo['squadNickname'][teamInfo['squadId'].index(squadId1)]
squadName2 = teamInfo['squadNickname'][teamInfo['squadId'].index(squadId2)]

#Get the match ID's and round/match number where these teams played
#There should be two matches for each combination in the regular season
df_currCombo = df_matchInfo.loc[(df_matchInfo['homeSquadId'].isin([squadId1,squadId2])) &
                                (df_matchInfo['awaySquadId'].isin([squadId1,squadId2])),]
df_currCombo.reset_index(drop = True, inplace = True)

#Loop through the two matches and print out some comparative data
for mm in range(0,len(df_currCombo)):
    
    #Current match ID
    matchId = df_currCombo['id'][mm]
    
    #Extract the team statistics for the current match
    df_currStats = df_teamStatsData.loc[(df_teamStatsData['matchId'] == matchId),]
    
    #Get match totals for each team
    df_currTotals = df_currStats.groupby('squadId').sum()
    
    #Print out summary stats for current game
    print(' ')
    print('Summary total stats for game',
          str(mm+1),
          'of',
          squadName1,
          'vs.',
          squadName2)
    
    #Print statistics
    #Final score
    print('Final Score:',
          squadName1,
          str(df_currTotals['goal_from_zone1'][squadId1] + df_currTotals['goal_from_zone2'][squadId1]*2),
          '/',
          squadName2,
          str(df_currTotals['goal_from_zone1'][squadId2] + df_currTotals['goal_from_zone2'][squadId2]*2))
    #Standard shot makes
    print('Standard Shot Makes:',
          squadName1,
          str(df_currTotals['goal_from_zone1'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['goal_from_zone1'][squadId2]))    
    #Standard shot attempts
    print('Standard Shot Attempts:',
          squadName1,
          str(df_currTotals['attempt_from_zone1'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['attempt_from_zone1'][squadId2]))
    #Super shot makes
    print('Super Shot Makes:',
          squadName1,
          str(df_currTotals['goal_from_zone2'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['goal_from_zone2'][squadId2]))    
    #Super shot attempts
    print('Super Shot Attempts:',
          squadName1,
          str(df_currTotals['attempt_from_zone2'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['attempt_from_zone2'][squadId2]))
    #Standard shot percentage
    per1 = round(df_currTotals['goal_from_zone1'][squadId1] / df_currTotals['attempt_from_zone1'][squadId1] * 100,1)
    per2 = round(df_currTotals['goal_from_zone1'][squadId2] / df_currTotals['attempt_from_zone1'][squadId2] * 100,1)
    print('Standard shot shooting %:',
          squadName1,
          str(per1),
          '/',
          squadName2,
          str(per2))
    #Super shot percentage
    per1 = round(df_currTotals['goal_from_zone2'][squadId1] / df_currTotals['attempt_from_zone2'][squadId1] * 100,1)
    per2 = round(df_currTotals['goal_from_zone2'][squadId2] / df_currTotals['attempt_from_zone2'][squadId2] * 100,1)
    print('Super shot shooting %:',
          squadName1,
          str(per1),
          '/',
          squadName2,
          str(per2))
    #Goals from centre pass
    print('Goals from centre pass:',
          squadName1,
          str(df_currTotals['goalsFromCentrePass'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['goalsFromCentrePass'][squadId2]))
    #Goals from gain
    print('Goals from gains:',
          squadName1,
          str(df_currTotals['goalsFromGain'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['goalsFromGain'][squadId2]))
    #Goals from turnovers
    print('Goals from turnovers:',
          squadName1,
          str(df_currTotals['goalsFromTurnovers'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['goalsFromTurnovers'][squadId2]))
    #Circle feeds
    print('Circle feeds:',
          squadName1,
          str(df_currTotals['feeds'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['feeds'][squadId2]))
    #Circle feeds with attempts
    print('Circle feeds with shot attempts:',
          squadName1,
          str(df_currTotals['feedWithAttempt'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['feedWithAttempt'][squadId2]))
    #Deflections with gain
    print('Deflections with gain:',
          squadName1,
          str(df_currTotals['deflectionWithGain'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['deflectionWithGain'][squadId2]))
    #Deflections with no gain
    print('Deflections with no gain:',
          squadName1,
          str(df_currTotals['deflectionWithNoGain'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['deflectionWithNoGain'][squadId2]))
    #General play turnovers
    print('General play turnovers:',
          squadName1,
          str(df_currTotals['generalPlayTurnovers'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['generalPlayTurnovers'][squadId2]))
    #Bad hands
    print('Bad hands:',
          squadName1,
          str(df_currTotals['badHands'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['badHands'][squadId2]))
    #Bad passes
    print('Bad passes:',
          squadName1,
          str(df_currTotals['badPasses'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['badPasses'][squadId2]))
    #Intercepts
    print('Intercepts:',
          squadName1,
          str(df_currTotals['intercepts'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['intercepts'][squadId2]))
    #Contact penalties
    print('Contact penalties:',
          squadName1,
          str(df_currTotals['contactPenalties'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['contactPenalties'][squadId2]))
    #Obstruction penalties
    print('Obstruction penalties:',
          squadName1,
          str(df_currTotals['obstructionPenalties'][squadId1]),
          '/',
          squadName2,
          str(df_currTotals['obstructionPenalties'][squadId2]))
    
#Extract the line-up data for the current match
#NOTE: Wil only work for two matches
df_lineUp1 = df_lineUp.loc[(df_lineUp['roundNo'] == df_currCombo['roundNo'][0]) &
                           (df_lineUp['matchNo'] == df_currCombo['matchNo'][0]),]
df_lineUp2 = df_lineUp.loc[(df_lineUp['roundNo'] == df_currCombo['roundNo'][1]) &
                           (df_lineUp['matchNo'] == df_currCombo['matchNo'][1]),]

#Combine and clean dataframe
df_lineUpCombo = pd.concat([df_lineUp1,df_lineUp2])
df_lineUpCombo.reset_index(drop = True, inplace = True)
df_lineUpCombo.drop(['lineUpId','lineUpName'], inplace = True, axis = 1)

#Get some sums for line up data
df_lineUpSums = df_lineUpCombo.groupby(['roundNo',
                                        'squadId',
                                        'combinedLineUpName'])[['durationSeconds',
                                                                'pointsFor',
                                                                'pointsAgainst',
                                                                'plusMinus']].sum(['durationSeconds'])

#Check out score flow data from each game
#Loop through games
for mm in range(0,len(df_currCombo)):
    
    #Current round and match no
    roundNo = df_currCombo['roundNo'][mm]
    matchNo = df_currCombo['matchNo'][mm]
    
    #Extract score flow data for current match
    df_currScore = df_scoreFlow.loc[(df_scoreFlow['roundNo'] == roundNo) &
                                    (df_scoreFlow['matchNo'] == matchNo),]
    
    #Group by players and sum scoring data to see who were most effective scorers
    df_scoreSums = df_currScore.groupby(['squadId','playerId','scoreName'])[['scorePoints']].sum()
    df_scoreSums.reset_index(drop = False, inplace = True)                         
    
    #Print out data
    print(' ')
    print('Scoring summary from game '+str(mm+1))
    for pp in range(0,len(df_scoreSums)):
        #Get player name
        currName = playerInfo['displayName'][playerInfo['playerId'].index(df_scoreSums['playerId'][pp])]
        #Print out current data
        print(currName+' '+df_scoreSums['scoreName'][pp]+' Total: '+str(df_scoreSums['scorePoints'][pp]))
                                   
# %% Calculate some basic substitution statistics

#### SEE DATA HELPER FUNCTION...
    
# %% Super shot period score simulator

##### Moved to own function...


# %% Super shot period score simulator with RiskFactor

# This analysis repeats the above score simulator, but considers a 'RiskFactor'
# for whether the super shot opportunity can actually be attempted. This goes 
# with the theory that teams might be turning the ball over in an attempt to try
# and get into a super shot position. Here we set a factor that sets the probability
# that the super shot attempt will be available.

##### TODO: we can package these up together as functions with options...

#Set the risk factor to 0.75, meaning that there is a 25% chance that the 
#super shot attempt will not get taken
superRiskFactor = 0.75

#Create dictionary to store data in
superSimResults_RiskFac = {'squadId': [], 'squadNickname': [],
                           'nShots': [], 'nStandard': [], 'nSuper': [],
                           'superProp': [], 'superPropCat': [], 'totalPts': []}

#Loop through teams
for tt in range(0,len(teamList)):
    
    #Set current squad labels
    currSquadId = teamInfo['squadId'][teamInfo['squadNickname'].index(teamList[tt])]
    currSquadName = teamInfo['squadNickname'][teamInfo['squadId'].index(currSquadId)]

    #Extract a dataframe of shots for the current team during super shot period
    df_currSquadShots = df_scoreFlow.loc[(df_scoreFlow['squadId'] == currSquadId) &
                                         (df_scoreFlow['periodCategory'] == 'twoPoint'),]
    
    #Loop through rounds, extract frequencies for different shots
    #Get number of rounds
    nRounds = max(df_currSquadShots['roundNo'])
    #Set lists to store data in
    madeStandard = list()
    missedStandard = list()
    madeSuper = list()
    missedSuper = list()
    totalShots = list()
    #Get data from each round
    for rr in range(0,nRounds):
        #Loop through quarters within rounds too
        for qq in range(0,4):
            #Made standard shots
            madeStandard.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                      (df_currSquadShots['period'] == qq+1) & 
                                                      (df_currSquadShots['scoreName'] == 'goal'),
                                                      ['roundNo']].count()[0])
            #Missed standard shots
            missedStandard.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                        (df_currSquadShots['period'] == qq+1) & 
                                                        (df_currSquadShots['scoreName'] == 'miss'),
                                                        ['roundNo']].count()[0])
            #Made super shots
            madeSuper.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                   (df_currSquadShots['period'] == qq+1) & 
                                                   (df_currSquadShots['scoreName'] == '2pt Goal'),
                                                   ['roundNo']].count()[0])
            #Missed standard shots
            missedSuper.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                     (df_currSquadShots['period'] == qq+1) & 
                                                     (df_currSquadShots['scoreName'] == '2pt Miss'),
                                                     ['roundNo']].count()[0])
            #Total shots
            totalShots.append(madeStandard[rr]+missedStandard[rr]+madeSuper[rr]+missedSuper[rr])
    
    #Calculate mean and standard deviation for total shots per quarter
    totalShotsM = np.mean(totalShots)
    totalShotsSD = np.std(totalShots)

    #Create a truncated normal distribution of the total shots mean/SD
    #Truncate it at 0 so that a team can't get less than no shots
    #Randomly sample values from the distribution to use in simulations
    
    #Sample from truncated normal distribution with mean/SD parameters
    #We choose to sample between +/- two standard deviations here. This might
    #mean shots sometimes go below zero, but we have a check in place to not
    #analyse these later
    lowLim = totalShotsM - (2*totalShotsSD)
    uppLim = totalShotsM + (2*totalShotsSD)
    nShotVals = stats.truncnorm((lowLim - totalShotsM) / totalShotsSD,
                                (uppLim - totalShotsM) / totalShotsSD,
                                loc = totalShotsM, scale = totalShotsSD).rvs(nSims)
    #Round shot values to nearest whole number
    nShotVals = np.around(nShotVals)
    
    #Calculate made and missed shots from the different zones for beta distributions
    totalMadeStandard = np.sum(madeStandard)
    totalMissedStandard = np.sum(missedStandard)
    totalMadeSuper = np.sum(madeSuper)
    totalMissedSuper = np.sum(missedSuper)
    
    #Loop through the different super shot proportions
    for pp in range(0,len(superShotProps)):
        
        #Loop through the simulations
        for nn in range(0,nSims):
            
            #Get the current number of shots for the quarter
            nShots = int(nShotVals[nn])
            
            #Put a check in place to see if any shots are given to the team
            #Simply don't run the analysis if there aren't any shots
            if nShots > 0:
            
                #Set total points counter for current iteration
                totalPts = 0
                
                #Get the standard and super shot attempts based on proportion
                nSuper = nShots * superShotProps[pp]
                #Round to ensure a whole number
                nSuper = int(np.around(nSuper))
                #Get standard based on difference
                nStandard = int(nShots - nSuper)
                
                #Correct the number of super shots based on the risk factor
                nSuper_RiskFac = 0
                for rr in range(0,nSuper):
                    #Get random number generated for shot attempt
                    r = random.random()
                    #Check against risk factor and add to shot number if successful
                    if r < superRiskFactor:
                        nSuper_RiskFac = nSuper_RiskFac + 1
                
                #Recalculate total number of shots
                nSuper = nSuper_RiskFac
                nShots = nStandard + nSuper
                
                #Recheck if there are any shots to progress analysis
                if nShots > 0:
                
                    #Calculate the actual proportion of the current super shot number
                    actualProp = nSuper / nShots
                    
                    #Set super shot category bin
                    if actualProp <= 0.1:
                        propCat = '0%-10%'
                    elif actualProp > 0.1 and actualProp <= 0.2:
                        propCat = '10%-20%'
                    elif actualProp > 0.2 and actualProp <= 0.3:
                        propCat = '20%-30%'
                    elif actualProp > 0.3 and actualProp <= 0.4:
                        propCat = '30%-40%'
                    elif actualProp > 0.4 and actualProp <= 0.5:
                        propCat = '40%-50%'
                    elif actualProp > 0.5 and actualProp <= 0.6:
                        propCat = '50%-60%'
                    elif actualProp > 0.6 and actualProp <= 0.7:
                        propCat = '60%-70%'
                    elif actualProp > 0.7 and actualProp <= 0.8:
                        propCat = '70%-80%'
                    elif actualProp > 0.8 and actualProp <= 0.9:
                        propCat = '80%-90%'
                    elif actualProp > 0.9:
                        propCat = '90%-100%'
                    
                    #Loop through standard shots and determine score
                    if nStandard > 0:
                        #Sample shot success probability for the shots from beta distribution
                        shotProb = np.random.beta(totalMadeStandard, totalMissedStandard,
                                                  size = nStandard)
                        #Loop through shots            
                        for ss in range(0,nStandard):
                            #Get random number to determine shot success
                            r = random.random()
                            #Check shot success and add to total points if successful
                            if r < shotProb[ss]:
                                totalPts = totalPts + 1
                        
                    #Loop through super shots and determine score
                    if nSuper > 0:
                        #Sample shot success probability for the shots from beta distribution
                        shotProb = np.random.beta(totalMadeSuper, totalMissedSuper,
                                                  size = nSuper)
                        #Loop through shots            
                        for ss in range(0,nSuper):
                            #Get random number to determine shot success
                            r = random.random()
                            #Check shot success and add to total points if successful
                            if r < shotProb[ss]:
                                totalPts = totalPts + 2
                                
                    #Store values in dictionary
                    superSimResults_RiskFac['squadId'].append(currSquadId)
                    superSimResults_RiskFac['squadNickname'].append(currSquadName)
                    superSimResults_RiskFac['nShots'].append(nShots)
                    superSimResults_RiskFac['nStandard'].append(nStandard)
                    superSimResults_RiskFac['nSuper'].append(nSuper)
                    superSimResults_RiskFac['superProp'].append(actualProp)
                    superSimResults_RiskFac['superPropCat'].append(propCat)
                    superSimResults_RiskFac['totalPts'].append(totalPts)

#Convert sim dictionary to dataframe
df_superSimResults_RiskFac = pd.DataFrame.from_dict(superSimResults_RiskFac)

#Create a boxplot of the simulation results

#Initialize the figure
fig, axes = plt.subplots(nrows = 2, ncols = 4, figsize=(15, 7))

#Loop through the teams
for tt in range(0,len(teamList)):

    #Get current squad name
    currSquadName = teamList[tt]
    
    #Create the boxplot
    gx = sns.boxplot(x = 'superPropCat', y = 'totalPts',
                     data = df_superSimResults_RiskFac.loc[(df_superSimResults_RiskFac['squadNickname'] == currSquadName),],
                     whis = [0, 100], width = 0.65,
                     color = colourDict[currSquadName],
                     ax = axes[whichAx[tt][0],whichAx[tt][1]])
    
    #Set the box plot face and line colours
    
    #First, identify the box to keep solid based on teams actual super shot proportions
    solidBarInd = int(np.floor(teamSuperProps[tt]*10))
    
    #Loop through boxes and fix colours
    for ii in range(0,len(axes[whichAx[tt][0],whichAx[tt][1]].artists)):
        
        #Get the current artist
        artist = axes[whichAx[tt][0],whichAx[tt][1]].artists[ii]
        
        #If the bar matches the one we want to keep solid, just change lines to black
        if ii == solidBarInd:
            
            #Set edge colour to black
            artist.set_edgecolor('k')
            
            #Each box has 6 associated Line2D objects (to make the whiskers, fliers, etc.)
            #Loop over them here, and use black
            for jj in range(ii*6,ii*6+6):
                line = axes[whichAx[tt][0],whichAx[tt][1]].lines[jj]
                line.set_color('k')
                line.set_mfc('k')
                line.set_mec('k')
                
        else:
            
            #Set the linecolor on the artist to the facecolor, and set the facecolor to None
            col = artist.get_facecolor()
            artist.set_edgecolor(col)
            artist.set_facecolor('None')
            
            #Each box has 6 associated Line2D objects (to make the whiskers, fliers, etc.)
            #Loop over them here, and use the same colour as above
            for jj in range(ii*6,ii*6+6):
                line = axes[whichAx[tt][0],whichAx[tt][1]].lines[jj]
                line.set_color(col)
                line.set_mfc(col)
                line.set_mec(col)
    
    #Set x labels only for bottom row
    if whichAx[tt][0] == 1:
        gx.set(xlabel = 'Proportion of Total Shots as Super Shots')
    else:
        gx.set(xlabel = '')
        
    #Set y label only for first column
    if whichAx[tt][1] == 0:
        gx.set(ylabel = 'Simulated Score')
    else:
        gx.set(ylabel = '')
        
    #Rotate x-tick labels, but only for bottom row
    if whichAx[tt][0] == 1:
        axes[whichAx[tt][0],whichAx[tt][1]].tick_params('x', labelrotation = 45)
    else:
        axes[whichAx[tt][0],whichAx[tt][1]].set_xticklabels([])
    
    #Point ticks in and make short
    axes[whichAx[tt][0],whichAx[tt][1]].tick_params(axis = 'both',
                                                    direction = 'in',
                                                    length = 1.5)
    
    #Set title
    axes[whichAx[tt][0],whichAx[tt][1]].set_title(currSquadName,
                                                  fontdict = {'fontsize': 12,
                                                              'fontweight': 'bold'})

#Set tight layout on figure
fig.tight_layout()

#Loop through and set y-axes to be consistent

#Use the same Y max as last time for ease of comparison

#Reset all of the axes ticks to min and new max
#Also set the tick labels to have 6 ticks here
for tt in range(0,len(teamList)):
    axes[whichAx[tt][0],whichAx[tt][1]].set_ylim([axes[whichAx[tt][0],whichAx[tt][1]].get_ylim()[0],
                                                  currYmax])
    axes[whichAx[tt][0],whichAx[tt][1]].set_yticks(np.arange(0, currYmax+1, step = currYmax/6))

#Export figure

#Export as PDF and basic png
plt.savefig('SuperShotSimulations_RiskFactor'+str(int(np.around(superRiskFactor*100)))+'per.png', format = 'png', dpi = 300)

#Close figure
plt.close()

# %% Super shot period score simulator with RiskFactor & standard supplementer

# This analysis repeats the above RiskFactor analysis, but during the times where
# the super shot opportunity is missed it supplements it with a standard shot.
# This emulates scenarios where the team sacrifices the need to go for a super
# shot for an easier standard shot.

##### TODO: we can package these up together as functions with options...

#Set the risk factor to 0.75, meaning that there is a 25% chance that the 
#super shot attempt will not get taken
superRiskFactor = 0.75

#Create dictionary to store data in
superSimResults_RiskFac_Supp = {'squadId': [], 'squadNickname': [],
                                'nShots': [], 'nStandard': [], 'nSuper': [],
                                'superProp': [], 'superPropCat': [], 'totalPts': []}

#Loop through teams
for tt in range(0,len(teamList)):
    
    #Set current squad labels
    currSquadId = teamInfo['squadId'][teamInfo['squadNickname'].index(teamList[tt])]
    currSquadName = teamInfo['squadNickname'][teamInfo['squadId'].index(currSquadId)]

    #Extract a dataframe of shots for the current team during super shot period
    df_currSquadShots = df_scoreFlow.loc[(df_scoreFlow['squadId'] == currSquadId) &
                                         (df_scoreFlow['periodCategory'] == 'twoPoint'),]
    
    #Loop through rounds, extract frequencies for different shots
    #Get number of rounds
    nRounds = max(df_currSquadShots['roundNo'])
    #Set lists to store data in
    madeStandard = list()
    missedStandard = list()
    madeSuper = list()
    missedSuper = list()
    totalShots = list()
    #Get data from each round
    for rr in range(0,nRounds):
        #Loop through quarters within rounds too
        for qq in range(0,4):
            #Made standard shots
            madeStandard.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                      (df_currSquadShots['period'] == qq+1) & 
                                                      (df_currSquadShots['scoreName'] == 'goal'),
                                                      ['roundNo']].count()[0])
            #Missed standard shots
            missedStandard.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                        (df_currSquadShots['period'] == qq+1) & 
                                                        (df_currSquadShots['scoreName'] == 'miss'),
                                                        ['roundNo']].count()[0])
            #Made super shots
            madeSuper.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                   (df_currSquadShots['period'] == qq+1) & 
                                                   (df_currSquadShots['scoreName'] == '2pt Goal'),
                                                   ['roundNo']].count()[0])
            #Missed standard shots
            missedSuper.append(df_currSquadShots.loc[(df_currSquadShots['roundNo'] == rr+1) & 
                                                     (df_currSquadShots['period'] == qq+1) & 
                                                     (df_currSquadShots['scoreName'] == '2pt Miss'),
                                                     ['roundNo']].count()[0])
            #Total shots
            totalShots.append(madeStandard[rr]+missedStandard[rr]+madeSuper[rr]+missedSuper[rr])
    
    #Calculate mean and standard deviation for total shots per quarter
    totalShotsM = np.mean(totalShots)
    totalShotsSD = np.std(totalShots)

    #Create a truncated normal distribution of the total shots mean/SD
    #Truncate it at 0 so that a team can't get less than no shots
    #Randomly sample values from the distribution to use in simulations
    
    #Sample from truncated normal distribution with mean/SD parameters
    #We choose to sample between +/- two standard deviations here. This might
    #mean shots sometimes go below zero, but we have a check in place to not
    #analyse these later
    lowLim = totalShotsM - (2*totalShotsSD)
    uppLim = totalShotsM + (2*totalShotsSD)
    nShotVals = stats.truncnorm((lowLim - totalShotsM) / totalShotsSD,
                                (uppLim - totalShotsM) / totalShotsSD,
                                loc = totalShotsM, scale = totalShotsSD).rvs(nSims)
    #Round shot values to nearest whole number
    nShotVals = np.around(nShotVals)
    
    #Calculate made and missed shots from the different zones for beta distributions
    totalMadeStandard = np.sum(madeStandard)
    totalMissedStandard = np.sum(missedStandard)
    totalMadeSuper = np.sum(madeSuper)
    totalMissedSuper = np.sum(missedSuper)
    
    #Loop through the different super shot proportions
    for pp in range(0,len(superShotProps)):
        
        #Loop through the simulations
        for nn in range(0,nSims):
            
            #Get the current number of shots for the quarter
            nShots = int(nShotVals[nn])
            
            #Put a check in place to see if any shots are given to the team
            #Simply don't run the analysis if there aren't any shots
            if nShots > 0:
            
                #Set total points counter for current iteration
                totalPts = 0
                
                #Get the standard and super shot attempts based on proportion
                nSuper = nShots * superShotProps[pp]
                #Round to ensure a whole number
                nSuper = int(np.around(nSuper))
                #Get standard based on difference
                nStandard = int(nShots - nSuper)
                
                #Correct the number of super shots based on the risk factor
                nSuper_RiskFac = 0
                for rr in range(0,nSuper):
                    #Get random number generated for shot attempt
                    r = random.random()
                    #Check against risk factor and add to shot number if successful
                    if r < superRiskFactor:
                        nSuper_RiskFac = nSuper_RiskFac + 1
                    else:
                        #Add the sacrificed shot to standard shots
                        nStandard = nStandard + 1
                
                #Recalculate total number of shots
                nSuper = nSuper_RiskFac
                nShots = nStandard + nSuper
                
                #Recheck if there are any shots to progress analysis
                if nShots > 0:
                
                    #Calculate the actual proportion of the current super shot number
                    actualProp = nSuper / nShots
                    
                    #Set super shot category bin
                    if actualProp <= 0.1:
                        propCat = '0%-10%'
                    elif actualProp > 0.1 and actualProp <= 0.2:
                        propCat = '10%-20%'
                    elif actualProp > 0.2 and actualProp <= 0.3:
                        propCat = '20%-30%'
                    elif actualProp > 0.3 and actualProp <= 0.4:
                        propCat = '30%-40%'
                    elif actualProp > 0.4 and actualProp <= 0.5:
                        propCat = '40%-50%'
                    elif actualProp > 0.5 and actualProp <= 0.6:
                        propCat = '50%-60%'
                    elif actualProp > 0.6 and actualProp <= 0.7:
                        propCat = '60%-70%'
                    elif actualProp > 0.7 and actualProp <= 0.8:
                        propCat = '70%-80%'
                    elif actualProp > 0.8 and actualProp <= 0.9:
                        propCat = '80%-90%'
                    elif actualProp > 0.9:
                        propCat = '90%-100%'
                    
                    #Loop through standard shots and determine score
                    if nStandard > 0:
                        #Sample shot success probability for the shots from beta distribution
                        shotProb = np.random.beta(totalMadeStandard, totalMissedStandard,
                                                  size = nStandard)
                        #Loop through shots            
                        for ss in range(0,nStandard):
                            #Get random number to determine shot success
                            r = random.random()
                            #Check shot success and add to total points if successful
                            if r < shotProb[ss]:
                                totalPts = totalPts + 1
                        
                    #Loop through super shots and determine score
                    if nSuper > 0:
                        #Sample shot success probability for the shots from beta distribution
                        shotProb = np.random.beta(totalMadeSuper, totalMissedSuper,
                                                  size = nSuper)
                        #Loop through shots            
                        for ss in range(0,nSuper):
                            #Get random number to determine shot success
                            r = random.random()
                            #Check shot success and add to total points if successful
                            if r < shotProb[ss]:
                                totalPts = totalPts + 2
                                
                    #Store values in dictionary
                    superSimResults_RiskFac_Supp['squadId'].append(currSquadId)
                    superSimResults_RiskFac_Supp['squadNickname'].append(currSquadName)
                    superSimResults_RiskFac_Supp['nShots'].append(nShots)
                    superSimResults_RiskFac_Supp['nStandard'].append(nStandard)
                    superSimResults_RiskFac_Supp['nSuper'].append(nSuper)
                    superSimResults_RiskFac_Supp['superProp'].append(actualProp)
                    superSimResults_RiskFac_Supp['superPropCat'].append(propCat)
                    superSimResults_RiskFac_Supp['totalPts'].append(totalPts)

#Convert sim dictionary to dataframe
df_superSimResults_RiskFac_Supp = pd.DataFrame.from_dict(superSimResults_RiskFac_Supp)

#Create a boxplot of the simulation results

#Initialize the figure
fig, axes = plt.subplots(nrows = 2, ncols = 4, figsize=(15, 7))

#Loop through the teams
for tt in range(0,len(teamList)):

    #Get current squad name
    currSquadName = teamList[tt]
    
    #Create the boxplot
    gx = sns.boxplot(x = 'superPropCat', y = 'totalPts',
                     data = df_superSimResults_RiskFac_Supp.loc[(df_superSimResults_RiskFac_Supp['squadNickname'] == currSquadName),],
                     whis = [0, 100], width = 0.65,
                     color = colourDict[currSquadName],
                     ax = axes[whichAx[tt][0],whichAx[tt][1]])
    
    #Set the box plot face and line colours
    
    #First, identify the box to keep solid based on teams actual super shot proportions
    solidBarInd = int(np.floor(teamSuperProps[tt]*10))
    
    #Loop through boxes and fix colours
    for ii in range(0,len(axes[whichAx[tt][0],whichAx[tt][1]].artists)):
        
        #Get the current artist
        artist = axes[whichAx[tt][0],whichAx[tt][1]].artists[ii]
        
        #If the bar matches the one we want to keep solid, just change lines to black
        if ii == solidBarInd:
            
            #Set edge colour to black
            artist.set_edgecolor('k')
            
            #Each box has 6 associated Line2D objects (to make the whiskers, fliers, etc.)
            #Loop over them here, and use black
            for jj in range(ii*6,ii*6+6):
                line = axes[whichAx[tt][0],whichAx[tt][1]].lines[jj]
                line.set_color('k')
                line.set_mfc('k')
                line.set_mec('k')
                
        else:
            
            #Set the linecolor on the artist to the facecolor, and set the facecolor to None
            col = artist.get_facecolor()
            artist.set_edgecolor(col)
            artist.set_facecolor('None')
            
            #Each box has 6 associated Line2D objects (to make the whiskers, fliers, etc.)
            #Loop over them here, and use the same colour as above
            for jj in range(ii*6,ii*6+6):
                line = axes[whichAx[tt][0],whichAx[tt][1]].lines[jj]
                line.set_color(col)
                line.set_mfc(col)
                line.set_mec(col)
    
    #Set x labels only for bottom row
    if whichAx[tt][0] == 1:
        gx.set(xlabel = 'Proportion of Total Shots as Super Shots')
    else:
        gx.set(xlabel = '')
        
    #Set y label only for first column
    if whichAx[tt][1] == 0:
        gx.set(ylabel = 'Simulated Score')
    else:
        gx.set(ylabel = '')
        
    #Rotate x-tick labels, but only for bottom row
    if whichAx[tt][0] == 1:
        axes[whichAx[tt][0],whichAx[tt][1]].tick_params('x', labelrotation = 45)
    else:
        axes[whichAx[tt][0],whichAx[tt][1]].set_xticklabels([])
    
    #Point ticks in and make short
    axes[whichAx[tt][0],whichAx[tt][1]].tick_params(axis = 'both',
                                                    direction = 'in',
                                                    length = 1.5)
    
    #Set title
    axes[whichAx[tt][0],whichAx[tt][1]].set_title(currSquadName,
                                                  fontdict = {'fontsize': 12,
                                                              'fontweight': 'bold'})

#Set tight layout on figure
fig.tight_layout()

#Loop through and set y-axes to be consistent

#Use the same Y max as last time for ease of comparison

#Reset all of the axes ticks to min and new max
#Also set the tick labels to have 6 ticks here
for tt in range(0,len(teamList)):
    axes[whichAx[tt][0],whichAx[tt][1]].set_ylim([axes[whichAx[tt][0],whichAx[tt][1]].get_ylim()[0],
                                                  currYmax])
    axes[whichAx[tt][0],whichAx[tt][1]].set_yticks(np.arange(0, currYmax+1, step = currYmax/6))

#Export figure

#Export as PDF and basic png
plt.savefig('SuperShotSimulations_RiskFactor'+str(int(np.around(superRiskFactor*100)))+'per_StandardSupp.png', format = 'png', dpi = 300)

#Close figure
plt.close()

# %% Export summary data for reactable

# The plot below doesn't present the data that well, so we'll test out the R
# package reactable for creating a summary html table of this data. This requires
# creating a summary of the results to present. See below code for details.
# For the table we'll colate into 20% intervals rather than 10%

#Start with the standard simulator

#Set proportional break points to loop through
propBreakPoints = [[0.00,0.20],[0.20,0.40],[0.40,0.60],[0.60,0.80],[0.80,1.00]]

#Create a dictionary to store values in
standardSimSummary = {'squadName': [],'meanShots': [], 'lbShots': [], 'ubShots': [],
                      'meanScore_0_20': [], 'meanScore_20_40': [], 'meanScore_40_60': [],
                      'meanScore_60_80': [],'meanScore_80_100': [],
                      'sdScore_0_20': [], 'sdScore_20_40': [], 'sdScore_40_60': [],
                      'sdScore_60_80': [],'sdScore_80_100': [],
                      'lbScore_0_20': [], 'lbScore_20_40': [], 'lbScore_40_60': [],
                      'lbScore_60_80': [],'lbScore_80_100': [],
                      'ubScore_0_20': [], 'ubScore_20_40': [], 'ubScore_40_60': [],
                      'ubScore_60_80': [],'ubScore_80_100': []}

#Loop through teams and create the data dictionary
for tt in range(0,len(teamList)):
    
    #Get current squad name
    standardSimSummary['squadName'].append(teamList[tt])
    
    #Get data for the current team
    df_currSquadData = df_superSimResults.loc[(df_superSimResults['squadNickname'] == teamList[tt]),]
    
    #Extract data into appropriate variables
    
    #Number of shots
    d = df_currSquadData['nShots'].to_numpy()
    standardSimSummary['meanShots'].append(np.mean(d))
    standardSimSummary['lbShots'].append(np.min(d))
    standardSimSummary['ubShots'].append(np.max(d))
    
    #Loop through proportional break points and collate scoring data
    for bb in range(0,len(propBreakPoints)):
        d = df_currSquadData.loc[(df_currSquadData['superProp'] > propBreakPoints[bb][0]) & 
                                 (df_currSquadData['superProp'] <= propBreakPoints[bb][1]),['totalPts']]['totalPts'].to_numpy()
        standardSimSummary['meanScore_'+str(int(propBreakPoints[bb][0]*100))+'_'+str(int(propBreakPoints[bb][1]*100))].append(np.mean(d))
        standardSimSummary['sdScore_'+str(int(propBreakPoints[bb][0]*100))+'_'+str(int(propBreakPoints[bb][1]*100))].append(np.std(d))
        standardSimSummary['lbScore_'+str(int(propBreakPoints[bb][0]*100))+'_'+str(int(propBreakPoints[bb][1]*100))].append(np.min(d))
        standardSimSummary['ubScore_'+str(int(propBreakPoints[bb][0]*100))+'_'+str(int(propBreakPoints[bb][1]*100))].append(np.max(d))

#Convert to dataframe
df_standardSimSummary = pd.DataFrame.from_dict(standardSimSummary)

#Export to CSV
#####TODO: export to appropriate reactable directory rather than copy-paste
df_standardSimSummary.to_csv('superSimSummary_afterRound'+str(nRounds)+'.csv')

# %% Merge simulator results together and plot comparison

#Add column distinguishing analysis type to each dataframe

#Standard sim
analysisType = ['standardSim'] * len(df_superSimResults)
df_superSimResults['analysisType'] = analysisType

#Standard sim with risk factor
analysisType = ['standardSim_RiskFac'] * len(df_superSimResults_RiskFac)
df_superSimResults_RiskFac['analysisType'] = analysisType

#Standard sim with risk factor but standard supplement
analysisType = ['standardSim_RiskFac_Supp'] * len(df_superSimResults_RiskFac_Supp)
df_superSimResults_RiskFac_Supp['analysisType'] = analysisType

#Concatenate dataframes together vertically
df_superSimResults_all = pd.concat([df_superSimResults,
                                    df_superSimResults_RiskFac,
                                    df_superSimResults_RiskFac_Supp])

#Plot comparison

##### Plot doesn't look great --- send out dataframes to .csv for reactable in R

# #Export CSV files
# df_superSimResults.to_csv('superSimResults_afterRound'+str(nRounds)+'.csv')
# df_superSimResults_RiskFac.to_csv('superSimResults_afterRound'+str(nRounds)+'_RiskFac.csv')
# df_superSimResults_RiskFac_Supp.to_csv('superSimResults_afterRound'+str(nRounds)+'_RiskFac_StandardSupp.csv')

##### Copy and paste these to reactable folder...

#Initialize the figure
fig, axes = plt.subplots(nrows = 2, ncols = 4, figsize=(15, 7))

#Loop through the teams
for tt in range(0,len(teamList)):

    #Get current squad name
    currSquadName = teamList[tt]
    
    #Create the boxplot
    gx = sns.boxplot(x = 'superPropCat', y = 'totalPts', hue = 'analysisType',
                     data = df_superSimResults_all.loc[(df_superSimResults_all['squadNickname'] == currSquadName),],
                     whis = [0, 100], width = 1,
                     color = colourDict[currSquadName],
                     ax = axes[whichAx[tt][0],whichAx[tt][1]])
    
    #Set the box plot face and line colours
    
    #First, identify the box to keep solid based on teams actual super shot proportions
    solidBarInd = int(np.floor(teamSuperProps[tt]*10))
    
    #Loop through boxes and fix colours
    for ii in range(0,len(axes[whichAx[tt][0],whichAx[tt][1]].artists)):
        
        #Get the current artist
        artist = axes[whichAx[tt][0],whichAx[tt][1]].artists[ii]
        
        #If the bar matches the one we want to keep solid, just change lines to black
        if ii == solidBarInd:
            
            #Set edge colour to black
            artist.set_edgecolor('k')
            
            #Each box has 6 associated Line2D objects (to make the whiskers, fliers, etc.)
            #Loop over them here, and use black
            for jj in range(ii*6,ii*6+6):
                line = axes[whichAx[tt][0],whichAx[tt][1]].lines[jj]
                line.set_color('k')
                line.set_mfc('k')
                line.set_mec('k')
                
        else:
            
            #Set the linecolor on the artist to the facecolor, and set the facecolor to None
            col = artist.get_facecolor()
            artist.set_edgecolor(col)
            artist.set_facecolor('None')
            
            #Each box has 6 associated Line2D objects (to make the whiskers, fliers, etc.)
            #Loop over them here, and use the same colour as above
            for jj in range(ii*6,ii*6+6):
                line = axes[whichAx[tt][0],whichAx[tt][1]].lines[jj]
                line.set_color(col)
                line.set_mfc(col)
                line.set_mec(col)
    
    #Set x labels only for bottom row
    if whichAx[tt][0] == 1:
        gx.set(xlabel = 'Proportion of Total Shots as Super Shots')
    else:
        gx.set(xlabel = '')
        
    #Set y label only for first column
    if whichAx[tt][1] == 0:
        gx.set(ylabel = 'Simulated Score')
    else:
        gx.set(ylabel = '')
        
    #Rotate x-tick labels, but only for bottom row
    if whichAx[tt][0] == 1:
        axes[whichAx[tt][0],whichAx[tt][1]].tick_params('x', labelrotation = 45)
    else:
        axes[whichAx[tt][0],whichAx[tt][1]].set_xticklabels([])
    
    #Point ticks in and make short
    axes[whichAx[tt][0],whichAx[tt][1]].tick_params(axis = 'both',
                                                    direction = 'in',
                                                    length = 1.5)
    
    #Set title
    axes[whichAx[tt][0],whichAx[tt][1]].set_title(currSquadName,
                                                  fontdict = {'fontsize': 12,
                                                              'fontweight': 'bold'})

#Set tight layout on figure
fig.tight_layout()








