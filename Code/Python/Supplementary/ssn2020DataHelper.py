# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 20:05:01 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au

This helper script contains a series of functions that are used for
getting data from the Super Netball 2020 season files.
    
"""

# %% Import packages

import pandas as pd
pd.options.mode.chained_assignment = None #turn of pandas chained warnings
import json

# %% getMatchData

def getMatchData(jsonFileList = None, df_squadLists = None,
                 exportDict = True, exportDf = True,
                 exportTeamData = True, exportPlayerData = True,
                 exportMatchData = True, exportScoreData = True,
                 exportLineUpData = True):
    
    # Function for importing the Champion Data .json files for SSN 2020
    #
    # Input:    jsonFileList - list of .json files to import
    #           df_squadLists - dataframe of players in each squad for look-up
    #           exportDict - boolean flag whether to return to data dictionaries
    #           exportDf - boolean flag whether to export the dataframes
    #           exportTeamData - boolean flag whether to export the team data
    #           exportPlayerData - boolean flag whether to export the player data 
    #           exportMatchData - boolean flag whether to export the match data
    #           exportScoreData - boolean flag whether to export the score flow data
    #           exportLineUpData - boolean flag whether to export the line up data

    #Create blank dictionaries to store data in

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
    
    #Create a variable for starting positions
    starterPositions = ['GS','GA','WA','C','WD','GD','GK']
    
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
                    
                    #If current subs dataframe is empty, this is an error or even the
                    #random situation of a player being sent off (i.e. GIANTS match
                    #in round 5). This needs to be accounted for by pulling the position
                    #from the lineup
                    if len(df_currSubs) == 0:
                        
                        #Extract the player going to the bench in isolation
                        df_currSubs = df_subCheckerTeam.loc[(df_subCheckerTeam['matchSeconds'] == uniqueSubs[uu]) &
                                                            (df_subCheckerTeam['toPos'] == 'S'),]    
                        df_currSubs.reset_index(drop=True, inplace=True)
                        
                        #Create a new lineup variable to edit from the previous lineup
                        newLineUpId = list()
                        newLineUpName = list()
                        for pp in range(0,7):
                            newLineUpId.append(lineUpData['lineUpId'][len(lineUpData['lineUpId'])-1][pp])
                            newLineUpName.append(lineUpData['lineUpName'][len(lineUpData['lineUpName'])-1][pp])
                            
                        #Loop through substitutions and replace the lineup with an
                        #empty value where appropriate
                        for cc in range(0,len(df_currSubs)):
                            #Check for position and replace appropriately
                            if df_currSubs['fromPos'][cc] == 'GS':
                                #Replace player ID
                                newLineUpId[0] = []
                                #Replace player name
                                newLineUpName[0] = []
                            elif df_currSubs['fromPos'][cc] == 'GA':
                                #Replace player ID
                                newLineUpId[1] = []
                                #Replace player name
                                newLineUpName[1] = []
                            elif df_currSubs['fromPos'][cc] == 'WA':
                                #Replace player ID
                                newLineUpId[2] = []
                                #Replace player name
                                newLineUpName[2] = []
                            elif df_currSubs['fromPos'][cc] == 'C':
                                #Replace player ID
                                newLineUpId[3] = []
                                #Replace player name
                                newLineUpName[3] = []
                            elif df_currSubs['fromPos'][cc] == 'WD':
                                #Replace player ID
                                newLineUpId[4] = []
                                #Replace player name
                                newLineUpName[4] = []
                            elif df_currSubs['fromPos'][cc] == 'GD':
                                #Replace player ID
                                newLineUpId[5] = []
                                #Replace player name
                                newLineUpName[5] = []
                            elif df_currSubs['fromPos'][cc] == 'GK':
                                #Replace player ID
                                newLineUpId[6] = []
                                #Replace player name
                                newLineUpName[6] = []
                        
                    else:
                    
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
                        lineUpData['pointsFor'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId) &
                                                                       (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1),
                                                                       ['scorePoints']].sum()['scorePoints'])
                        #Set points against the lineup
                        lineUpData['pointsAgainst'].append(df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId) &
                                                                       (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1),
                                                                       ['scorePoints']].sum()['scorePoints'])
                        #Calculate plus/minus
                        plusMinus = df_scoreChecker.loc[(df_scoreChecker['squadId'] == currLineUpSquadId) &
                                                        (df_scoreChecker['matchSeconds'] > uniqueSubs[uu]+1),
                                                        ['scorePoints']].sum()['scorePoints'] - \
                            df_scoreChecker.loc[(df_scoreChecker['squadId'] != currLineUpSquadId) &
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
    
    #Export data
    
    #Set a dictionary to pack data in to
    exportData = dict()
    
    #Team info
    if exportTeamData is True:
        #Set to dataframe
        df_teamInfo = pd.DataFrame.from_dict(teamInfo)
        #Check and return data
        if exportDict is True:
            exportData['teamInfo'] = teamInfo
        if exportDf is True:
            exportData['df_teamInfo'] = df_teamInfo
        
    #Player info
    if exportPlayerData is True:
        #Set to dataframe
        df_playerInfo = pd.DataFrame.from_dict(playerInfo)
        #Check and return data
        if exportDict is True:
            exportData['playerInfo'] = playerInfo
        if exportDf is True:
            exportData['df_playerInfo'] =df_playerInfo
        
    #Match info
    if exportMatchData is True:
        #Set to dataframe
        df_matchInfo = pd.DataFrame.from_dict(matchInfo)
        #Check and return data
        if exportDict is True:
            exportData['matchInfo'] = matchInfo
        if exportDf is True:
            exportData['df_matchInfo'] = df_matchInfo
    
    #Score flow data
    if exportScoreData is True:
        #Set to dataframe
        df_scoreFlow = pd.DataFrame.from_dict(scoreFlowData)
        #Check and return data
        if exportDict is True:
            exportData['scoreFlowData'] = scoreFlowData
        if exportDf is True:
            exportData['df_scoreFlow'] = df_scoreFlow
    
    #Lineup data
    if exportLineUpData is True:
        #Set to dataframe
        df_lineUp = pd.DataFrame.from_dict(lineUpData)
        df_individualLineUp = pd.DataFrame.from_dict(individualLineUpData)
        #Check and return data
        if exportDict is True:
            exportData['lineUpData'] = lineUpData
            exportData['individualLineUpData'] = individualLineUpData
        if exportDf is True:
            exportData['df_lineUp'] = df_lineUp
            exportData['df_individualLineUp'] = df_individualLineUp
    
    #Return data dictionary
    return exportData
    
    ##### TODO: other dataframes once extracted
    ##### e.g. game statistics
    
# %%
    
    