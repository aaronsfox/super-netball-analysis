# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:13:01 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au

This code builds an output of weekly team ratings across the different competitions
and years used to build the win probability models.

The team ratings created here use the glicko2 system with the Python implementation
developed by Ryan Kirkman (see resources). Rather than attempt any carry-over across
years within teams and between competitions, we reset each teams rankings to the
default parameters of 1500 (ranking), 350 (deviation) and 0.06 (volatility).

Resources:
    
    http://www.glicko.net/glicko/glicko2.pdf
    https://github.com/ryankirkman/pyglicko2

"""

# %% Import packages

import glicko2
import pandas as pd
pd.options.mode.chained_assignment = None #turn of pandas chained warnings
import os
import json
# import math
# import numpy as np

# %% Load in match data

#Navigate to data directory
os.chdir('..\\MatchData')

#Get the list of .json files
jsonFileList = list()
for file in os.listdir(os.getcwd()):
    if file.endswith('.json'):
        jsonFileList.append(file)
        
#Get the scoreflow data for each match to determine results

#Create blank dictionaries to store data in
    
#Match info
matchInfo = {'id': [], 'homeSquadId': [], 'awaySquadId': [],
             'homeSquadName': [], 'awaySquadName': [],
             'startTime': [], 'roundNo': [], 'matchNo': [],
             'venueId': [], 'venueName': [], 'periodSeconds': [],
             'competition': [], 'year': []}

#Score flow data
scoreFlowData = {'roundNo': [], 'matchNo': [], 'matchId': [],
                 'competition': [], 'year': [],
                 'period': [], 'periodSeconds': [], 'matchSeconds': [],
                 'playerId': [],'squadId': [], 'scoreName': [], 'scorePoints': [],
                 'distanceCode': [], 'positionCode': []}

#Loop through file list and extract data
for ff in range(0,len(jsonFileList)):
    
    #Load the .json data
    with open(jsonFileList[ff], encoding = 'utf-8') as json_file:
        data = json.load(json_file)
        
    #Extract match details
    matchInfo['id'].append(data['matchInfo']['matchId'][0])
    matchInfo['homeSquadId'].append(data['matchInfo']['homeSquadId'][0])
    matchInfo['awaySquadId'].append(data['matchInfo']['awaySquadId'][0])
    if data['teamInfo']['team'][0]['squadId'][0] == data['matchInfo']['homeSquadId'][0]:
        matchInfo['homeSquadName'].append(data['teamInfo']['team'][0]['squadName'][0])
        matchInfo['awaySquadName'].append(data['teamInfo']['team'][1]['squadName'][0])
    else:
        matchInfo['homeSquadName'].append(data['teamInfo']['team'][1]['squadName'][0])
        matchInfo['awaySquadName'].append(data['teamInfo']['team'][0]['squadName'][0])
    matchInfo['startTime'].append(data['matchInfo']['localStartTime'][0])
    matchInfo['roundNo'].append(data['matchInfo']['roundNumber'][0])
    matchInfo['matchNo'].append(data['matchInfo']['matchNumber'][0])
    matchInfo['venueId'].append(data['matchInfo']['venueId'][0])
    matchInfo['venueName'].append(data['matchInfo']['venueName'][0])
    qtrSeconds = list()
    for qq in range(0,4):
        qtrSeconds.append(data['periodInfo']['qtr'][qq]['periodSeconds'][0])
    matchInfo['periodSeconds'].append(qtrSeconds)
    
    #Add competition details to match based on file name
    fileSplit = jsonFileList[ff].split('_')
    matchInfo['competition'].append(fileSplit[0])
    matchInfo['year'].append(int(fileSplit[1]))

    #Extract score flow data
    for ss in range(0,len(data['scoreFlow']['score'])):
        scoreFlowData['competition'].append(fileSplit[0])
        scoreFlowData['year'].append(int(fileSplit[1]))
        scoreFlowData['matchId'].append(data['matchInfo']['matchId'][0])
        scoreFlowData['roundNo'].append(data['matchInfo']['roundNumber'][0])
        scoreFlowData['matchNo'].append(data['matchInfo']['matchNumber'][0])
        scoreFlowData['period'].append(data['scoreFlow']['score'][ss]['period'][0])
        scoreFlowData['periodSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0])
        if data['scoreFlow']['score'][ss]['period'][0] == 1:
            #Just use period seconds
            scoreFlowData['matchSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0])
        elif data['scoreFlow']['score'][ss]['period'][0] == 2:
            #Add the preceding period seconds
            scoreFlowData['matchSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0])
        elif data['scoreFlow']['score'][ss]['period'][0] == 3:
            #Add the preceding period seconds
            scoreFlowData['matchSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0] + matchInfo['periodSeconds'][ff][1])
        elif data['scoreFlow']['score'][ss]['period'][0] >= 4:
            ##### NOTE: some random periods of 5 or 6 show up, but these aren't
            ##### listed in period seconds though???
            #Add the preceding period seconds
            scoreFlowData['matchSeconds'].append(data['scoreFlow']['score'][ss]['periodSeconds'][0] + matchInfo['periodSeconds'][ff][0] + matchInfo['periodSeconds'][ff][1] + matchInfo['periodSeconds'][ff][2])
        scoreFlowData['playerId'].append(data['scoreFlow']['score'][ss]['playerId'][0])
        scoreFlowData['squadId'].append(data['scoreFlow']['score'][ss]['squadId'][0])
        scoreFlowData['scoreName'].append(data['scoreFlow']['score'][ss]['scoreName'][0])
        scoreFlowData['scorePoints'].append(data['scoreFlow']['score'][ss]['scorepoints'][0])
        scoreFlowData['distanceCode'].append(data['scoreFlow']['score'][ss]['distanceCode'][0])
        scoreFlowData['positionCode'].append(data['scoreFlow']['score'][ss]['positionCode'][0])

#Convert to dataframes
df_matchInfo = pd.DataFrame.from_dict(matchInfo)
df_scoreFlow = pd.DataFrame.from_dict(scoreFlowData)

# %% Determine match results

# As part of this analysis the score will be determined, with a +ve marging representing
# a home team win and -ve margin an away team win. Similarly, the match result will
# be indicated as 1 for a home team win and -1 for an away team win (0 for draw)

#Identify the unique match ID's to work through
matchList = df_matchInfo['id'].unique()

#Set lists to place margins and match results into
margin = list()
result = list()

#Loop through matches and extract results
for mm in range(0,len(matchList)):
    
    #Get current match score flow data
    df_currScoreFlow = df_scoreFlow.loc[(df_scoreFlow['matchId'] == matchList[mm]),]
    
    #Get the current squad identifiers
    homeSquadId = df_matchInfo['homeSquadId'][mm]
    awaySquadId = df_matchInfo['awaySquadId'][mm]
    
    #Total up the scores for each team
    homeScore = df_currScoreFlow.loc[(df_currScoreFlow['squadId'] == homeSquadId),
                                     ['scorePoints']].sum()[0]
    awayScore = df_currScoreFlow.loc[(df_currScoreFlow['squadId'] == awaySquadId),
                                     ['scorePoints']].sum()[0]
    
    #Calculate and append the margin relative to home team
    margin.append(homeScore - awayScore)
    
    #Determine win/loss/draw identifier
    if (homeScore - awayScore) > 0:
        #Home win
        result.append(1)
    elif (homeScore - awayScore) < 0:
        #Away win
        result.append(-1)
    elif homeScore == awayScore:
        #Draw
        result.append(0)
    
#Append the new columns to the match info data
df_matchInfo['margin'] = margin
df_matchInfo['result'] = result

# %% Determine competition/years to evaluate

# This process involves identifying the different competitions and years, and
# the different teams involved. Once we have that, we can loop through the progressive
# rounds and calculate what each teams rating is at the beginning of that round

#Create a list of the different competitions
compList = df_matchInfo['competition'].unique()

#Extract the years each competition ran
compYears = list()
for cc in range(0,len(compList)):
    #Extract current competition
    df_currComp = df_matchInfo.loc[(df_matchInfo['competition'] == compList[cc]),]
    #Append years to list
    compYears.append(list(df_currComp['year'].unique()))
    
#Extract the teams for each competition and year
compDict = {'competition': [], 'year': [], 'teamId': [], 'teamName': [], 'rounds': []}

#Loop through competitions
for cc in range(0,len(compList)):
    
    #Loop through years of current competition
    for yy in range(0,len(compYears[cc])):
        
        #Extract current competition and year data
        df_currComp = df_matchInfo.loc[(df_matchInfo['competition'] == compList[cc]) &
                                       (df_matchInfo['year'] == compYears[cc][yy]),]
        
        #Set the current competition, year and round number in dictionary
        compDict['competition'].append(compList[cc])
        compDict['year'].append(compYears[cc][yy])
        
        #Set the number of rounds
        compDict['rounds'].append(max(df_currComp['roundNo']))
        
        #Get the list of unique teams
        #ID's
        homeTeamId = list(df_currComp['homeSquadId'].unique())
        awayTeamId = list(df_currComp['awaySquadId'].unique())
        allTeamId = (list((set(homeTeamId) | set(awayTeamId))))
        compDict['teamId'].append(allTeamId)
        #Team names (slightly different implementation to match up)
        #Assumes every team has at least one home game, which they should
        allTeamName = list()
        for aa in range(0,len(allTeamId)):
            #Get team name and append to list
            allTeamName.append(df_currComp.loc[(df_currComp['homeSquadId'] == allTeamId[aa]),
                                               ]['homeSquadName'].unique()[0])
        #Names
        compDict['teamName'].append(allTeamName)
        
# %% Calculate weekly glicko2 ratings

##### TODO: could build multiple iterations of this rating system to test with
##### different parameters (i.e. different starting deviations, reverting to previous
##### season ratings or a proportion of this?)

##### TODO: consider changing volatility as it doesn't seem to shift much?

# As part of this, we loop through the teams and rounds of each competition and
# calculate their new glicko2 ratings each week, remembering that each year of a
# competition starts with the default values
#
# Note that the rankings calculated here represent what the team is ranked at the
# *START* of the current round they are listed for.

#Set dictionary to store all data in
glicko2Dict = {'competition': [], 'year': [], 'round': [],
               'teamId': [], 'teamName': [],
               'glicko2Rating': [], 'glicko2Deviation': [], 'glicko2Volatility': []}

#Loop through competition years
for cc in range(0,len(compDict['competition'])):
    
    #Get current competition details
    currComp = compDict['competition'][cc]
    currRounds = compDict['rounds'][cc]
    currYear = compDict['year'][cc]
    currTeamIds = compDict['teamId'][cc]
    currTeamNames = compDict['teamName'][cc]
    
    #Loop through rounds and allocate ratings
    for rr in range(0,currRounds):
        
        #First check if it's the first round
        if rr == 0:
            
            #Loop through teams and allocate default ratings
            for tt in range(0,len(currTeamIds)):
                
                #Add competition and round parameters to dictionary
                glicko2Dict['competition'].append(currComp)
                glicko2Dict['year'].append(currYear)
                glicko2Dict['round'].append(rr+1)
                
                #Add team details to the dictionary
                glicko2Dict['teamId'].append(currTeamIds[tt])
                glicko2Dict['teamName'].append(currTeamNames[tt])
                
                #Create default glicko2 rating
                glickoRating = glicko2.Player()
                
                #Extract and add the default parameters
                glicko2Dict['glicko2Rating'].append(glickoRating.rating)
                glicko2Dict['glicko2Deviation'].append(glickoRating.rd)
                glicko2Dict['glicko2Volatility'].append(glickoRating.vol)
        
        #If not the first round
        else:
            
            #Loop through teams, determine their result and new rating
            for tt in range(0,len(currTeamIds)):
                
                #Convert intermediate dictionary to dataframe
                df_currGlicko2 = pd.DataFrame.from_dict(glicko2Dict)
                
                #Get the current teams values from the past round
                currTeamGlicko = df_currGlicko2.loc[(df_currGlicko2['competition'] == currComp) &
                                                     (df_currGlicko2['year'] == currYear) &
                                                      (df_currGlicko2['teamId'] == currTeamIds[tt]) &
                                                       (df_currGlicko2['round'] == rr),]
                currTeamGlicko.reset_index(inplace = True)
                rating = currTeamGlicko['glicko2Rating'][0]
                rd = currTeamGlicko['glicko2Deviation'][0]
                vol = currTeamGlicko['glicko2Volatility'][0]
                                    
                #Identify the current teams match in the match info dataframe
                #Check for both home and away match for the current team
                homeCheck = df_matchInfo.loc[(df_matchInfo['competition'] == currComp) &
                                             (df_matchInfo['year'] == currYear) &
                                             (df_matchInfo['roundNo'] == rr) &
                                             (df_matchInfo['homeSquadId'] == currTeamIds[tt]),]
                awayCheck = df_matchInfo.loc[(df_matchInfo['competition'] == currComp) &
                                             (df_matchInfo['year'] == currYear) &
                                             (df_matchInfo['roundNo'] == rr) &
                                             (df_matchInfo['awaySquadId'] == currTeamIds[tt]),]
                
                #Check if both dataframes are empty so the team didn't play. If
                #this is the case we can just use their existing values
                if len(homeCheck) == 0 and len(awayCheck) == 0:
                    
                    #Team didn't play, use existing ratings
                    
                    #Add competition and round parameters to dictionary
                    glicko2Dict['competition'].append(currComp)
                    glicko2Dict['year'].append(currYear)
                    glicko2Dict['round'].append(rr+1)
                    
                    #Add team details to the dictionary
                    glicko2Dict['teamId'].append(currTeamIds[tt])
                    glicko2Dict['teamName'].append(currTeamNames[tt])
                    
                    #Create default glicko2 rating
                    glickoRating = glicko2.Player()
                    
                    #Extract and add the default parameters
                    glicko2Dict['glicko2Rating'].append(rating)
                    glicko2Dict['glicko2Deviation'].append(rd)
                    glicko2Dict['glicko2Volatility'].append(vol)
                    
                elif len(homeCheck) == 1:
                    
                    #Team played a home game
                    homeCheck.reset_index(inplace = True)
                    
                    #Get their oppositions current rating
                    oppTeamId = homeCheck['awaySquadId'][0]
                    oppTeamGlicko = df_currGlicko2.loc[(df_currGlicko2['competition'] == currComp) &
                                                       (df_currGlicko2['year'] == currYear) &
                                                       (df_currGlicko2['teamId'] == oppTeamId) &
                                                       (df_currGlicko2['round'] == rr),]
                    oppTeamGlicko.reset_index(inplace = True)
                    oppRating = oppTeamGlicko['glicko2Rating'][0]
                    oppRd = oppTeamGlicko['glicko2Deviation'][0]
                    oppVol = oppTeamGlicko['glicko2Volatility'][0]
                    
                    #Code the result for the current team
                    if homeCheck['result'][0] > 0:
                        matchResult = 1
                    elif homeCheck['result'][0] < 0:
                        matchResult = 0
                    elif homeCheck['result'][0] == 0:
                        matchResult = 0.5
                        
                    #Create the current teams glicko2 rating
                    glickoRating = glicko2.Player(rating = rating,
                                                  rd = rd,
                                                  vol = vol)
                    
                    #Update the current teams glicko2 rating
                    glickoRating.update_player([oppRating],
                                               [oppRd],
                                               [matchResult])
                    
                    #Add competition and round parameters to dictionary
                    glicko2Dict['competition'].append(currComp)
                    glicko2Dict['year'].append(currYear)
                    glicko2Dict['round'].append(rr+1)
                    
                    #Add team details to the dictionary
                    glicko2Dict['teamId'].append(currTeamIds[tt])
                    glicko2Dict['teamName'].append(currTeamNames[tt])
                    
                    #Extract and add the default parameters
                    glicko2Dict['glicko2Rating'].append(glickoRating.rating)
                    glicko2Dict['glicko2Deviation'].append(glickoRating.rd)
                    glicko2Dict['glicko2Volatility'].append(glickoRating.vol)
                    
                elif len(awayCheck) == 1:
                    
                    #Team played an away game
                    awayCheck.reset_index(inplace = True)
                    
                    #Get their oppositions current rating
                    oppTeamId = awayCheck['homeSquadId'][0]
                    oppTeamGlicko = df_currGlicko2.loc[(df_currGlicko2['competition'] == currComp) &
                                                       (df_currGlicko2['year'] == currYear) &
                                                       (df_currGlicko2['teamId'] == oppTeamId) &
                                                       (df_currGlicko2['round'] == rr),]
                    oppTeamGlicko.reset_index(inplace = True)
                    oppRating = oppTeamGlicko['glicko2Rating'][0]
                    oppRd = oppTeamGlicko['glicko2Deviation'][0]
                    oppVol = oppTeamGlicko['glicko2Volatility'][0]
                    
                    #Code the result for the current team
                    if awayCheck['result'][0] < 0:
                        matchResult = 1
                    elif awayCheck['result'][0] > 0:
                        matchResult = 0
                    elif awayCheck['result'][0] == 0:
                        matchResult = 0.5
                        
                    #Create the current teams glicko2 rating
                    glickoRating = glicko2.Player(rating = rating,
                                                  rd = rd,
                                                  vol = vol)
                    
                    #Update the current teams glicko2 rating
                    glickoRating.update_player([oppRating],
                                               [oppRd],
                                               [matchResult])
                    
                    #Add competition and round parameters to dictionary
                    glicko2Dict['competition'].append(currComp)
                    glicko2Dict['year'].append(currYear)
                    glicko2Dict['round'].append(rr+1)
                    
                    #Add team details to the dictionary
                    glicko2Dict['teamId'].append(currTeamIds[tt])
                    glicko2Dict['teamName'].append(currTeamNames[tt])
                    
                    #Extract and add the default parameters
                    glicko2Dict['glicko2Rating'].append(glickoRating.rating)
                    glicko2Dict['glicko2Deviation'].append(glickoRating.rd)
                    glicko2Dict['glicko2Volatility'].append(glickoRating.vol)
                    
                elif len(homeCheck) > 1:
                    
                    #Team played multiple home games
                    homeCheck.reset_index(inplace = True)
                    
                    #Set lists to store values for updating rankings
                    oppRating = list()
                    oppRd = list()
                    oppVol = list()
                    matchResult = list()
                    
                    #Loop through matches and compile into adjusting rating
                    for gg in range(0,len(homeCheck)):
                        
                        #Get their oppositions current rating
                        oppTeamId = homeCheck['awaySquadId'][gg]
                        oppTeamGlicko = df_currGlicko2.loc[(df_currGlicko2['competition'] == currComp) &
                                                           (df_currGlicko2['year'] == currYear) &
                                                           (df_currGlicko2['teamId'] == oppTeamId) &
                                                           (df_currGlicko2['round'] == rr),]
                        oppTeamGlicko.reset_index(inplace = True)
                        oppRating.append(oppTeamGlicko['glicko2Rating'][0])
                        oppRd.append(oppTeamGlicko['glicko2Deviation'][0])
                        oppVol.append(oppTeamGlicko['glicko2Volatility'][0])
                        
                        #Code the result for the current team
                        if homeCheck['result'][gg] > 0:
                            matchResult.append(1)
                        elif homeCheck['result'][gg] < 0:
                            matchResult.append(0)
                        elif homeCheck['result'][gg] == 0:
                            matchResult.append(0.5)
                            
                    #Create the current teams glicko2 rating
                    glickoRating = glicko2.Player(rating = rating,
                                                  rd = rd,
                                                  vol = vol)
                    
                    #Update the current teams glicko2 rating
                    glickoRating.update_player(oppRating,
                                               oppRd,
                                               matchResult)
                    
                    #Add competition and round parameters to dictionary
                    glicko2Dict['competition'].append(currComp)
                    glicko2Dict['year'].append(currYear)
                    glicko2Dict['round'].append(rr+1)
                    
                    #Add team details to the dictionary
                    glicko2Dict['teamId'].append(currTeamIds[tt])
                    glicko2Dict['teamName'].append(currTeamNames[tt])
                    
                    #Extract and add the default parameters
                    glicko2Dict['glicko2Rating'].append(glickoRating.rating)
                    glicko2Dict['glicko2Deviation'].append(glickoRating.rd)
                    glicko2Dict['glicko2Volatility'].append(glickoRating.vol)
                    
                elif len(awayCheck) > 1:
                    
                    #Team played multiple away games
                    awayCheck.reset_index(inplace = True)
                    
                    #Set lists to store values for updating rankings
                    oppRating = list()
                    oppRd = list()
                    oppVol = list()
                    matchResult = list()
                    
                    #Loop through matches and compile into adjusting rating
                    for gg in range(0,len(awayCheck)):
                        
                        #Get their oppositions current rating
                        oppTeamId = awayCheck['homeSquadId'][gg]
                        oppTeamGlicko = df_currGlicko2.loc[(df_currGlicko2['competition'] == currComp) &
                                                           (df_currGlicko2['year'] == currYear) &
                                                           (df_currGlicko2['teamId'] == oppTeamId) &
                                                           (df_currGlicko2['round'] == rr),]
                        oppTeamGlicko.reset_index(inplace = True)
                        oppRating.append(oppTeamGlicko['glicko2Rating'][0])
                        oppRd.append(oppTeamGlicko['glicko2Deviation'][0])
                        oppVol.append(oppTeamGlicko['glicko2Volatility'][0])
                        
                        #Code the result for the current team
                        if awayCheck['result'][gg] < 0:
                            matchResult.append(1)
                        elif awayCheck['result'][gg] > 0:
                            matchResult.append(0)
                        elif awayCheck['result'][gg] == 0:
                            matchResult.append(0.5)
                            
                    #Create the current teams glicko2 rating
                    glickoRating = glicko2.Player(rating = rating,
                                                  rd = rd,
                                                  vol = vol)
                    
                    #Update the current teams glicko2 rating
                    glickoRating.update_player(oppRating,
                                               oppRd,
                                               matchResult)
                    
                    #Add competition and round parameters to dictionary
                    glicko2Dict['competition'].append(currComp)
                    glicko2Dict['year'].append(currYear)
                    glicko2Dict['round'].append(rr+1)
                    
                    #Add team details to the dictionary
                    glicko2Dict['teamId'].append(currTeamIds[tt])
                    glicko2Dict['teamName'].append(currTeamNames[tt])
                    
                    #Extract and add the default parameters
                    glicko2Dict['glicko2Rating'].append(glickoRating.rating)
                    glicko2Dict['glicko2Deviation'].append(glickoRating.rd)
                    glicko2Dict['glicko2Volatility'].append(glickoRating.vol)
                    
                elif len(homeCheck) > 0 and len(awayCheck) > 0:
                    
                    #Team played a home and away game
                    
                    #Run home games
                    homeCheck.reset_index(inplace = True)
                    
                    #Set lists to store values for updating rankings
                    oppRating = list()
                    oppRd = list()
                    oppVol = list()
                    matchResult = list()
                    
                    #Loop through matches and compile into adjusting rating
                    for gg in range(0,len(homeCheck)):
                        
                        #Get their oppositions current rating
                        oppTeamId = homeCheck['awaySquadId'][gg]
                        oppTeamGlicko = df_currGlicko2.loc[(df_currGlicko2['competition'] == currComp) &
                                                           (df_currGlicko2['year'] == currYear) &
                                                           (df_currGlicko2['teamId'] == oppTeamId) &
                                                           (df_currGlicko2['round'] == rr),]
                        oppTeamGlicko.reset_index(inplace = True)
                        oppRating.append(oppTeamGlicko['glicko2Rating'][0])
                        oppRd.append(oppTeamGlicko['glicko2Deviation'][0])
                        oppVol.append(oppTeamGlicko['glicko2Volatility'][0])
                        
                        #Code the result for the current team
                        if homeCheck['result'][gg] > 0:
                            matchResult.append(1)
                        elif homeCheck['result'][gg] < 0:
                            matchResult.append(0)
                        elif homeCheck['result'][gg] == 0:
                            matchResult.append(0.5)
                    
                    #Run away games
                    awayCheck.reset_index(inplace = True)

                    #Loop through matches and compile into adjusting rating
                    for gg in range(0,len(awayCheck)):
                        
                        #Get their oppositions current rating
                        oppTeamId = awayCheck['homeSquadId'][gg]
                        oppTeamGlicko = df_currGlicko2.loc[(df_currGlicko2['competition'] == currComp) &
                                                           (df_currGlicko2['year'] == currYear) &
                                                           (df_currGlicko2['teamId'] == oppTeamId) &
                                                           (df_currGlicko2['round'] == rr),]
                        oppTeamGlicko.reset_index(inplace = True)
                        oppRating.append(oppTeamGlicko['glicko2Rating'][0])
                        oppRd.append(oppTeamGlicko['glicko2Deviation'][0])
                        oppVol.append(oppTeamGlicko['glicko2Volatility'][0])
                        
                        #Code the result for the current team
                        if awayCheck['result'][gg] < 0:
                            matchResult.append(1)
                        elif awayCheck['result'][gg] > 0:
                            matchResult.append(0)
                        elif awayCheck['result'][gg] == 0:
                            matchResult.append(0.5)
                            
                    #Create the current teams glicko2 rating
                    glickoRating = glicko2.Player(rating = rating,
                                                  rd = rd,
                                                  vol = vol)
                    
                    #Update the current teams glicko2 rating
                    glickoRating.update_player(oppRating,
                                               oppRd,
                                               matchResult)
                    
                    #Add competition and round parameters to dictionary
                    glicko2Dict['competition'].append(currComp)
                    glicko2Dict['year'].append(currYear)
                    glicko2Dict['round'].append(rr+1)
                    
                    #Add team details to the dictionary
                    glicko2Dict['teamId'].append(currTeamIds[tt])
                    glicko2Dict['teamName'].append(currTeamNames[tt])
                    
                    #Extract and add the default parameters
                    glicko2Dict['glicko2Rating'].append(glickoRating.rating)
                    glicko2Dict['glicko2Deviation'].append(glickoRating.rd)
                    glicko2Dict['glicko2Volatility'].append(glickoRating.vol)
                    
#Convert glicko2 rating dictionary to dataframe
df_glicko2Ratings = pd.DataFrame.from_dict(glicko2Dict)

#Export rating data to .csv
os.chdir('..\\TeamRatings')
df_glicko2Ratings.to_csv('glicko2Ratings.csv', index = False)

# %%  Calculate weekly ELO ratings

##### TODO: add ELO rating as another system to check in model --- this may be
##### useful as it accounts for margin whereas Glicko2 doesn't. We could also 
##### create multiple ELO systems altering the parameters to test in the model
