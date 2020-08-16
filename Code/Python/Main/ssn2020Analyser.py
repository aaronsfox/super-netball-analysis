# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 20:07:40 2020

Author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au

This script serves to analyse various aspects of the Super Netball 2020 season.
It will be continuously updated with different aspects depending on what analysis 
is of interest, and leverages a number of functions in the supplementart code folder
of this repo. The script uses the .json files grabbed using the superNetballR package
and collates data into Pandas dataframe format to analyse and visualise.

"""

# %% Import packages

import pandas as pd
import numpy as np
import scipy.stats as stats
import random
import seaborn as sns
import matplotlib.pyplot as plt
pd.options.mode.chained_assignment = None #turn of pandas chained warnings
import os
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import gridplot
from bokeh.models import FactorRange, ColumnDataSource, Legend, HoverTool
from bokeh.transform import factor_cmap
from bokeh.io import show
from bokeh.io import export_png
import json

#Navigate to supplementary directory and import helper scripts
os.chdir('..\\Supplementary')
import ssn2020FigHelper as figHelper

##### TODO: import figHelper script as 'figHelper'

# %% Load in match data

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

#Create blank dictionaries to store data in

#####TODO: convert whole import data to a function

#Match info
matchInfo = {'id': [], 'homeSquadId': [], 'awaySquadId': [],
             'startTime': [], 'roundNo': [], 'matchNo': [],
             'venueId': [], 'venueName': [], 'periodSeconds': []}

#Team info
teamInfo = {'squadCode': [], 'squadId': [],
            'squadName': [], 'squadNickname': []}

#Player info
playerInfo = {'playerId': [], 'displayName': [],
              'firstName': [], 'surname': [],
              'shortDisplayName': [], 'squadId': []}

#Score flow data
scoreFlowData = {'roundNo': [], 'matchNo': [],
                 'period': [], 'periodSeconds': [], 'periodCategory': [], 'matchSeconds': [],
                 'playerId': [],'squadId': [], 'scoreName': [], 'shotOutcome': [], 'scorePoints': [],
                 'distanceCode': [], 'positionCode': [], 'shotCircle': []}

#Substitution data
substitutionData = {'roundNo': [], 'matchNo': [],
                    'period': [], 'periodSeconds': [], 'matchSeconds': [],
                    'playerId': [], 'squadId': [], 'fromPos': [], 'toPos': []}

#Line-up data
lineUpData = {'lineUpId': [], 'lineUpName': [], 'matchNo': [], 'roundNo': [], 'squadId': [],
              'matchSecondsStart': [], 'matchSecondsEnd': [], 'durationSeconds': [],
              'pointsFor': [], 'pointsAgainst': [], 'plusMinus': []}

#Individual player data
individualLineUpData = {'playerId': [], 'playerName':[], 'squadId': [], 'playerPosition': [],
                        'roundNo': [], 'matchNo': [],
                        'matchSecondsStart': [], 'matchSecondsEnd': [], 'durationSeconds': [],
                        'pointsFor': [], 'pointsAgainst': [], 'plusMinus': []}

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
    qtrSeconds = list()
    for qq in range(0,4):
        qtrSeconds.append(data['periodInfo']['qtr'][qq]['periodSeconds'][0])
    matchInfo['periodSeconds'].append(qtrSeconds)

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
    for pp in range(0,len(data['playerInfo']['player'])):
        #First, check if the player ID is in the current id list
        currPlayerId = playerInfo['playerId']
        if data['playerInfo']['player'][pp]['playerId'][0] not in currPlayerId:
            #Grab the new player details
            playerInfo['playerId'].append(data['playerInfo']['player'][pp]['playerId'][0])
            playerInfo['displayName'].append(data['playerInfo']['player'][pp]['displayName'][0])
            playerInfo['firstName'].append(data['playerInfo']['player'][pp]['firstname'][0])
            playerInfo['surname'].append(data['playerInfo']['player'][pp]['surname'][0])
            playerInfo['shortDisplayName'].append(data['playerInfo']['player'][pp]['shortDisplayName'][0])
            #Find which squad they belong to in the squad list dataframe
            currPlayerSquad = df_squadLists.loc[(df_squadLists['displayName'] == \
                                                 data['playerInfo']['player'][pp]['displayName'][0]),\
                                                ].reset_index()['squadNickname'][0]
            #Get the squad ID from the team info and append to players info
            currPlayerSquadId = teamInfo['squadId'][teamInfo['squadNickname'].index(currPlayerSquad)]
            playerInfo['squadId'].append(currPlayerSquadId)
            
    #Extract score flow data
    for ss in range(0,len(data['scoreFlow']['score'])):
        scoreFlowData['roundNo'].append(data['matchInfo']['roundNumber'][0])
        scoreFlowData['matchNo'].append(data['matchInfo']['matchNumber'][0])
        scoreFlowData['period'].append(data['scoreFlow']['score'][ss]['period'][0])
        scoreFlowData['periodSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0])
        ##### TODO: check that this period seconds check holds up to rules...
        if data['scoreFlow']['score'][ss]['periodSeconds'][0] > 600:
            scoreFlowData['periodCategory'].append('twoPoint')
        else:
            scoreFlowData['periodCategory'].append('standard')
        if data['scoreFlow']['score'][ss]['period'][0] == 1:
            #Just use period seconds
            scoreFlowData['matchSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0])
        elif data['scoreFlow']['score'][ss]['period'][0] == 2:
            #Add the preceding period seconds
            scoreFlowData['matchSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0])
        elif data['scoreFlow']['score'][ss]['period'][0] == 3:
            #Add the preceding period seconds
            scoreFlowData['matchSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0] + matchInfo['periodSeconds'][ff][1])
        elif data['scoreFlow']['score'][ss]['period'][0] == 4:
            #Add the preceding period seconds
            scoreFlowData['matchSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0] + matchInfo['periodSeconds'][ff][1] + matchInfo['periodSeconds'][ff][2])
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
    
    #Extract substitution data
    for ss in range(0,len(data['playerSubs']['player'])):
        #Get current round and match number from match data
        substitutionData['roundNo'].append(matchInfo['roundNo'][ff])
        substitutionData['matchNo'].append(matchInfo['matchNo'][ff])
        #Get period and period seconds
        substitutionData['period'].append(data['playerSubs']['player'][ss]['period'][0])
        substitutionData['periodSeconds'].append(data['playerSubs']['player'][ss]['periodSeconds'][0])
        #Convert to match seconds based on match info and period number
        if data['playerSubs']['player'][ss]['period'][0] == 1:
            #Just use the period seconds
            substitutionData['matchSeconds'].append(data['playerSubs']['player'][ss]['periodSeconds'][0])
        elif data['playerSubs']['player'][ss]['period'][0] == 2:
            #Add the matches period 1 seconds to the total
            newSeconds = data['playerSubs']['player'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0]
            #Add to data dictionary
            substitutionData['matchSeconds'].append(newSeconds)
        elif data['playerSubs']['player'][ss]['period'][0] == 3:
            #Add the matches period 1 & 2 seconds to the total
            newSeconds = data['playerSubs']['player'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0] + matchInfo['periodSeconds'][ff][1]
            #Add to data dictionary
            substitutionData['matchSeconds'].append(newSeconds)
        elif data['playerSubs']['player'][ss]['period'][0] == 4:
            #Add the matches period 1, 2 & 3 seconds to the total
            newSeconds = data['playerSubs']['player'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0] + matchInfo['periodSeconds'][ff][1] + matchInfo['periodSeconds'][ff][2]
            #Add to data dictionary
            substitutionData['matchSeconds'].append(newSeconds)
        #Get player and squad ID's
        substitutionData['playerId'].append(data['playerSubs']['player'][ss]['playerId'][0])
        substitutionData['squadId'].append(data['playerSubs']['player'][ss]['squadId'][0])
        #Get substitution positions
        substitutionData['fromPos'].append(data['playerSubs']['player'][ss]['fromPos'][0])
        substitutionData['toPos'].append(data['playerSubs']['player'][ss]['toPos'][0])
                
    #Extract lineup data
    
    ##### TODO: consider adding durations for within one/two-point periods
    
    #Get the squad ID and name order
    if data['teamInfo']['team'][0]['squadId'][0] < data['teamInfo']['team'][1]['squadId'][0]:
        lineUpSquadId1 = data['teamInfo']['team'][0]['squadId'][0]
        lineUpSquadName1 = teamInfo['squadNickname'][teamInfo['squadId'].index(lineUpSquadId1)]
        lineUpSquadId2 = data['teamInfo']['team'][1]['squadId'][0]
        lineUpSquadName2 = teamInfo['squadNickname'][teamInfo['squadId'].index(lineUpSquadId2)]
    else:
        lineUpSquadId1 = data['teamInfo']['team'][1]['squadId'][0]
        lineUpSquadName1 = teamInfo['squadNickname'][teamInfo['squadId'].index(lineUpSquadId1)]
        lineUpSquadId2 = data['teamInfo']['team'][0]['squadId'][0]
        lineUpSquadName2 = teamInfo['squadNickname'][teamInfo['squadId'].index(lineUpSquadId2)]
    
    #Get the starting lineups
    
    #Find the first player in the player list that matches the first squad ID.
    #This should theoretically always be at index 0
    #Set starting search parameters
    playerNo = 0
    startIndSquad1 = []
    #Loop through players
    while not startIndSquad1:
        #Get current player name
        currPlayerName = data['playerInfo']['player'][playerNo]['displayName'][0]
        #Get this players squad ID
        currPlayerSquadId = playerInfo['squadId'][playerInfo['displayName'].index(currPlayerName)]
        #Check if it matches the first squad ID and append if so. This should exit the loop
        if currPlayerSquadId == lineUpSquadId1:
            startIndSquad1.append(playerNo)
        else:
            #Add to the search index for player no
            playerNo = playerNo + 1
            
    #Find the first player in the player list that matches the second squad ID.
    #Set starting search parameters
    playerNo = 0
    startIndSquad2 = []
    #Loop through players
    while not startIndSquad2:
        #Get current player name
        currPlayerName = data['playerInfo']['player'][playerNo]['displayName'][0]
        #Get this players squad ID
        currPlayerSquadId = playerInfo['squadId'][playerInfo['displayName'].index(currPlayerName)]
        #Check if it matches the first squad ID and append if so. This should exit the loop
        if currPlayerSquadId == lineUpSquadId2:
            startIndSquad2.append(playerNo)
        else:
            #Add to the search index for player no
            playerNo = playerNo + 1
            
    #Convert the current substitution data dictionary to a dataframe to use
    #Only extract the subs for the current round and match number
    df_subChecker = pd.DataFrame.from_dict(substitutionData).loc[(pd.DataFrame.from_dict(substitutionData)['roundNo'] == matchInfo['roundNo'][ff]) &
                                                                 (pd.DataFrame.from_dict(substitutionData)['matchNo'] == matchInfo['matchNo'][ff]),]
    
    #Convert the current score flow data dictionary to a dataframe to use
    #Only extract the scores for the current round and match number
    df_scoreChecker = pd.DataFrame.from_dict(scoreFlowData).loc[(pd.DataFrame.from_dict(scoreFlowData)['roundNo'] == matchInfo['roundNo'][ff]) &
                                                                (pd.DataFrame.from_dict(scoreFlowData)['matchNo'] == matchInfo['matchNo'][ff]),]
    
    #Extract each squads lineups
    for nn in range(0,2):
        
        #Set current squad details within loop
        if nn == 0:
            currStartIndSquad = startIndSquad1
            currLineUpSquadId = lineUpSquadId1
            
        else:
            currStartIndSquad = startIndSquad2
            currLineUpSquadId = lineUpSquadId2
    
        #Get the starting lineup
        startLineUpId = list()
        startLineUpName = list()
        for pp in range(currStartIndSquad[0],currStartIndSquad[0]+7):
            startLineUpId.append(data['playerInfo']['player'][pp]['playerId'][0])
            startLineUpName.append(data['playerInfo']['player'][pp]['displayName'][0])
        
        #Get subs for the current squad
        df_subCheckerTeam = df_subChecker.loc[(df_subChecker['squadId'] == currLineUpSquadId),]  
        df_subCheckerTeam.reset_index(drop=True, inplace=True)
        
        #First check if dataframe is empty if a team makes no subs
        if len(df_subCheckerTeam) == 0:
            #No subs made by this team
            #This lineup stays in the whole game and can be treated that way
            #Set lineup ID and names
            lineUpData['lineUpId'].append(startLineUpId)
            lineUpData['lineUpName'].append(startLineUpName)
            lineUpData['squadId'].append(currLineUpSquadId)
            #Set match and round numbers
            lineUpData['roundNo'].append(matchInfo['roundNo'][ff])
            lineUpData['matchNo'].append(matchInfo['matchNo'][ff])
            #Set match seconds start and end to 0 and match length
            lineUpData['matchSecondsStart'].append(0)
            lineUpData['matchSecondsEnd'].append(sum(matchInfo['periodSeconds'][ff]))
            lineUpData['durationSeconds'].append(sum(matchInfo['periodSeconds'][ff]))
            #Set points for the lineup
            #Simply across the whole match
            lineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId),
                                                               ['scorePoints']].sum()['scorePoints'])
            #Set points against the lineup
            #Simply across the whole match
            lineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId),
                                                                   ['scorePoints']].sum()['scorePoints'])
            #Calculate plus/minus
            plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId),
                                            ['scorePoints']].sum()['scorePoints'] - \
                df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId),
                                    ['scorePoints']].sum()['scorePoints']
            lineUpData['plusMinus'].append(plusMinus)
        else:
            #Set the first lineup data based on the first substituion made by the team
            #Set lineup ID and names
            lineUpData['lineUpId'].append(startLineUpId)
            lineUpData['lineUpName'].append(startLineUpName)
            lineUpData['squadId'].append(currLineUpSquadId)
            #Set match and round numbers
            lineUpData['roundNo'].append(matchInfo['roundNo'][ff])
            lineUpData['matchNo'].append(matchInfo['matchNo'][ff])
            #Set match seconds start and end to 0 and the first substitution
            lineUpData['matchSecondsStart'].append(0)
            lineUpData['matchSecondsEnd'].append(df_subCheckerTeam['matchSeconds'][0])
            lineUpData['durationSeconds'].append(df_subCheckerTeam['matchSeconds'][0])
            #Set points for the lineup
            #Search in score flow for less than the substitution end time
            lineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId) &
                                                               (df_scoreChecker['matchSeconds'] <= df_subCheckerTeam['matchSeconds'][0]),
                                                               ['scorePoints']].sum()['scorePoints'])
            #Set points against the lineup
            #Simply across the whole match
            lineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId) &
                                                               (df_scoreChecker['matchSeconds'] <= df_subCheckerTeam['matchSeconds'][0]),
                                                               ['scorePoints']].sum()['scorePoints'])
            #Calculate plus/minus
            plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId) &
                                            (df_scoreChecker['matchSeconds'] <= df_subCheckerTeam['matchSeconds'][0]),
                                            ['scorePoints']].sum()['scorePoints'] - \
                df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId) &
                                    (df_scoreChecker['matchSeconds'] <= df_subCheckerTeam['matchSeconds'][0]),
                                    ['scorePoints']].sum()['scorePoints']
            lineUpData['plusMinus'].append(plusMinus)
            
            #Loop through substitutions, identify lineups and calculate data
            
            #Identify the substitutions that are grouped together
            uniqueSubs = df_subCheckerTeam['matchSeconds'].unique()
            #Loop through unique subs
            for uu in range(0,len(uniqueSubs)):
    
                #Get substitutions for current time point
                #Only take the ones that shift into a lineup position
                df_currSubs = df_subCheckerTeam.loc[(df_subCheckerTeam['matchSeconds'] == uniqueSubs[uu]) &
                                                    (df_subCheckerTeam['toPos'] != 'S'),]
                df_currSubs.reset_index(drop=True, inplace=True)
                
                #Create a new lineup variable to edit from the previous lineup
                newLineUpId = list()
                newLineUpName = list()
                for pp in range(0,7):
                    newLineUpId.append(lineUpData['lineUpId'][len(lineUpData['lineUpId'])-1][pp])
                    newLineUpName.append(lineUpData['lineUpName'][len(lineUpData['lineUpName'])-1][pp])
                
                #Loop through substitutions and replace the lineup
                for cc in range(0,len(df_currSubs)):
                    #Check for position and replace appropriately
                    if df_currSubs['toPos'][cc] == 'GS':
                        #Replace player ID
                        newLineUpId[0] = df_currSubs['playerId'][cc]
                        #Get and replace player name
                        newPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(newLineUpId[0])]
                        newLineUpName[0] = newPlayerName
                    elif df_currSubs['toPos'][cc] == 'GA':
                        #Replace player ID
                        newLineUpId[1] = df_currSubs['playerId'][cc]
                        #Get and replace player name
                        newPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(newLineUpId[1])]
                        newLineUpName[1] = newPlayerName
                    elif df_currSubs['toPos'][cc] == 'WA':
                        #Replace player ID
                        newLineUpId[2] = df_currSubs['playerId'][cc]
                        #Get and replace player name
                        newPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(newLineUpId[2])]
                        newLineUpName[2] = newPlayerName
                    elif df_currSubs['toPos'][cc] == 'C':
                        #Replace player ID
                        newLineUpId[3] = df_currSubs['playerId'][cc]
                        #Get and replace player name
                        newPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(newLineUpId[3])]
                        newLineUpName[3] = newPlayerName
                    elif df_currSubs['toPos'][cc] == 'WD':
                        #Replace player ID
                        newLineUpId[4] = df_currSubs['playerId'][cc]
                        #Get and replace player name
                        newPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(newLineUpId[4])]
                        newLineUpName[4] = newPlayerName
                    elif df_currSubs['toPos'][cc] == 'GD':
                        #Replace player ID
                        newLineUpId[5] = df_currSubs['playerId'][cc]
                        #Get and replace player name
                        newPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(newLineUpId[5])]
                        newLineUpName[5] = newPlayerName
                    elif df_currSubs['toPos'][cc] == 'GK':
                        #Replace player ID
                        newLineUpId[6] = df_currSubs['playerId'][cc]
                        #Get and replace player name
                        newPlayerName = playerInfo['displayName'][playerInfo['playerId'].index(newLineUpId[6])]
                        newLineUpName[6] = newPlayerName
                
                #Calculate and set data in lineup structure
                #Set lineup ID and names
                lineUpData['lineUpId'].append(newLineUpId)
                lineUpData['lineUpName'].append(newLineUpName)
                lineUpData['squadId'].append(currLineUpSquadId)
                #Set match and round numbers
                lineUpData['roundNo'].append(matchInfo['roundNo'][ff])
                lineUpData['matchNo'].append(matchInfo['matchNo'][ff])
                #Set match seconds start and end to 0 and the first substitution
                lineUpData['matchSecondsStart'].append(uniqueSubs[uu]+1)
                #Match seconds end will be next sub or match end when last sub
                if uu < len(uniqueSubs)-1:
                    lineUpData['matchSecondsEnd'].append(uniqueSubs[uu+1])
                    lineUpData['durationSeconds'].append(uniqueSubs[uu+1] - uniqueSubs[uu])
                else:
                    lineUpData['matchSecondsEnd'].append(sum(matchInfo['periodSeconds'][ff]))
                    lineUpData['durationSeconds'].append(sum(matchInfo['periodSeconds'][ff]) - uniqueSubs[uu])
                #Search in score flow for less than the substitution end time
                #If last sub need to only search for greater than the seconds time
                if uu < len(uniqueSubs)-1:
                    #Set points for the lineup
                    lineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId) &
                                                                   (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1) & 
                                                                   (df_scoreChecker['matchSeconds'] <= uniqueSubs[uu+1]),
                                                                   ['scorePoints']].sum()['scorePoints'])
                    #Set points against the lineup
                    lineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId) &
                                                                   (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1) & 
                                                                   (df_scoreChecker['matchSeconds'] <= uniqueSubs[uu+1]),
                                                                   ['scorePoints']].sum()['scorePoints'])
                    #Calculate plus/minus
                    plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId) &
                                                    (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1) & 
                                                    (df_scoreChecker['matchSeconds'] <= uniqueSubs[uu+1]),
                                                    ['scorePoints']].sum()['scorePoints'] - \
                        df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId) &
                                            (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1) & 
                                            (df_scoreChecker['matchSeconds'] <= uniqueSubs[uu+1]),
                                            ['scorePoints']].sum()['scorePoints']
                    lineUpData['plusMinus'].append(plusMinus)
                else:
                    #Set points for the lineup
                    lineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == lineUpSquadId1) &
                                                                   (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1),
                                                                   ['scorePoints']].sum()['scorePoints'])
                    #Set points against the lineup
                    lineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != lineUpSquadId1) &
                                                                   (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1),
                                                                   ['scorePoints']].sum()['scorePoints'])
                    #Calculate plus/minus
                    plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == lineUpSquadId1) &
                                                    (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1),
                                                    ['scorePoints']].sum()['scorePoints'] - \
                        df_scoreChecker.loc[(df_scoreChecker['squadId'] != lineUpSquadId1) &
                                            (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1),
                                            ['scorePoints']].sum()['scorePoints']
                    lineUpData['plusMinus'].append(plusMinus)
                    
    #Extract individual player 'lineup' data
    #Loop through two teams
    for nn in range(0,2):
        
        #Set current squad details within loop
        if nn == 0:
            currStartIndSquad = startIndSquad1
            if currStartIndSquad < startIndSquad2:
                currEndIndSquad = startIndSquad2
            else:
                currEndIndSquad = [len(data['playerInfo']['player'])]                
        else:
            currStartIndSquad = startIndSquad2
            if currStartIndSquad < startIndSquad1:
                currEndIndSquad = startIndSquad1
            else:
                currEndIndSquad = [len(data['playerInfo']['player'])]    
    
        #Start with first squad players
        for pp in range(currStartIndSquad[0],currEndIndSquad[0]):
            
            #Extract current player info
            currPlayerId = data['playerInfo']['player'][pp]['playerId'][0]
            currPlayerName = data['playerInfo']['player'][pp]['displayName'][0]
            currPlayerSquadId = playerInfo['squadId'][playerInfo['playerId'].index(currPlayerId)]
            
            #Check if player is in starting lineup
            if pp <= (currStartIndSquad[0] + 6):
                isStarter = True
            else:
                isStarter = False
            
            #Grab the substitution data that contains this players id
            df_subCheckerPlayer = df_subChecker.loc[(df_subChecker['playerId'] == currPlayerId),]
            df_subCheckerPlayer.reset_index(drop=True, inplace=True)
            
            #Check combinations of starter vs. no starter and number of subs
            if len(df_subCheckerPlayer) == 0:
                
                #If the player started the game and had no subs, they played the whole game
                #If they didn't then we won't add them as they didn't play
                if isStarter:
                
                    #Player started and played the whole game
                    #Set player/squad ID and names
                    individualLineUpData['playerId'].append(currPlayerId)
                    individualLineUpData['playerName'].append(currPlayerName)
                    individualLineUpData['playerPosition'].append(starterPositions[pp - currStartIndSquad[0]])
                    individualLineUpData['squadId'].append(currPlayerSquadId)
                    #Set match and round numbers
                    individualLineUpData['roundNo'].append(matchInfo['roundNo'][ff])
                    individualLineUpData['matchNo'].append(matchInfo['matchNo'][ff])
                    #Set match seconds start and end to 0 and match length
                    individualLineUpData['matchSecondsStart'].append(0)
                    individualLineUpData['matchSecondsEnd'].append(sum(matchInfo['periodSeconds'][ff]))
                    individualLineUpData['durationSeconds'].append(sum(matchInfo['periodSeconds'][ff]))
                    #Set points for the lineup
                    #Simply across the whole match
                    individualLineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId),
                                                                       ['scorePoints']].sum()['scorePoints'])
                    #Set points against the lineup
                    #Simply across the whole match
                    individualLineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId),
                                                                           ['scorePoints']].sum()['scorePoints'])
                    #Calculate plus/minus
                    plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId),
                                                    ['scorePoints']].sum()['scorePoints'] - \
                        df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId),
                                            ['scorePoints']].sum()['scorePoints']
                    individualLineUpData['plusMinus'].append(plusMinus)
                
            else:
                
                #Player incurred some form of substitution and game time
                
                #Loop through substitutions and address accordingly
                for ss in range(0,len(df_subCheckerPlayer)+1):
                    
                    #Set player/squad ID and names
                    individualLineUpData['playerId'].append(currPlayerId)
                    individualLineUpData['playerName'].append(currPlayerName)
                    individualLineUpData['squadId'].append(currPlayerSquadId)
                    #Set match and round numbers
                    individualLineUpData['roundNo'].append(matchInfo['roundNo'][ff])
                    individualLineUpData['matchNo'].append(matchInfo['matchNo'][ff])
                    
                    #Check substitution number and code accordingly
                    if ss == 0:
                        #Starters first substitution involvement                    
                        #Set starting position
                        if isStarter:
                            individualLineUpData['playerPosition'].append(starterPositions[pp - currStartIndSquad[0]])
                        else:
                            individualLineUpData['playerPosition'].append('S')                        
                        #Set match start, end and duration
                        individualLineUpData['matchSecondsStart'].append(0)
                        individualLineUpData['durationSeconds'].append(df_subCheckerPlayer['matchSeconds'][ss])
                        individualLineUpData['matchSecondsEnd'].append(df_subCheckerPlayer['matchSeconds'][ss])
                        #Set points for and against the lineup
                        individualLineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId) &
                                                                                     (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                                                     ['scorePoints']].sum()['scorePoints'])
                        individualLineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId) &
                                                                                     (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                                                     ['scorePoints']].sum()['scorePoints'])
                        #Calculate plus/minus
                        plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId) &
                                                        (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                        ['scorePoints']].sum()['scorePoints'] - \
                            df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId) &
                                                (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                ['scorePoints']].sum()['scorePoints']
                        individualLineUpData['plusMinus'].append(plusMinus)    
                        
                    elif ss == len(df_subCheckerPlayer):
                        
                        #Starters last substituion involvement
                        #Set starting position
                        individualLineUpData['playerPosition'].append(df_subCheckerPlayer['toPos'][ss-1])
                        #Set match start and duration
                        individualLineUpData['matchSecondsStart'].append(df_subCheckerPlayer['matchSeconds'][ss-1]+1)
                        individualLineUpData['durationSeconds'].append(sum(matchInfo['periodSeconds'][ff]) - df_subCheckerPlayer['matchSeconds'][ss-1]+1)
                        individualLineUpData['matchSecondsEnd'].append(sum(matchInfo['periodSeconds'][ff]))
                        #Set points for and against the lineup
                        individualLineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId) &
                                                                                     (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]) & 
                                                                                     (df_scoreChecker['matchSeconds'] <= sum(matchInfo['periodSeconds'][ff])),
                                                                                     ['scorePoints']].sum()['scorePoints'])
                        individualLineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId) &
                                                                                     (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]) & 
                                                                                     (df_scoreChecker['matchSeconds'] <= sum(matchInfo['periodSeconds'][ff])),
                                                                                     ['scorePoints']].sum()['scorePoints'])
                        #Calculate plus/minus
                        plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId) &
                                                        (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]) & 
                                                        (df_scoreChecker['matchSeconds'] <= sum(matchInfo['periodSeconds'][ff])),
                                                        ['scorePoints']].sum()['scorePoints'] - \
                            df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId) &
                                                (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]) & 
                                                (df_scoreChecker['matchSeconds'] <= sum(matchInfo['periodSeconds'][ff])),
                                                ['scorePoints']].sum()['scorePoints']
                        individualLineUpData['plusMinus'].append(plusMinus)
                        
                    else:
                        
                        #Substitutions throughout match
                        #Set substituting position
                        individualLineUpData['playerPosition'].append(df_subCheckerPlayer['toPos'][ss-1])
                        #Set match start, end and duration
                        individualLineUpData['matchSecondsStart'].append(df_subCheckerPlayer['matchSeconds'][ss-1]+1)
                        individualLineUpData['durationSeconds'].append(df_subCheckerPlayer['matchSeconds'][ss] - df_subCheckerPlayer['matchSeconds'][ss-1]+1)
                        individualLineUpData['matchSecondsEnd'].append(df_subCheckerPlayer['matchSeconds'][ss])
                        #Set points for and against the lineup
                        individualLineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId) &
                                                                                     (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]) & 
                                                                                     (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                                                     ['scorePoints']].sum()['scorePoints'])
                        individualLineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId) &
                                                                                     (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]) & 
                                                                                     (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                                                     ['scorePoints']].sum()['scorePoints'])                
                        #Calculate plus/minus
                        plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currPlayerSquadId) &
                                                        (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]+1) & 
                                                        (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                        ['scorePoints']].sum()['scorePoints'] - \
                            df_scoreChecker.loc[(df_scoreChecker['squadId'] != currPlayerSquadId) &
                                                (df_scoreChecker['matchSeconds'] > df_subCheckerPlayer['matchSeconds'][ss-1]+1) & 
                                                (df_scoreChecker['matchSeconds'] <= df_subCheckerPlayer['matchSeconds'][ss]),
                                                ['scorePoints']].sum()['scorePoints']
                        individualLineUpData['plusMinus'].append(plusMinus)
                
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

#Lineup data
df_lineUp = pd.DataFrame.from_dict(lineUpData)
df_individualLineUp = pd.DataFrame.from_dict(individualLineUpData)

##### TODO: other dataframes once extracted

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

#Total one vs. two point shots
round2Plot = 4
figHelper.totalPointsOneVsTwo(round2Plot = round2Plot, matchInfo = matchInfo,
                              teamInfo = teamInfo, df_scoreFlow = df_scoreFlow,
                              colourDict = colourDict, bokehOptions = bokehOptions,
                              showPlot = False, exportPNG = True, exportHTML = True)

#Quarter by quarter one vs. two point shots
round2Plot = 4
figHelper.quarterPointsOneVsTwo(round2Plot = round2Plot, matchInfo = matchInfo,
                                teamInfo = teamInfo, df_scoreFlow = df_scoreFlow,
                                colourDict = colourDict, bokehOptions = bokehOptions,
                                showPlot = False, exportPNG = True, exportHTML = True)

#Ratio of inner vs. outer shots in different periods
round2Plot = 4
figHelper.teamShotRatiosInnerVsOuter(round2Plot = round2Plot, matchInfo = matchInfo,
                                     teamInfo = teamInfo, df_scoreFlow = df_scoreFlow,
                                     colourDict = colourDict, bokehOptions = bokehOptions,
                                     showPlot = False, exportPNG = True, exportHTML = True)

# %% Individual player two-point scoring

#Total two-point score
round2Plot = 4
figHelper.playerTwoPointTotals(round2Plot = round2Plot, df_scoreFlow = df_scoreFlow,
                               df_playerInfo = df_playerInfo, df_teamInfo = df_teamInfo,
                               colourDict = colourDict, showPlot = False,
                               exportPNG = True, exportHTML = True)

#Differential between two and one point scoring
round2Plot = 4
figHelper.playerTwoPointDifferentials(round2Plot = round2Plot, df_scoreFlow = df_scoreFlow,
                                      df_playerInfo = df_playerInfo, df_teamInfo = df_teamInfo,
                                      colourDict = colourDict, showPlot = False,
                                      exportPNG = True, exportHTML = True)

#Relative differential for two vs. one point totals
round2Plot = 4
figHelper.playerTwoPointRelativeDifferentials(round2Plot = round2Plot, df_scoreFlow = df_scoreFlow,
                                              df_playerInfo = df_playerInfo, df_teamInfo = df_teamInfo,
                                              colourDict = colourDict, showPlot = False,
                                              exportPNG = True, exportHTML = True)

# %% Plus/minus figures

#Navigate to appropriate directory
os.chdir('..\\..\\PlusMinusAnalysis')

##### TODO: sort plus minus per figure, toolbar in second html issue?

# %% All matches team line-up plus/minus grid

#Create plot
figHelper.totalPlusMinusLineUps(teamInfo = teamInfo, df_lineUp = df_lineUp,
                                absPlusMinus = True, perPlusMinus = True,
                                perDivider = 15, minLineUpDuration = 5,
                                colourDict = colourDict, showPlot = False,
                                exportPNG = True, exportHTML = True)

# %% Super shot period score simulator

# The goal of this analysis is to understand how many shot opportunities teams
# get in the five minute super shot period, the success of standard vs. super shots 
# in this period - and from this simulate how many points teams would expect to get
# taking different proportions of standard vs. super shots

##### TODO: consider adding a factor that removes the super shot opportunity at a
##### certain probability (e.g. only 75% of super shots get a chance) --- simulates 
##### the idea that teams are getting turnovers when trying to set up...

#Set a list of proportions to examine across simulations
superShotProps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5,
                  0.6, 0.7, 0.8, 0.9, 1.0]

#Create dictionary to store data in
superSimResults = {'squadId': [], 'squadNickname': [],
                   'nShots': [], 'nStandard': [], 'nSuper': [],
                   'superProp': [], 'superPropCat': [], 'totalPts': []}

#Loop through teams
##### TODO: start with one team
currSquadId = 8117
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

#Set number of simulations
nSims = 1000

#Sample from truncated normal distribution with mean/SD parameters
nShotVals = stats.truncnorm((0 - totalShotsM) / totalShotsSD,
                            (np.inf - totalShotsM) / totalShotsSD,
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
        
        #Set total points counter for current iteration
        totalPts = 0
        
        #Get the current number of shots for the quarter
        nShots = int(nShotVals[nn])
        
        #Get the standard and super shot attempts based on proportion
        nSuper = nShots * superShotProps[pp]
        #Round to ensure a whole number
        nSuper = int(np.around(nSuper))
        #Get standard based on difference
        nStandard = int(nShots - nSuper)
        
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
        superSimResults['squadId'].append(currSquadId)
        superSimResults['squadNickname'].append(currSquadName)
        superSimResults['nShots'].append(nShots)
        superSimResults['nStandard'].append(nStandard)
        superSimResults['nSuper'].append(nSuper)
        superSimResults['superProp'].append(actualProp)
        superSimResults['superPropCat'].append(propCat)
        superSimResults['totalPts'].append(totalPts)
        


#Create test gridplot for first squad

#Convert sim dictionary to datafram
df_superSimResults = pd.DataFrame.from_dict(superSimResults)


##### Ridge plot doesn't work that well, scatter may be good

#Try boxplot
sns.boxplot(x = 'superPropCat', y = 'totalPts',
            data = df_superSimResults,
            palette = "vlag")

# # Add in points to show each observation
# sns.swarmplot(x="distance", y="method", data=planets,
#               size=2, color=".3", linewidth=0)

##### The large variation might be due to the potentially wide ranging
##### beta distributions...?

##### The strip-plot seaborn example with different colours might work well to distribute
##### different scores

##### Ridge plot probably doesn't work well with such integer based data...

# %%



 
# %% Plot player plus/minus

####### UP TO HERE

#Get unique list of players from the lineup dataframe
plotPlayers = list(df_individualLineUp['playerId'].unique())

#Loop through players and extract total plus minus data
#Set blank lists to store data in
playerDuration = list()
playerPlusMinus = list()
playerPlusMinusPer15 = list()
analysePlayer = list()
analyseColour = list()
analyseSquad = list()
for pp in range(0,len(plotPlayers)):
    
    #Extract current player to dataframe
    df_currPlayer = df_individualLineUp.loc[(df_individualLineUp['playerId'] == plotPlayers[pp]) &
                                            (df_individualLineUp['playerPosition'] != 'S'),
                                            ['playerId','durationSeconds','plusMinus']]
    df_currPlayer.reset_index(drop=True, inplace=True)
    
    #Check if player total is greater than 5 minutes and get data if so
    if sum(df_currPlayer['durationSeconds']) > 300:
        #Append duration and plus/minus
        playerDuration.append(sum(df_currPlayer['durationSeconds'])/60)
        playerPlusMinus.append(sum(df_currPlayer['plusMinus']))
        #Calculate per 15 plus minus
        perDivider = 15
        perFac = perDivider / (sum(df_currPlayer['durationSeconds']/60))
        playerPlusMinusPer15.append(sum(df_currPlayer['plusMinus'])*perFac)
        #Get current player and append
        analysePlayer.append(playerInfo['displayName'][playerInfo['playerId'].index(plotPlayers[pp])])
        #Get squad ID colour for player
        currSquadId = playerInfo['squadId'][playerInfo['playerId'].index(plotPlayers[pp])]
        analyseColour.append(colourDict[teamInfo['squadNickname'][teamInfo['squadId'].index(currSquadId)]])
        analyseSquad.append(teamInfo['squadNickname'][teamInfo['squadId'].index(currSquadId)])
        
        
        
#Place player plus minus data in dataframe and sort
df_playerPlusMinus = pd.DataFrame(list(zip(analysePlayer,analyseColour,analyseSquad,
                                           playerDuration,playerPlusMinus,playerPlusMinusPer15)),
                                  columns = ['analysePlayer','analyseColour','analyseSquad',
                                             'playerDuration','playerPlusMinus','playerPlusMinusPer15'])
df_playerPlusMinus.sort_values(by = 'playerPlusMinus', inplace = True,
                               ascending = False, ignore_index = True)
 
#Create figure for total player plus minus (top 20 players)
figPlot = list()
figSource = list()

#Create source for figure
figSource.append(ColumnDataSource(data = dict(players = list(df_playerPlusMinus['analysePlayer'].iloc[0:20]),
                                              counts = list(df_playerPlusMinus['playerPlusMinus'].iloc[0:20]),
                                              duration = list(df_playerPlusMinus['playerDuration'].iloc[0:20]),
                                              squad = list(df_playerPlusMinus['analyseSquad'].iloc[0:20]),
                                              colours = tuple(df_playerPlusMinus['analyseColour'].iloc[0:20]))))

#Create figure
figPlot.append(figure(x_range = list(df_playerPlusMinus['analysePlayer'].iloc[0:20]), plot_height = 400, plot_width = 800,
                      title = 'Top 20 Players for Total Plus/Minus (min. 5 minutes played)',
                      toolbar_location = None,
                      tools = 'hover', 
                      tooltips = [("Player", "@players"), ("Team", "@squad"), ("Total Minutes", "@duration"), ("Player Total Plus/Minus", "@counts")]))

#Add bars
figPlot[0].vbar(x = 'players', top = 'counts', width=0.6,
                color = 'colours', source = figSource[0])

#Set figure parameters
figPlot[0].y_range.start = 0
figPlot[0].x_range.range_padding = 0.1
figPlot[0].xaxis.major_label_orientation = 1
figPlot[0].xgrid.grid_line_color = None
figPlot[0].title.align = 'center'
figPlot[0].yaxis.axis_label = 'Total Plus/Minus'

# #Show figure
# show(figPlot[0])

#Export figure as PNG and HTML

#Seems like storing html in same folder causes figures to overwrite?
#Make directory to store
os.mkdir('total-absolutePlusMinus-players')
os.chdir('total-absolutePlusMinus-players')

#PNG
export_png(figPlot[0], filename = 'total-absolutePlusMinus-players.png')

#HTML
output_file('total-absolutePlusMinus-players.html')
save(figPlot[0])

#Navigate back up
os.chdir('..') 

# %% Plot player plus/minus per 15

#Resort player plus minus by per 15
df_playerPlusMinus.sort_values(by = 'playerPlusMinusPer15', inplace = True,
                               ascending = False, ignore_index = True)
 
#Create figure for total player plus minus (top 20 players)
figPlot = list()
figSource = list()

#Create source for figure
figSource.append(ColumnDataSource(data = dict(players = list(df_playerPlusMinus['analysePlayer'].iloc[0:20]),
                                              counts = list(df_playerPlusMinus['playerPlusMinusPer15'].iloc[0:20]),
                                              duration = list(df_playerPlusMinus['playerDuration'].iloc[0:20]),
                                              squad = list(df_playerPlusMinus['analyseSquad'].iloc[0:20]),
                                              colours = tuple(df_playerPlusMinus['analyseColour'].iloc[0:20]))))

#Create figure
figPlot.append(figure(x_range = list(df_playerPlusMinus['analysePlayer'].iloc[0:20]), plot_height = 400, plot_width = 800,
                      title = 'Top 20 Players for Total Plus/Minus Per 15 Minutes (min. 5 minutes played)',
                      toolbar_location = None,
                      tools = 'hover', 
                      tooltips = [("Player", "@players"), ("Team", "@squad"), ("Total Minutes", "@duration"), ("Player Total Plus/Minus Per 15", "@counts")]))

#Add bars
figPlot[0].vbar(x = 'players', top = 'counts', width=0.6,
                color = 'colours', source = figSource[0])

#Set figure parameters
figPlot[0].y_range.start = 0
figPlot[0].x_range.range_padding = 0.1
figPlot[0].xaxis.major_label_orientation = 1
figPlot[0].xgrid.grid_line_color = None
figPlot[0].title.align = 'center'
figPlot[0].yaxis.axis_label = 'Total Plus/Minus Per 15 Minutes Played'

# #Show figure
# show(figPlot[0])

#Export figure as PNG and HTML

#Seems like storing html in same folder causes figures to overwrite?
#Make directory to store
os.mkdir('total-per15PlusMinus-players')
os.chdir('total-per15PlusMinus-players')

#PNG
export_png(figPlot[0], filename = 'total-per15PlusMinus-players.png')

#HTML
output_file('total-per15PlusMinus-players.html')
save(figPlot[0])

#Navigate back up
os.chdir('..') 

# %% Plot differential between plus/minus when player on/off

#Loop through players and extract total plus minus data
#Set blank lists to store data in
playerDurationOn = list()
playerDurationOff = list()
playerPlusMinusOn = list()
playerPlusMinusOff = list()
playerPlusMinusOnPer15 = list()
playerPlusMinusOffPer15 = list()
analysePlayer = list()
analyseColour = list()
analyseSquad = list()
for pp in range(0,len(plotPlayers)):
    
    #Extract current player to dataframe for on and off
    df_currPlayerOn = df_individualLineUp.loc[(df_individualLineUp['playerId'] == plotPlayers[pp]) &
                                              (df_individualLineUp['playerPosition'] != 'S'),
                                              ['playerId','durationSeconds','plusMinus']]
    df_currPlayerOn.reset_index(drop=True, inplace=True)
    df_currPlayerOff = df_individualLineUp.loc[(df_individualLineUp['playerId'] == plotPlayers[pp]) &
                                               (df_individualLineUp['playerPosition'] == 'S'),
                                               ['playerId','durationSeconds','plusMinus']]
    df_currPlayerOff.reset_index(drop=True, inplace=True)
    
    #Check if player total is greater than 5 minutes and get data if so
    if sum(df_currPlayerOn['durationSeconds']) > 300 and sum(df_currPlayerOff['durationSeconds']) > 300:
        #Append duration and plus/minus when on vs. off
        playerDurationOn.append(sum(df_currPlayerOn['durationSeconds'])/60)
        playerPlusMinusOn.append(sum(df_currPlayerOn['plusMinus']))
        playerDurationOff.append(sum(df_currPlayerOff['durationSeconds'])/60)
        playerPlusMinusOff.append(sum(df_currPlayerOff['plusMinus']))
        #Calculate per 15 plus minus
        perDivider = 15
        #On
        perFac = perDivider / (sum(df_currPlayerOn['durationSeconds']/60))
        playerPlusMinusOnPer15.append(sum(df_currPlayerOn['plusMinus'])*perFac)
        #Off
        perFac = perDivider / (sum(df_currPlayerOff['durationSeconds']/60))
        playerPlusMinusOffPer15.append(sum(df_currPlayerOff['plusMinus'])*perFac)
        #Get current player and append
        analysePlayer.append(playerInfo['displayName'][playerInfo['playerId'].index(plotPlayers[pp])])
        #Get squad ID colour for player
        currSquadId = playerInfo['squadId'][playerInfo['playerId'].index(plotPlayers[pp])]
        analyseColour.append(colourDict[teamInfo['squadNickname'][teamInfo['squadId'].index(currSquadId)]])
        analyseSquad.append(teamInfo['squadNickname'][teamInfo['squadId'].index(currSquadId)])
        
        
        
#Place player plus minus data in dataframe and sort
df_playerPlusMinusRel = pd.DataFrame(list(zip(analysePlayer,analyseColour,analyseSquad,
                                              playerDurationOn,playerPlusMinusOn,playerPlusMinusOnPer15,
                                              playerDurationOff,playerPlusMinusOff,playerPlusMinusOffPer15)),
                                     columns = ['analysePlayer','analyseColour','analyseSquad',
                                                'playerDurationOn','playerPlusMinusOn','playerPlusMinusOnPer15',
                                                'playerDurationOff','playerPlusMinusOff','playerPlusMinusOffPer15'])

#Calculate the relative difference between when the player is off vs. on
#This calculation means positive and negative values mean the team does better
#versus worse when the player is on, respectively
relPerformance = list()
relPerformancePer15 = list()
for dd in range(0,len(df_playerPlusMinusRel)):
    relPerformance.append(df_playerPlusMinusRel['playerPlusMinusOn'][dd] - df_playerPlusMinusRel['playerPlusMinusOff'][dd])
    relPerformancePer15.append(df_playerPlusMinusRel['playerPlusMinusOnPer15'][dd] - df_playerPlusMinusRel['playerPlusMinusOffPer15'][dd])
#Append to dataframe
df_playerPlusMinusRel['relPerformance'] = relPerformance
df_playerPlusMinusRel['relPerformancePer15'] = relPerformancePer15
#Resort by relative per 15 performance
df_playerPlusMinusRel.sort_values(by = 'relPerformancePer15', inplace = True,
                                  ascending = False, ignore_index = True)
 
#Create figure for total player plus minus (top 20 players)
figPlot = list()
figSource = list()

#Create source for figure
figSource.append(ColumnDataSource(data = dict(players = list(df_playerPlusMinusRel['analysePlayer'].iloc[0:20]),
                                              counts = list(df_playerPlusMinusRel['relPerformancePer15'].iloc[0:20]),
                                              durationOn = list(df_playerPlusMinusRel['playerDurationOn'].iloc[0:20]),
                                              durationOff = list(df_playerPlusMinusRel['playerDurationOff'].iloc[0:20]),
                                              squad = list(df_playerPlusMinusRel['analyseSquad'].iloc[0:20]),
                                              colours = tuple(df_playerPlusMinusRel['analyseColour'].iloc[0:20]))))

#Create figure
figPlot.append(figure(x_range = list(df_playerPlusMinusRel['analysePlayer'].iloc[0:20]), plot_height = 400, plot_width = 800,
                      title = 'Top 20 Players for Plus/Minus per 15 Minute when On vs. Off Court (min. 5 minutes on & off court)',
                      toolbar_location = None,
                      tools = 'hover', 
                      tooltips = [("Player", "@players"), ("Team", "@squad"), ("Minutes On-Court", "@durationOn"), ("Minutes Off-Court", "@durationOff"), ("Relative Plus/Minus per 15 Minutes", "@counts")]))

#Add bars
figPlot[0].vbar(x = 'players', top = 'counts', width=0.6,
                color = 'colours', source = figSource[0])

#Set figure parameters
figPlot[0].y_range.start = 0
figPlot[0].x_range.range_padding = 0.1
figPlot[0].xaxis.major_label_orientation = 1
figPlot[0].xgrid.grid_line_color = None
figPlot[0].title.align = 'center'
figPlot[0].yaxis.axis_label = 'Relative Plus/Minus per 15 Minutes'

# #Show figure
# show(figPlot[0])

#Export figure as PNG and HTML

#Seems like storing html in same folder causes figures to overwrite?
#Make directory to store
os.mkdir('total-relativePer15PlusMinus-players')
os.chdir('total-relativePer15PlusMinus-players')

#PNG
export_png(figPlot[0], filename = 'total-relativePer15PlusMinus-players.png')

#HTML
output_file('total-relativePer15PlusMinus-players.html')
save(figPlot[0])

#Navigate back up
os.chdir('..') 

# %%
