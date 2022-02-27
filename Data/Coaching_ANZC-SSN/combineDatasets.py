# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 09:28:40 2021

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Quick script to combine the season win-loss and coach datasets together
    
"""

# %% Import packages

import pandas as pd

# %% Combine datasets

#Import season win-loss
winLoss = pd.read_csv('seasonWinLossSummaries.csv')

#Import coach dataset
coachData = pd.read_csv('coachSummaries.csv')

#Import premiership dataset
premiershipData = pd.read_csv('premiershipSummaries.csv')

#Loop through season data and identify coach and premiership status
coachList = []
minorPremierList = []
runnerUpList = []
premierList = []
competitionList = []
for ii in range(len(winLoss)):
    
    #Get current team and year
    team = winLoss['team'][ii]
    year = winLoss['year'][ii]
    
    #Get coach from dataset
    coach = coachData.loc[(coachData['team'] == team) &
                          (coachData['year'] == year),['coach']].reset_index(
                              drop = True)['coach'][0]
                              
    #Append to list
    coachList.append(coach)
                              
    #Get premiership/runner-up status
    #Premiers
    if premiershipData.loc[premiershipData['year'] == year,['premiers']].reset_index(
            drop = True)['premiers'][0] == team:
        premierList.append('Yes')
    else:
        premierList.append('No')
    #Minor premiers
    if premiershipData.loc[premiershipData['year'] == year,['minorPremiers']].reset_index(
            drop = True)['minorPremiers'][0] == team:
        minorPremierList.append('Yes')
    else:
        minorPremierList.append('No')
    #Runner Up
    if premiershipData.loc[premiershipData['year'] == year,['runnerUp']].reset_index(
            drop = True)['runnerUp'][0] == team:
        runnerUpList.append('Yes')
    else:
        runnerUpList.append('No')
    
    #Set competition
    competitionList.append(premiershipData.loc[premiershipData['year'] == year, ['competition']].reset_index(
        drop = True)['competition'][0])
    
#Add new variables to win loss dataframe
winLoss['coach'] = coachList
winLoss['minorPremiership'] = minorPremierList
winLoss['premiership'] = premierList
winLoss['runnerUp'] = runnerUpList
winLoss['competition'] = competitionList

#Save dataset
winLoss.to_csv('resultsFromTheTimeMachine.csv', index = False)

# %% ----- End of combineDatasets.py -----