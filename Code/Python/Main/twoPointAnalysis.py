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

TODO: convert script for round to round analysis & mean data
    
TODO: convert plot data generation to separate functions with inputs

TODO: this script is expanding outside of just two point analysis (e.g. subs & +/-)

"""

# %% Import packages

import pandas as pd
pd.options.mode.chained_assignment = None #turn of pandas chained warnings
import os
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import gridplot
from bokeh.models import FactorRange, ColumnDataSource, Legend, HoverTool
from bokeh.transform import factor_cmap
from bokeh.io import show
from bokeh.io import export_png
import json

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
    
# %%

# %% Test plots from round 1

##### TODO: wrap each of these in function that takes round input etc.

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

# %% Team-based data

# %% Total one vs. two point shots

#See for sample: https://nbviewer.jupyter.org/github/bokeh/bokeh-notebooks/blob/master/tutorial/07%20-%20Bar%20and%20Categorical%20Data%20Plots.ipynb

#Loop through the four games from round 1
##### TODO: This won't work for matches above round 1

#Set blank lists to fill with plots and source
figPlot = list()
figSource = list()

#Enter round
##### TODO: create function with round as input
round2Plot = 2

#Run loop to create plots
for gg in range(0,4):
    
    #Get team ID's for this match
    teamId1 = matchInfo['homeSquadId'][((round2Plot-1)*4)+gg]
    teamId2 = matchInfo['awaySquadId'][((round2Plot-1)*4)+gg]
   
    #Get team names for these ID's
    teamInd1 = [i for i,x in enumerate(teamInfo['squadId']) if x == teamId1]
    teamName1 = teamInfo['squadNickname'][teamInd1[0]]
    teamInd2 = [i for i,x in enumerate(teamInfo['squadId']) if x == teamId2]
    teamName2 = teamInfo['squadNickname'][teamInd2[0]]
    
    #Get match result for title
    team1Score = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                  (df_scoreFlow['scoreName'] == 'goal') & 
                                  (df_scoreFlow['squadId'] == teamId1),
                                  ['scorePoints']].sum()[0] + \
        df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                         (df_scoreFlow['scoreName'] == '2pt Goal') & 
                         (df_scoreFlow['squadId'] == teamId1),
                         ['scorePoints']].sum()[0]
    team2Score = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                  (df_scoreFlow['scoreName'] == 'goal') & 
                                  (df_scoreFlow['squadId'] == teamId2),
                                  ['scorePoints']].sum()[0] + \
        df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                         (df_scoreFlow['scoreName'] == '2pt Goal') & 
                         (df_scoreFlow['squadId'] == teamId2),
                         ['scorePoints']].sum()[0]
    
    #Set colour palette based on team names
    palette = tuple([colourDict[teamName1],
                     colourDict[teamName2]])
    
    #Set up categorical variables for current game
    goalTypes = ['Standard Shots', 'Super Shots']
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
                          title = teamName1+' ('+str(team1Score)+') vs. '+teamName2+' ('+str(team2Score)+')',
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

# #Show grid
# show(grid)

#Export grid as both .png and .html

#Navigate to relevant figure directory
##### TODO: better navigation set
os.chdir('..\\..\\Figures\\TwoPointAnalysis\\RoundByRound')

##### TODO: set better naming strings for figures with looping

#Seems like storing html in same folder causes figures to overwrite?
#Make directory to store
os.mkdir('round'+str(round2Plot)+'-totalteampoints-onevstwo')
os.chdir('round'+str(round2Plot)+'-totalteampoints-onevstwo')

#PNG
export_png(grid, filename = 'round'+str(round2Plot)+'-totalteampoints-onevstwo.png')

#HTML
output_file('round'+str(round2Plot)+'-totalteampoints-onevstwo.html')
save(grid)

#Navigate back up
os.chdir('..')

##### TODO: figure out effective method to copy to github pages?

# %% Quarter by quarter one vs. two point shots

#Loop through the four games from round 1
##### TODO: This won't work for matches above round 1

#Enter round
##### TODO: create function with round as input
round2Plot = 2

#Set blank lists to fill with plots and source
figPlot = list()
figSource = list()

#Run loop to create plots
for gg in range(0,4):
    
    #Get team ID's for this match
    teamId1 = matchInfo['homeSquadId'][((round2Plot-1)*4)+gg]
    teamId2 = matchInfo['awaySquadId'][((round2Plot-1)*4)+gg]
    
    #Get team names for these ID's
    teamInd1 = [i for i,x in enumerate(teamInfo['squadId']) if x == teamId1]
    teamName1 = teamInfo['squadNickname'][teamInd1[0]]
    teamInd2 = [i for i,x in enumerate(teamInfo['squadId']) if x == teamId2]
    teamName2 = teamInfo['squadNickname'][teamInd2[0]]
    
    #Get match result for title
    team1Score = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                  (df_scoreFlow['scoreName'] == 'goal') & 
                                  (df_scoreFlow['squadId'] == teamId1),
                                  ['scorePoints']].sum()[0] + \
        df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                         (df_scoreFlow['scoreName'] == '2pt Goal') & 
                         (df_scoreFlow['squadId'] == teamId1),
                         ['scorePoints']].sum()[0]
    team2Score = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                  (df_scoreFlow['scoreName'] == 'goal') & 
                                  (df_scoreFlow['squadId'] == teamId2),
                                  ['scorePoints']].sum()[0] + \
        df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                         (df_scoreFlow['scoreName'] == '2pt Goal') & 
                         (df_scoreFlow['squadId'] == teamId2),
                         ['scorePoints']].sum()[0]
    
    #Set colour palette based on team names
    palette = tuple([colourDict[teamName1],
                      colourDict[teamName2]])
    
    #Set teams for factors
    teams = [teamName1, teamName2]
    
    #Set up factors
    factors = [
        ('Standard Shots',teamName1),('Super Shots',teamName1),
        ('Standard Shots',teamName2),('Super Shots',teamName2),
        ]
    
    #Set up quarter list
    quarters = ['Q1','Q2','Q3','Q4']
    
    #Extract total points scored by the two teams in each category & quarter
    
    #Team 1
    standardTeam1 = list()
    twoPointTeam1 = list()
    for qq in range(0,4):
        standardTeam1.append(df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                              (df_scoreFlow['scoreName'] == 'goal') & 
                                              (df_scoreFlow['squadId'] == teamId1) & 
                                              (df_scoreFlow['period'] == qq+1),
                                              ['scorePoints']].sum()[0])
        twoPointTeam1.append(df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                              (df_scoreFlow['scoreName'] == '2pt Goal') & 
                                              (df_scoreFlow['squadId'] == teamId1) & 
                                              (df_scoreFlow['period'] == qq+1),
                                              ['scorePoints']].sum()[0])
        
    #Team 2
    standardTeam2 = list()
    twoPointTeam2 = list()
    for qq in range(0,4):
        standardTeam2.append(df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                              (df_scoreFlow['scoreName'] == 'goal') & 
                                              (df_scoreFlow['squadId'] == teamId2) & 
                                              (df_scoreFlow['period'] == qq+1),
                                              ['scorePoints']].sum()[0])
        twoPointTeam2.append(df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                              (df_scoreFlow['scoreName'] == '2pt Goal') & 
                                              (df_scoreFlow['squadId'] == teamId2) & 
                                              (df_scoreFlow['period'] == qq+1),
                                              ['scorePoints']].sum()[0])
     
    #Set up data source
    figSource.append(ColumnDataSource(data = dict(
        x = factors,
        Q1 = [standardTeam1[0],twoPointTeam1[0],standardTeam2[0],twoPointTeam2[0]],
        Q2 = [standardTeam1[1],twoPointTeam1[1],standardTeam2[1],twoPointTeam2[1]],
        Q3 = [standardTeam1[2],twoPointTeam1[2],standardTeam2[2],twoPointTeam2[2]],
        Q4 = [standardTeam1[3],twoPointTeam1[3],standardTeam2[3],twoPointTeam2[3]],
        )))
    
    #Create figure
    figPlot.append(figure(x_range = FactorRange(*factors),
                          plot_height = 400, plot_width = 500,
                          title = teamName1+' ('+str(team1Score)+') vs. '+teamName2+' ('+str(team2Score)+')',
                          toolbar_location = None,
                          tools = 'hover', 
                          tooltips = [("Category", "@x"),("Quarter", "$name"),("Points Scored", "@$name")]))
    
    #Add the vbar stack
    f = figPlot[gg].vbar_stack(quarters, x = 'x', width = 1.0,
                               #color = ["blue", "red", "green", "yellow"],
                               fill_color = 'white', #white setting for hatches;#factor_cmap('x', palette = palette, factors = teams, start = 1, end = 2),
                               line_color = factor_cmap('x', palette = palette, factors = teams, start = 1, end = 2),
                               hatch_pattern = ['/','/','blank','\\'], #scale setting for the / is a hack to get solid
                               hatch_color = factor_cmap('x', palette = palette, factors = teams, start = 1, end = 2),
                               hatch_scale = [1.0,10,10,10],
                               #legend_label = quarters,
                               source = figSource[gg])
    
    #Add legend
    legend = Legend(items = [(x,[f[i]]) for i,x in enumerate(quarters)], location=(10, 0))
    figPlot[gg].add_layout(legend,'right')
    
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
                plot_width = 400, plot_height = 350)

# #Show grid
# show(grid)

#Export grid as both .png and .html

##### TODO: set better naming strings for figures with looping

#Seems like storing html in same folder causes figures to overwrite?
#Make directory to store
os.mkdir('round'+str(round2Plot)+'-quarterteampoints-onevstwo')
os.chdir('round'+str(round2Plot)+'-quarterteampoints-onevstwo')

#PNG
export_png(grid, filename = 'round'+str(round2Plot)+'-quarterteampoints-onevstwo.png')

#HTML
output_file('round'+str(round2Plot)+'-quarterteampoints-onevstwo.html')
save(grid)

#Navigate back up
os.chdir('..')

##### TODO: figure out effective method to copy to github pages?

# %% Ratio of inner vs. outer shots in different periods

#Enter round
##### TODO: create function with round as input
round2Plot = 2

#Set blank lists to fill with plots and source
figPlot = list()
figSource = list()

#Run loop to create plots
for gg in range(0,4):
    
    #Get team ID's for this match
    teamId1 = matchInfo['homeSquadId'][((round2Plot-1)*4)+gg]
    teamId2 = matchInfo['awaySquadId'][((round2Plot-1)*4)+gg]
    
    #Get team names for these ID's
    teamInd1 = [i for i,x in enumerate(teamInfo['squadId']) if x == teamId1]
    teamName1 = teamInfo['squadNickname'][teamInd1[0]]
    teamInd2 = [i for i,x in enumerate(teamInfo['squadId']) if x == teamId2]
    teamName2 = teamInfo['squadNickname'][teamInd2[0]]
    
    #Get match result for title
    team1Score = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                  (df_scoreFlow['scoreName'] == 'goal') & 
                                  (df_scoreFlow['squadId'] == teamId1),
                                  ['scorePoints']].sum()[0] + \
        df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                         (df_scoreFlow['scoreName'] == '2pt Goal') & 
                         (df_scoreFlow['squadId'] == teamId1),
                         ['scorePoints']].sum()[0]
    team2Score = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                  (df_scoreFlow['scoreName'] == 'goal') & 
                                  (df_scoreFlow['squadId'] == teamId2),
                                  ['scorePoints']].sum()[0] + \
        df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                         (df_scoreFlow['scoreName'] == '2pt Goal') & 
                         (df_scoreFlow['squadId'] == teamId2),
                         ['scorePoints']].sum()[0]
    
    #Set colour palette based on team names
    palette = tuple([colourDict[teamName1],
                      colourDict[teamName2]])
    
    #Set teams for factors
    teams = [teamName1, teamName2]
    
    #Set up factors
    factors = [
        ('Standard Period',teamName1),('Super Shot Period',teamName1),
        ('Standard Period',teamName2),('Super Shot Period',teamName2),
        ]
    
    #Set up circle and ratios list
    circle = ['Inner Circle','Outer Circle']
    ratios = ['standard', 'twoPoint']
    
    #Extract total points scored by the two teams in each category & quarter
    
    #Extract ratio of shots in inner vs. outer circle in the different periods
    
    #Team 1
    innerTeam1 = list()
    outerTeam1 = list()
    for qq in range(0,len(ratios)):
        innerTeam1.append(df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                           (df_scoreFlow['squadId'] == teamId1) & 
                                           (df_scoreFlow['periodCategory'] == ratios[qq]) &
                                           (df_scoreFlow['shotCircle'] == 'innerCircle'),
                                           ['shotCircle']].count()[0])
        outerTeam1.append(df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                           (df_scoreFlow['squadId'] == teamId1) & 
                                           (df_scoreFlow['periodCategory'] == ratios[qq]) &
                                           (df_scoreFlow['shotCircle'] == 'outerCircle'),
                                           ['shotCircle']].count()[0])
    
    #Normalise team 1 data to a ratio
    innerTeam1Ratio = list()
    innerTeam1Ratio.append(innerTeam1[0] / (innerTeam1[0]+outerTeam1[0]))
    innerTeam1Ratio.append(innerTeam1[1] / (innerTeam1[1]+outerTeam1[1]))
    outerTeam1Ratio = list()
    outerTeam1Ratio.append(outerTeam1[0] / (innerTeam1[0]+outerTeam1[0]))
    outerTeam1Ratio.append(outerTeam1[1] / (innerTeam1[1]+outerTeam1[1]))
        
    #Team 2
    innerTeam2 = list()
    outerTeam2 = list()
    for qq in range(0,len(ratios)):
        innerTeam2.append(df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                           (df_scoreFlow['squadId'] == teamId2) & 
                                           (df_scoreFlow['periodCategory'] == ratios[qq]) &
                                           (df_scoreFlow['shotCircle'] == 'innerCircle'),
                                           ['shotCircle']].count()[0])
        outerTeam2.append(df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                           (df_scoreFlow['squadId'] == teamId2) & 
                                           (df_scoreFlow['periodCategory'] == ratios[qq]) &
                                           (df_scoreFlow['shotCircle'] == 'outerCircle'),
                                           ['shotCircle']].count()[0])
    
    #Normalise team 2 data to a ratio
    innerTeam2Ratio = list()
    innerTeam2Ratio.append(innerTeam2[0] / (innerTeam2[0]+outerTeam2[0]))
    innerTeam2Ratio.append(innerTeam2[1] / (innerTeam2[1]+outerTeam2[1]))
    outerTeam2Ratio = list()
    outerTeam2Ratio.append(outerTeam2[0] / (innerTeam2[0]+outerTeam2[0]))
    outerTeam2Ratio.append(outerTeam2[1] / (innerTeam2[1]+outerTeam2[1]))
     
    #Set up data source
    figSource.append(ColumnDataSource(data = dict(
        x = factors,
        standard = [innerTeam1Ratio[0],innerTeam1Ratio[1],innerTeam2Ratio[0],innerTeam2Ratio[1]],
        twoPoint = [outerTeam1Ratio[0],outerTeam1Ratio[1],outerTeam2Ratio[0],outerTeam2Ratio[1]],
        )))
    
    #Create figure
    figPlot.append(figure(x_range = FactorRange(*factors),
                          plot_height = 450, plot_width = 500,
                          title = teamName1+' ('+str(team1Score)+') vs. '+teamName2+' ('+str(team2Score)+')',
                          toolbar_location = None,
                          tools = 'hover', 
                          tooltips = [("Category", "@x"),("Shot Ratio", "@$name")]))
    
    #Add the vbar stack
    f = figPlot[gg].vbar_stack(ratios, x = 'x', width = 1.0,
                               fill_color = 'white', #white setting for hatches;#factor_cmap('x', palette = palette, factors = teams, start = 1, end = 2),
                               line_color = factor_cmap('x', palette = palette, factors = teams, start = 1, end = 2),
                               hatch_pattern = ['/','blank'], #scale setting for the / is a hack to get solid
                               hatch_color = factor_cmap('x', palette = palette, factors = teams, start = 1, end = 2),
                               hatch_scale = [1,10],
                               source = figSource[gg])
    
    #Add legend
    legend = Legend(items = [(x,[f[i]]) for i,x in enumerate(circle)], location=(10, 0))
    figPlot[gg].add_layout(legend,'right')
    
    #Set figure parameters
    figPlot[gg].y_range.start = 0
    figPlot[gg].x_range.range_padding = 0.1
    figPlot[gg].xaxis.major_label_orientation = 1
    figPlot[gg].xgrid.grid_line_color = None
    figPlot[gg].title.align = 'center'
    figPlot[gg].yaxis.axis_label = 'Ratio of Shots'
    
    # #Show figure
    # show(figPlot[gg])
 
#Create the gridplot
grid = gridplot([[figPlot[0], figPlot[1]],
                 [figPlot[2], figPlot[3]]],
                plot_width = 450, plot_height = 350)

# #Show grid
# show(grid)

#Export grid as both .png and .html

##### TODO: set better naming strings for figures with looping

#Seems like storing html in same folder causes figures to overwrite?
#Make directory to store
os.mkdir('round'+str(round2Plot)+'-teamshotratios-innervsouter')
os.chdir('round'+str(round2Plot)+'-teamshotratios-innervsouter')

#PNG
export_png(grid, filename = 'round'+str(round2Plot)+'-teamshotratios-innervsouter.png')

#HTML
output_file('round'+str(round2Plot)+'-teamshotratios-innervsouter.html')
save(grid)

#Navigate back up
os.chdir('..')

# %% Individual player two-point scoring

#Create list to stash 2pt figures
figPlot_2ptPlayerScoring = list()
figSource_2ptPlayerScoring = list()

#Setting for current figure index
ind_2ptPlayerScoring = 0

# %% Total two-point score

#Enter round
##### TODO: create function with round as input
round2Plot = 2

#Extract a dataframe of 2pt Goals
df_2ptGoal = df_scoreFlow.loc[(df_scoreFlow['scoreName'] == '2pt Goal') &
                              (df_scoreFlow['roundNo'] == round2Plot),]

#Get the unique list of players who scored two-point goals
playerList_2ptGoal = list(df_2ptGoal['playerId'].unique())

#Loop through and sum the total two point value for each player
playerList_2ptTotal = list()
for pp in range(0,len(playerList_2ptGoal)):
    #Calculate and append total 2 point score
    playerList_2ptTotal.append(df_2ptGoal.loc[(df_2ptGoal['playerId'] == playerList_2ptGoal[pp]),
                                              ['scorePoints']].sum()[0])
    
#Convert to dataframe and sort
df_2ptTotals = pd.DataFrame(list(zip(playerList_2ptGoal,playerList_2ptTotal)),
                            columns = ['playerId','2ptTotal'])
df_2ptTotals.sort_values(by = '2ptTotal', inplace = True,
                         ascending = False, ignore_index = True)

#Create bar plot for two point totals
#Create lists to store the data in
players = list()
fullNames = list()
squadNames = list()
totals = list()
twoPointTotalsPalette = list()
#Loop through the player list and collate the data needed for the plot
for pp in range(0,len(df_2ptTotals)):
    #Get the ID of the current player
    currId = df_2ptTotals.iloc[pp]['playerId']
    #Get the dataframe ID of the current player
    currInd = df_playerInfo.index[df_playerInfo['playerId'] == currId].tolist()[0]
    #Get the current player details
    players.append(df_playerInfo.iloc[currInd]['displayName'])
    fullNames.append(df_playerInfo.iloc[currInd]['firstName']+' '+df_playerInfo.iloc[currInd]['surname'])
    #Get current players total points
    totals.append(df_2ptTotals.iloc[pp]['2ptTotal'])
    #Set current colour and name based on squad ID
    currSquadId = df_playerInfo.iloc[currInd]['squadId']
    squadInd = df_teamInfo.index[df_teamInfo['squadId'] == currSquadId].tolist()[0]
    currSquadName = df_teamInfo.iloc[squadInd]['squadNickname']    
    twoPointTotalsPalette.append(colourDict[currSquadName])
    squadNames.append(currSquadName)
    
#Create source for figure
figSource_2ptPlayerScoring.append(ColumnDataSource(data = dict(players = players,
                                                               counts = totals,
                                                               fullNames = fullNames,
                                                               squadNames = squadNames,
                                                               color = tuple(twoPointTotalsPalette))))

#Create figure
figPlot_2ptPlayerScoring.append(figure(x_range = players, plot_height = 400, plot_width = 800,
                                       title = 'Total Points from Super Shots',
                                       toolbar_location = None,
                                       tools = 'hover', 
                                       tooltips = [("Player", "@fullNames"), ("Team", "@squadNames"), ("Total Points from Super Shots", "@counts")]))

#Add bars
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].vbar(x = 'players', top = 'counts', width=0.6,
                                                    color = 'color', source = figSource_2ptPlayerScoring[ind_2ptPlayerScoring])

#Set figure parameters
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].y_range.start = 0
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].x_range.range_padding = 0.1
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].xaxis.major_label_orientation = 1
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].xgrid.grid_line_color = None
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].title.align = 'center'
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].yaxis.axis_label = 'Total Points'

# #Show figure
# show(figPlot_2ptPlayerScoring[ind_2ptPlayerScoring])

#Seems like storing html in same folder causes figures to overwrite?
#Make directory to store
os.mkdir('round'+str(round2Plot)+'-player-twopointtotals')
os.chdir('round'+str(round2Plot)+'-player-twopointtotals')
    
#Export figure as both .png and .html

##### TODO: set better naming strings for figures with looping

#PNG
export_png(figPlot_2ptPlayerScoring[ind_2ptPlayerScoring],
           filename = 'round'+str(round2Plot)+'-player-twopointtotals.png')

#HTML
output_file('round'+str(round2Plot)+'-player-twopointtotals.html')
save(figPlot_2ptPlayerScoring[ind_2ptPlayerScoring])

#Navigate back up
os.chdir('..')

#Add to two point figure indexing
ind_2ptPlayerScoring = ind_2ptPlayerScoring + 1

# %% Differential between two and one point scoring

##### TODO: fix so that players with no 2-point goals are still included...

#Extract a dataframe of 2pt Goals
df_allGoals = df_scoreFlow.loc[(df_scoreFlow['scoreName'].isin(['goal','2pt Goal'])) & 
                               (df_scoreFlow['roundNo'] == round2Plot),]

#Get the unique list of players who scored any goal
playerList_allGoals = list(df_allGoals['playerId'].unique())

#Loop through and sum the total one and two point value for each player
#Calculate the differential with +ve reflecting more two point points
playerList_2ptDifferential = list()
for pp in range(0,len(playerList_allGoals)):
    #Calculate and two vs. one point differential
    #Calculate two point score
    twoPointVal = df_allGoals.loc[(df_allGoals['playerId'] == playerList_allGoals[pp]) &
                                  (df_allGoals['scoreName'] == '2pt Goal'),
                                  ['scorePoints']].sum()[0]
    #Calculate one point score
    onePointVal = df_allGoals.loc[(df_allGoals['playerId'] == playerList_allGoals[pp]) &
                                  (df_allGoals['scoreName'] == 'goal'),
                                  ['scorePoints']].sum()[0]
    #Append differential
    playerList_2ptDifferential.append(twoPointVal - onePointVal)
    
#Convert to dataframe and sort
df_2ptDifferential = pd.DataFrame(list(zip(playerList_allGoals,playerList_2ptDifferential)),
                                  columns = ['playerId','2ptDifferential'])
df_2ptDifferential.sort_values(by = '2ptDifferential', inplace = True,
                               ascending = False, ignore_index = True)

#Create bar plot for two point totals
#Create lists to store the data in
players = list()
fullNames = list()
squadNames = list()
differentials = list()
twoPointDifferentialPalette = list()
#Loop through the player list and collate the data needed for the plot
for pp in range(0,len(df_2ptDifferential)):
    #Get the ID of the current player
    currId = df_2ptDifferential.iloc[pp]['playerId']
    #Get the dataframe ID of the current player
    currInd = df_playerInfo.index[df_playerInfo['playerId'] == currId].tolist()[0]
    #Get the current player details
    players.append(df_playerInfo.iloc[currInd]['displayName'])
    fullNames.append(df_playerInfo.iloc[currInd]['firstName']+' '+df_playerInfo.iloc[currInd]['surname'])
    #Get current players total points
    differentials.append(df_2ptDifferential.iloc[pp]['2ptDifferential'])
    #Set current colour and name based on squad ID
    currSquadId = df_playerInfo.iloc[currInd]['squadId']
    squadInd = df_teamInfo.index[df_teamInfo['squadId'] == currSquadId].tolist()[0]
    currSquadName = df_teamInfo.iloc[squadInd]['squadNickname']    
    twoPointDifferentialPalette.append(colourDict[currSquadName])
    squadNames.append(currSquadName)
    
#Create source for figure
figSource_2ptPlayerScoring.append(ColumnDataSource(data = dict(players = players,
                                                               counts = differentials,
                                                               fullNames = fullNames,
                                                               squadNames = squadNames,
                                                               color = tuple(twoPointDifferentialPalette))))

#Create figure
figPlot_2ptPlayerScoring.append(figure(x_range = players, plot_height = 400, plot_width = 800,
                                       title = 'Differential in Points from Super vs. Standard Shots',
                                       toolbar_location = None,
                                       tools = 'hover', 
                                       tooltips = [("Player", "@fullNames"), ("Team", "@squadNames"), ("Differential in Points from Standard vs. Super Shots", "@counts")]))

#Add bars
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].vbar(x = 'players', top = 'counts', width=0.6,
                                                    color = 'color', source = figSource_2ptPlayerScoring[ind_2ptPlayerScoring])

#Set figure parameters
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].x_range.range_padding = 0.1
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].xaxis.major_label_orientation = 1
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].xgrid.grid_line_color = None
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].title.align = 'center'
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].yaxis.axis_label = 'Points from Two-Point Shots - Points from One-Point Shots'

# #Show figure
# show(figPlot_2ptPlayerScoring[ind_2ptPlayerScoring])
    
#Export figure as both .png and .html

##### TODO: set better naming strings for figures with looping

#Seems like storing html in same folder causes figures to overwrite?
#Make directory to store
os.mkdir('round'+str(round2Plot)+'-player-twopointdifferentials')
os.chdir('round'+str(round2Plot)+'-player-twopointdifferentials')

#PNG
export_png(figPlot_2ptPlayerScoring[ind_2ptPlayerScoring],
           filename = 'round'+str(round2Plot)+'-player-twopointdifferentials.png')

#HTML
output_file('round'+str(round2Plot)+'-player-twopointdifferentials.html')
save(figPlot_2ptPlayerScoring[ind_2ptPlayerScoring])

#Navigate back up
os.chdir('..')

#Add to two point figure indexing
ind_2ptPlayerScoring = ind_2ptPlayerScoring + 1 

# %% Relative differential for two vs. one point totals

### This section already has the specific round...

#Loop through and sum the total one and two point value for each player
#Calculate the relative differential with +ve reflecting more two point points
playerList_2ptDifferentialRelative = list()
playerList_bothGoals = list()
for pp in range(0,len(playerList_allGoals)):
    #Calculate and two vs. one point differential
    #Calculate two point score
    twoPointVal = df_allGoals.loc[(df_allGoals['playerId'] == playerList_allGoals[pp]) &
                                  (df_allGoals['scoreName'] == '2pt Goal'),
                                  ['scorePoints']].sum()[0]
    #Calculate one point score
    onePointVal = df_allGoals.loc[(df_allGoals['playerId'] == playerList_allGoals[pp]) &
                                  (df_allGoals['scoreName'] == 'goal'),
                                  ['scorePoints']].sum()[0]
    #Append differential
    #Check if they have at least a score from each
    if twoPointVal != 0 and onePointVal != 0:
        playerList_bothGoals.append(playerList_allGoals[pp])
        playerList_2ptDifferentialRelative.append(twoPointVal / onePointVal)
    
#Convert to dataframe and sort
df_2ptDifferentialRelative = pd.DataFrame(list(zip(playerList_bothGoals,playerList_2ptDifferentialRelative)),
                                          columns = ['playerId','2ptDifferentialRelative'])
df_2ptDifferentialRelative.sort_values(by = '2ptDifferentialRelative', inplace = True,
                                       ascending = False, ignore_index = True)

#Create bar plot for two point totals
#Create lists to store the data in
players = list()
fullNames = list()
squadNames = list()
differentials = list()
twoPointDifferentialPalette = list()
#Loop through the player list and collate the data needed for the plot
for pp in range(0,len(df_2ptDifferentialRelative)):
    #Get the ID of the current player
    currId = df_2ptDifferentialRelative.iloc[pp]['playerId']
    #Get the dataframe ID of the current player
    currInd = df_playerInfo.index[df_playerInfo['playerId'] == currId].tolist()[0]
    #Get the current player details
    players.append(df_playerInfo.iloc[currInd]['displayName'])
    fullNames.append(df_playerInfo.iloc[currInd]['firstName']+' '+df_playerInfo.iloc[currInd]['surname'])
    #Get current players total points
    differentials.append(df_2ptDifferentialRelative.iloc[pp]['2ptDifferentialRelative'])
    #Set current colour and name based on squad ID
    currSquadId = df_playerInfo.iloc[currInd]['squadId']
    squadInd = df_teamInfo.index[df_teamInfo['squadId'] == currSquadId].tolist()[0]
    currSquadName = df_teamInfo.iloc[squadInd]['squadNickname']    
    twoPointDifferentialPalette.append(colourDict[currSquadName])
    squadNames.append(currSquadName)
    
#Create source for figure
figSource_2ptPlayerScoring.append(ColumnDataSource(data = dict(players = players,
                                                               counts = differentials,
                                                               fullNames = fullNames,
                                                               squadNames = squadNames,
                                                               color = tuple(twoPointDifferentialPalette))))

#Create figure
figPlot_2ptPlayerScoring.append(figure(x_range = players, plot_height = 400, plot_width = 800,
                                       title = 'Relative Differential in Points from Super vs. Standard Shots',
                                       toolbar_location = None,
                                       tools = 'hover', 
                                       tooltips = [("Player", "@fullNames"), ("Team", "@squadNames"), ("Ratio of Points from Super:Standard Shots", "@counts")]))

#Add bars
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].vbar(x = 'players', top = 'counts', width=0.6,
                                                    color = 'color', source = figSource_2ptPlayerScoring[ind_2ptPlayerScoring])

#Set figure parameters
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].y_range.start = 0
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].x_range.range_padding = 0.1
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].xaxis.major_label_orientation = 1
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].xgrid.grid_line_color = None
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].title.align = 'center'
figPlot_2ptPlayerScoring[ind_2ptPlayerScoring].yaxis.axis_label = 'Points from Super Shots / Points from Standard Shots'

# #Show figure
# show(figPlot_2ptPlayerScoring[ind_2ptPlayerScoring])
    
#Export figure as both .png and .html

##### TODO: set better naming strings for figures with looping

#Seems like storing html in same folder causes figures to overwrite?
#Make directory to store
os.mkdir('round'+str(round2Plot)+'-player-twopointdifferentialsrelative')
os.chdir('round'+str(round2Plot)+'-player-twopointdifferentialsrelative')

#PNG
export_png(figPlot_2ptPlayerScoring[ind_2ptPlayerScoring],
           filename = 'round'+str(round2Plot)+'-player-twopointdifferentialsrelative.png')

#HTML
output_file('round'+str(round2Plot)+'-player-twopointdifferentialsrelative.html')
save(figPlot_2ptPlayerScoring[ind_2ptPlayerScoring])

#Navigate back up
os.chdir('..')

#Add to two point figure indexing
ind_2ptPlayerScoring = ind_2ptPlayerScoring + 1 

# %% Plus/minus figures

# %% Team line-up plus/minus grid

##### TODO: sort plus minus per figure, toolbar in second html issue?

os.chdir('..\\..\\PlusMinusAnalysis')

##### NOTE: this doesn't split across rounds

#Get alphabetical list of squad nicknames
plotSquadNames = teamInfo['squadNickname']
plotSquadNames = sorted(plotSquadNames)

#Get the id's for the team names ordering
plotSquadId = list()
for tt in range(0,len(plotSquadNames)):
    plotSquadId.append(teamInfo['squadId'][teamInfo['squadNickname'].index(plotSquadNames[tt])])

#Set blank lists to fill with plots and source
figPlotAbs = list()
figSourceAbs = list()
figPlotPer = list()
figSourcePer = list()

#Loop through teams
for tt in range(0,len(plotSquadNames)):

    #Set current squad ID
    currSquadId = plotSquadId[tt]
    
    #Extract the lineup dataframe for the current team
    df_lineUpChecker = df_lineUp.loc[(df_lineUp['squadId'] == currSquadId),]
    df_lineUpChecker.reset_index(drop=True, inplace=True)
    
    #Loop through dataframe and create a new list of combined player names
    combinedLineUpName = list()
    for dd in range(0,len(df_lineUpChecker)):
        combinedLineUpName.append(", ".join(df_lineUpChecker['lineUpName'][dd]))
    #Append to dataframe
    df_lineUpChecker['combinedLineUpName'] = combinedLineUpName
        
    #Extract the unique lineups for the current team
    uniqueLineUps = df_lineUpChecker['combinedLineUpName'].unique()
    
    #Loop through unique lineups and sum the duration and plus/minus data
    ##### NOTE: current code only takes lineups that have played more than 5 mins
    #Durations converted to minutes here
    lineUpDuration = list()
    lineUpPlusMinus = list()
    analyseLineUps = list()
    for uu in range(0,len(uniqueLineUps)):
        #Get a separated dataframe
        df_currLineUp = df_lineUpChecker.loc[(df_lineUpChecker['combinedLineUpName'] == uniqueLineUps[uu]),]
        #Sum data and append to list if greater than 5 mins (300 seconds)
        if sum(df_currLineUp['durationSeconds']) >= 300:
            analyseLineUps.append(uniqueLineUps[uu])
            lineUpDuration.append(sum(df_currLineUp['durationSeconds']) / 60)
            lineUpPlusMinus.append(sum(df_currLineUp['plusMinus']))
    
    #Split the string of the lineups to put in figure source
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
        
    #Convert to dataframe and sort
    df_lineUpPlusMinus = pd.DataFrame(list(zip(analyseLineUps,lineUpDuration,lineUpPlusMinus,
                                               lineUpGS,lineUpGA,lineUpWA,lineUpC,lineUpWD,lineUpGD,lineUpGK)),
                                      columns = ['analyseLineUps','lineUpDuration','lineUpPlusMinus',
                                                 'lineUpGS','lineUpGA','lineUpWA','lineUpC','lineUpWD','lineUpGD','lineUpGK'])
    df_lineUpPlusMinus.sort_values(by = 'lineUpPlusMinus', inplace = True,
                                   ascending = False, ignore_index = True)
    
    #Add a per 15 column to dataframe
    perPlusMinus = list()
    perDivider = 15 #per 15 minutes
    for mm in range(0,len(df_lineUpPlusMinus)):
        perFac = perDivider / df_lineUpPlusMinus['lineUpDuration'][mm]
        perPlusMinus.append(df_lineUpPlusMinus['lineUpPlusMinus'][mm]*perFac)
    #Append to dataframe
    df_lineUpPlusMinus['lineUpPerPlusMinus'] = perPlusMinus
    
    #Create source for figures
    figSourceAbs.append(ColumnDataSource(data = dict(analyseLineUps = list(df_lineUpPlusMinus['analyseLineUps']),
                                                     plusMinus = list(df_lineUpPlusMinus['lineUpPlusMinus']),
                                                     durations = list(df_lineUpPlusMinus['lineUpDuration']),
                                                     lineUpGS = list(df_lineUpPlusMinus['lineUpGS']),
                                                     lineUpGA = list(df_lineUpPlusMinus['lineUpGA']),
                                                     lineUpWA = list(df_lineUpPlusMinus['lineUpWA']),
                                                     lineUpC = list(df_lineUpPlusMinus['lineUpC']),
                                                     lineUpWD = list(df_lineUpPlusMinus['lineUpWD']),
                                                     lineUpGD = list(df_lineUpPlusMinus['lineUpGD']),
                                                     lineUpGK = list(df_lineUpPlusMinus['lineUpGK']))))
    figSourcePer.append(ColumnDataSource(data = dict(analyseLineUps = list(df_lineUpPlusMinus['analyseLineUps']),
                                                     plusMinus = list(df_lineUpPlusMinus['lineUpPerPlusMinus']),
                                                     durations = list(df_lineUpPlusMinus['lineUpDuration']),
                                                     lineUpGS = list(df_lineUpPlusMinus['lineUpGS']),
                                                     lineUpGA = list(df_lineUpPlusMinus['lineUpGA']),
                                                     lineUpWA = list(df_lineUpPlusMinus['lineUpWA']),
                                                     lineUpC = list(df_lineUpPlusMinus['lineUpC']),
                                                     lineUpWD = list(df_lineUpPlusMinus['lineUpWD']),
                                                     lineUpGD = list(df_lineUpPlusMinus['lineUpGD']),
                                                     lineUpGK = list(df_lineUpPlusMinus['lineUpGK']))))
    
    #Create figures
    figPlotAbs.append(figure(x_range = list(df_lineUpPlusMinus['analyseLineUps']), plot_height = 300, plot_width = 400,
                             title = plotSquadNames[tt]+' Lineups Plus/Minus (Min. 5 Minutes Played)',
                             toolbar_location = None,
                             tools = 'hover', 
                             tooltips = [("GS", "@lineUpGS"), ("GA", "@lineUpGA"), ("WA", "@lineUpWA"), 
                                      ("C", "@lineUpC"), ("WD", "@lineUpWD"), ("GD", "@lineUpGD"), ("GK", "@lineUpGK"),
                                      ("Minutes Played", "@durations"), ("Plus/Minus", "@plusMinus")]))
    figPlotPer.append(figure(x_range = list(df_lineUpPlusMinus['analyseLineUps']), plot_height = 300, plot_width = 400,
                             title = plotSquadNames[tt]+' Lineups Plus/Minus per 15 Minute (Min. 5 Minutes Played)',
                             toolbar_location = None,
                             tools = 'hover', 
                             tooltips = [("GS", "@lineUpGS"), ("GA", "@lineUpGA"), ("WA", "@lineUpWA"), 
                                      ("C", "@lineUpC"), ("WD", "@lineUpWD"), ("GD", "@lineUpGD"), ("GK", "@lineUpGK"),
                                      ("Minutes Played", "@durations"), ("Plus/Minus per 15 Mins", "@plusMinus")]))
    
    #Add bars
    figPlotAbs[tt].vbar(x = 'analyseLineUps', top = 'plusMinus', width=0.6,
                        color = colourDict[plotSquadNames[tt]], source = figSourceAbs[tt])
    figPlotPer[tt].vbar(x = 'analyseLineUps', top = 'plusMinus', width=0.6,
                        color = colourDict[plotSquadNames[tt]], source = figSourcePer[tt])
    
    #Set figure parameters
    # figPlot[tt].y_range.start = 0
    figPlotAbs[tt].x_range.range_padding = 0.1
    figPlotAbs[tt].xaxis.major_label_orientation = 1
    figPlotAbs[tt].xgrid.grid_line_color = None
    figPlotAbs[tt].title.align = 'center'
    figPlotAbs[tt].yaxis.axis_label = 'Total Plus/Minus'
    figPlotAbs[tt].xaxis.major_label_text_font_size = '0pt'  # current solution to turn off long x-tick labels
    figPlotAbs[tt].xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    
    # figPlot[tt].y_range.start = 0
    figPlotPer[tt].x_range.range_padding = 0.1
    figPlotPer[tt].xaxis.major_label_orientation = 1
    figPlotPer[tt].xgrid.grid_line_color = None
    figPlotPer[tt].title.align = 'center'
    figPlotPer[tt].title.text_font_size = '8pt'
    figPlotPer[tt].yaxis.axis_label = 'Total Plus/Minus (per 15 minutes)'
    figPlotPer[tt].xaxis.major_label_text_font_size = '0pt'  # current solution to turn off long x-tick labels
    figPlotPer[tt].xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    
    # #Show figure
    # show(figPlotAbs[tt])
    # show(figPlotPer[tt])
    
#Create the gridplot
gridAbs = gridplot([[figPlotAbs[0], figPlotAbs[1], figPlotAbs[2], figPlotAbs[3]],
                    [figPlotAbs[4], figPlotAbs[5], figPlotAbs[6], figPlotAbs[7]]],
                   plot_height = 300, plot_width = 400)
gridPer = gridplot([[figPlotPer[0], figPlotPer[1], figPlotPer[2], figPlotPer[3]],
                    [figPlotPer[4], figPlotPer[5], figPlotPer[6], figPlotPer[7]]],
                   plot_height = 300, plot_width = 400)

# #Show grid
# show(gridAbs)
# show(gridPer)

#Export grid as both .png and .html

##### TODO: set better naming strings for figures with looping

#Seems like storing html in same folder causes figures to overwrite?
#Make directory to store
os.mkdir('total-absolutePlusMinus-teamLineUps')
os.chdir('total-absolutePlusMinus-teamLineUps')

#PNG
export_png(gridAbs, filename = 'total-absolutePlusMinus-teamLineUps.png')

#HTML
output_file('total-absolutePlusMinus-teamLineUps.html')
save(gridAbs)

#Navigate back up
os.chdir('..')     

#Seems like storing html in same folder causes figures to overwrite?
#Make directory to store
os.mkdir('total-per15PlusMinus-teamLineUps')
os.chdir('total-per15PlusMinus-teamLineUps')

#PNG
export_png(gridPer, filename = 'total-per15PlusMinus-teamLineUps.png')

#HTML
output_file('total-per15PlusMinus-teamLineUps.html')
save(gridPer)

#Navigate back up
os.chdir('..')  
    
# %% Plot player plus/minus

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
