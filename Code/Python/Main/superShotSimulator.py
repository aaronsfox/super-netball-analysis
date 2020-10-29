# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 21:13:39 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au

The goal of this analysis is to understand how many shot opportunities teams
get in the five minute super shot period, the success of standard vs. super shots 
in this period - and from this simulate how many points teams would expect to get
taking different proportions of standard vs. super shots
    
"""

# %% Import packages

import pandas as pd
pd.options.mode.chained_assignment = None #turn off pandas chained warnings
import numpy as np
import scipy.stats as stats
import random
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle 
import os
import math
import locale
locale.setlocale(locale.LC_ALL, 'en_US')

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
import ssn2020DataHelper as dataHelper

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

#Import data using helper function
dataImport = dataHelper.getMatchData(jsonFileList = jsonFileList,
                                     df_squadLists = df_squadLists,
                                     exportDict = True, exportDf = True,
                                     exportTeamData = True, exportPlayerData = True,
                                     exportMatchData = True, exportScoreData = True,
                                     exportLineUpData = True)

#Unpack the imported data
teamInfo = dataImport['teamInfo']
matchInfo = dataImport['matchInfo']
playerInfo = dataImport['playerInfo']
scoreFlowData = dataImport['scoreFlowData']
lineUpData = dataImport['lineUpData']
individualLineUpData = dataImport['individualLineUpData']
df_teamInfo = dataImport['df_teamInfo']
df_matchInfo = dataImport['df_matchInfo']
df_playerInfo = dataImport['df_playerInfo']
df_scoreFlow = dataImport['df_scoreFlow']
df_lineUp = dataImport['df_lineUp']
df_individualLineUp = dataImport['df_individualLineUp']

#Colour settings for teams
colourDict = {'Fever': '#00953b',
              'Firebirds': '#4b2c69',
              'GIANTS': '#f57921',
              'Lightning': '#fdb61c',
              'Magpies': '#494b4a',
              'Swifts': '#0082cd',
              'Thunderbirds': '#e54078',
              'Vixens': '#00a68e'}

# %% Run the standard simulation

#Set a list of proportions to examine across simulations
superShotProps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5,
                  0.6, 0.7, 0.8, 0.9, 1.0]
    
#Set number of simulations
nSims = 1000

#Set numpy seed
np.random.seed(123)

#Set random seed
random.seed(123)

#Create dictionary to store data in
superSimResults = {'squadId': [], 'squadNickname': [],
                   'nShots': [], 'nStandard': [], 'nSuper': [],
                   'superProp': [], 'superPropCat': [], 'totalPts': []}

#Set list to store actual team super shot proportions in
teamSuperProps = list()

#Get alphabetically ordered teams to loop through
teamList = list(colourDict.keys())

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
    
    #Calculate the current teams actual super shot proportions
    teamSuperProps.append((np.sum(madeSuper)+np.sum(missedSuper)) / np.sum(totalShots))  
    
    #Create a truncated normal distribution of the total shots mean/SD
    #Truncate it at 0 so that a team can't get less than no shots
    #Randomly sample values from the distribution to use in simulations
    
    #Sample from truncated normal distribution with mean/SD parameters
    #We choose to sample between the 95% CI of the mean here. This might
    #mean shots sometimes go below zero, but we have a check in place to not
    #analyse these later (although this is unlikely to happen...)
    lowLim = totalShotsM - (1.96 * (totalShotsSD / math.sqrt(len(totalShots))))
    uppLim = totalShotsM + (1.96 * (totalShotsSD / math.sqrt(len(totalShots))))
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

#Convert sim dictionary to dataframe
df_superSimResults = pd.DataFrame.from_dict(superSimResults)

# %% Get max and min scores with different proportions

#Get the proportion category names as a list
propCats = df_superSimResults['superPropCat'].unique()

#Calculate proportion of results that maximise score in each 10% bin

#Set data dictionary to store max results in to
maxSuperSimResults = {'squadNickname': [], 
                      'score': [], 'nShots': [],
                      'actualProp': [], 'superPropCat': []}

#Set data dictionary to store min results in to
minSuperSimResults = {'squadNickname': [], 
                      'score': [], 'nShots': [],
                      'actualProp': [], 'superPropCat': []}

#Loop through teams
for tt in range(0,len(teamList)):
    
    #Extract current teams data
    df_currTeamSims = df_superSimResults.loc[(df_superSimResults['squadNickname'] == teamList[tt]),]
    
    #Get the number of simulations ran for the current teams shots
    nTeamSims = int(len(df_currTeamSims)/len(superShotProps))
    
    #Loop through sims and extract the values for each to compare
    for nn in range(0,nTeamSims):
        
        #Get the results for each super shot proportion
        currShotResults = list()
        currShotProp = list()
        currShotNo = list()
        for pp in range(0,len(superShotProps)):
            currShotResults.append(df_currTeamSims.iloc[pp*nTeamSims+nn]['totalPts'])
            currShotProp.append(df_currTeamSims.iloc[pp*nTeamSims+nn]['superProp'])
            currShotNo.append(df_currTeamSims.iloc[pp*nTeamSims+nn]['nShots'])
        
        #Find the index of the maximum and minimum score
        mx = max(currShotResults)
        mn = min(currShotResults)
        mxInd = [ii for ii, jj in enumerate(currShotResults) if jj == mx]
        mnInd = [ii for ii, jj in enumerate(currShotResults) if jj == mn]
        #Check and see if there are more than one max, and take the smaller 
        #super shot proportion --- this assumes 'less risk'
        if len(mxInd) > 1:
            #Grab smaller super shot proportion value index
            for mm in range(0,len(mxInd)):
                if mm == 0:
                    #Just grab the first proportion to compare to the next
                    currSmallestProp = currShotProp[mxInd[mm]]
                else:
                    #Check to see if the next one is a smaller proportion
                    if currShotProp[mxInd[mm]] < currSmallestProp:
                        currSmallestProp = currShotProp[mxInd[mm]]
                        
            #Reset the mxInd value
            mxInd = currShotProp.index(currSmallestProp)
            
        else:
            
            #Set mxInd to int
            mxInd = int(mxInd[0])

        #Check and see if there are more than one min, and take the higher 
        #super shot proportion --- this assumes 'less risk'
        if len(mnInd) > 1:
            #Grab smaller super shot proportion value index
            for mm in range(0,len(mnInd)):
                if mm == 0:
                    #Just grab the first proportion to compare to the next
                    currSmallestProp = currShotProp[mnInd[mm]]
                else:
                    #Check to see if the next one is a greater proportion
                    if currShotProp[mnInd[mm]] > currSmallestProp:
                        currSmallestProp = currShotProp[mnInd[mm]]
                        
            #Reset the mxInd value
            mnInd = currShotProp.index(currSmallestProp)
            
        else:
            
            #Set mxInd to int
            mnInd = int(mnInd[0])         
        
        #Set values in data dictionary
        #Max value
        maxSuperSimResults['squadNickname'].append(teamList[tt])
        maxSuperSimResults['score'].append(currShotResults[mxInd])
        maxSuperSimResults['nShots'].append(currShotNo[mxInd])
        maxSuperSimResults['actualProp'].append(currShotProp[mxInd])
        #Min value
        minSuperSimResults['squadNickname'].append(teamList[tt])
        minSuperSimResults['score'].append(currShotResults[mnInd])
        minSuperSimResults['nShots'].append(currShotNo[mnInd])
        minSuperSimResults['actualProp'].append(currShotProp[mnInd])
        
        #Identify which bin the max and min super shot result falls in to, and append
        #Max value
        if currShotProp[mxInd] <= 0.1:
            maxSuperSimResults['superPropCat'].append('0%-10%')
        elif currShotProp[mxInd] > 0.1 and currShotProp[mxInd] <= 0.2:
            maxSuperSimResults['superPropCat'].append('10%-20%')
        elif currShotProp[mxInd] > 0.2 and currShotProp[mxInd] <= 0.3:
            maxSuperSimResults['superPropCat'].append('20%-30%')
        elif currShotProp[mxInd] > 0.3 and currShotProp[mxInd] <= 0.4:
            maxSuperSimResults['superPropCat'].append('30%-40%')
        elif currShotProp[mxInd] > 0.4 and currShotProp[mxInd] <= 0.5:
            maxSuperSimResults['superPropCat'].append('40%-50%')
        elif currShotProp[mxInd] > 0.5 and currShotProp[mxInd] <= 0.6:
            maxSuperSimResults['superPropCat'].append('50%-60%')
        elif currShotProp[mxInd] > 0.6 and currShotProp[mxInd] <= 0.7:
            maxSuperSimResults['superPropCat'].append('60%-70%')
        elif currShotProp[mxInd] > 0.7 and currShotProp[mxInd] <= 0.8:
            maxSuperSimResults['superPropCat'].append('70%-80%')
        elif currShotProp[mxInd] > 0.8 and currShotProp[mxInd] <= 0.9:
            maxSuperSimResults['superPropCat'].append('80%-90%')
        elif currShotProp[mxInd] > 0.9:
            maxSuperSimResults['superPropCat'].append('90%-100%')
        #Min value
        if currShotProp[mnInd] <= 0.1:
            minSuperSimResults['superPropCat'].append('0%-10%')
        elif currShotProp[mnInd] > 0.1 and currShotProp[mnInd] <= 0.2:
            minSuperSimResults['superPropCat'].append('10%-20%')
        elif currShotProp[mnInd] > 0.2 and currShotProp[mnInd] <= 0.3:
            minSuperSimResults['superPropCat'].append('20%-30%')
        elif currShotProp[mnInd] > 0.3 and currShotProp[mnInd] <= 0.4:
            minSuperSimResults['superPropCat'].append('30%-40%')
        elif currShotProp[mnInd] > 0.4 and currShotProp[mnInd] <= 0.5:
            minSuperSimResults['superPropCat'].append('40%-50%')
        elif currShotProp[mnInd] > 0.5 and currShotProp[mnInd] <= 0.6:
            minSuperSimResults['superPropCat'].append('50%-60%')
        elif currShotProp[mnInd] > 0.6 and currShotProp[mnInd] <= 0.7:
            minSuperSimResults['superPropCat'].append('60%-70%')
        elif currShotProp[mnInd] > 0.7 and currShotProp[mnInd] <= 0.8:
            minSuperSimResults['superPropCat'].append('70%-80%')
        elif currShotProp[mnInd] > 0.8 and currShotProp[mnInd] <= 0.9:
            minSuperSimResults['superPropCat'].append('80%-90%')
        elif currShotProp[mnInd] > 0.9:
            minSuperSimResults['superPropCat'].append('90%-100%')

#Convert max sim dictionary to dataframe
df_maxSuperSimResults = pd.DataFrame.from_dict(maxSuperSimResults)
df_minSuperSimResults = pd.DataFrame.from_dict(minSuperSimResults)

#Get counts in each 20% bin for each team and normalise these to the total 
#number of sims the team went through
##### NOTE: this uses 20% bins rather than the current 10% set-up

#Set dictionary to store data into
summaryMaxSimResults = {'squadNickname': [], '0%-20%': [], '20%-40%': [],
                        '40%-60%': [], '60%-80%': [], '80%-100%': [],
                        'meanShots': [], 'minShots': [], 'maxShots': []}
summaryMinSimResults = {'squadNickname': [], '0%-20%': [], '20%-40%': [],
                        '40%-60%': [], '60%-80%': [], '80%-100%': [],
                        'meanShots': [], 'minShots': [], 'maxShots': []}

#Loop through teams
for tt in range(0,len(teamList)):
    
    #Extract current teams data
    df_currTeamSims = df_superSimResults.loc[(df_superSimResults['squadNickname'] == teamList[tt]),]
    
    #Get the number of simulations ran for the current teams shots
    nTeamSims = int(len(df_currTeamSims)/len(superShotProps))
    
    #Append squadname to dictionary
    summaryMaxSimResults['squadNickname'].append(teamList[tt])
    summaryMinSimResults['squadNickname'].append(teamList[tt])
    
    #Get current team results for each proportion and set in each dictionary list
    #### NOTE: use of 20% bins
    #Max results
    summaryMaxSimResults['0%-20%'].append(len(df_maxSuperSimResults.loc[(df_maxSuperSimResults['squadNickname'] == teamList[tt]) &
                                                                    (df_maxSuperSimResults['superPropCat'].isin(['0%-10%','10%-20%'])),]) / nTeamSims)
    summaryMaxSimResults['20%-40%'].append(len(df_maxSuperSimResults.loc[(df_maxSuperSimResults['squadNickname'] == teamList[tt]) &
                                                                    (df_maxSuperSimResults['superPropCat'].isin(['20%-30%','30%-40%'])),]) / nTeamSims)
    summaryMaxSimResults['40%-60%'].append(len(df_maxSuperSimResults.loc[(df_maxSuperSimResults['squadNickname'] == teamList[tt]) &
                                                                    (df_maxSuperSimResults['superPropCat'].isin(['40%-50%','50%-60%'])),]) / nTeamSims)
    summaryMaxSimResults['60%-80%'].append(len(df_maxSuperSimResults.loc[(df_maxSuperSimResults['squadNickname'] == teamList[tt]) &
                                                                    (df_maxSuperSimResults['superPropCat'].isin(['60%-70%','70%-80%'])),]) / nTeamSims)
    summaryMaxSimResults['80%-100%'].append(len(df_maxSuperSimResults.loc[(df_maxSuperSimResults['squadNickname'] == teamList[tt]) &
                                                                    (df_maxSuperSimResults['superPropCat'].isin(['80%-90%','90%-100%'])),]) / nTeamSims)
    #Min results
    summaryMinSimResults['0%-20%'].append(len(df_minSuperSimResults.loc[(df_maxSuperSimResults['squadNickname'] == teamList[tt]) &
                                                                    (df_minSuperSimResults['superPropCat'].isin(['0%-10%','10%-20%'])),]) / nTeamSims)
    summaryMinSimResults['20%-40%'].append(len(df_minSuperSimResults.loc[(df_minSuperSimResults['squadNickname'] == teamList[tt]) &
                                                                    (df_minSuperSimResults['superPropCat'].isin(['20%-30%','30%-40%'])),]) / nTeamSims)
    summaryMinSimResults['40%-60%'].append(len(df_minSuperSimResults.loc[(df_minSuperSimResults['squadNickname'] == teamList[tt]) &
                                                                    (df_minSuperSimResults['superPropCat'].isin(['40%-50%','50%-60%'])),]) / nTeamSims)
    summaryMinSimResults['60%-80%'].append(len(df_minSuperSimResults.loc[(df_minSuperSimResults['squadNickname'] == teamList[tt]) &
                                                                    (df_minSuperSimResults['superPropCat'].isin(['60%-70%','70%-80%'])),]) / nTeamSims)
    summaryMinSimResults['80%-100%'].append(len(df_minSuperSimResults.loc[(df_minSuperSimResults['squadNickname'] == teamList[tt]) &
                                                                    (df_minSuperSimResults['superPropCat'].isin(['80%-90%','90%-100%'])),]) / nTeamSims)
    
    
    #Get the summary of shot statistics for current team
    #Max results
    summaryMaxSimResults['meanShots'].append(df_maxSuperSimResults.loc[(df_maxSuperSimResults['squadNickname'] == teamList[tt]),]['nShots'].mean())
    summaryMaxSimResults['minShots'].append(df_maxSuperSimResults.loc[(df_maxSuperSimResults['squadNickname'] == teamList[tt]),]['nShots'].min())
    summaryMaxSimResults['maxShots'].append(df_maxSuperSimResults.loc[(df_maxSuperSimResults['squadNickname'] == teamList[tt]),]['nShots'].max())
    #Min results
    summaryMinSimResults['meanShots'].append(df_minSuperSimResults.loc[(df_minSuperSimResults['squadNickname'] == teamList[tt]),]['nShots'].mean())
    summaryMinSimResults['minShots'].append(df_minSuperSimResults.loc[(df_minSuperSimResults['squadNickname'] == teamList[tt]),]['nShots'].min())
    summaryMinSimResults['maxShots'].append(df_minSuperSimResults.loc[(df_minSuperSimResults['squadNickname'] == teamList[tt]),]['nShots'].max())
    
    
#Convert summary dictionary to dataframe
df_summaryMaxSimResults = pd.DataFrame.from_dict(summaryMaxSimResults)  
df_summaryMinSimResults = pd.DataFrame.from_dict(summaryMinSimResults)  

#Export summary table to CSV
maxRound = max(df_matchInfo['roundNo'])
os.chdir('..\\..\\Code\\R\\htmlTables\\superSims\\Data')
df_summaryMaxSimResults.to_csv('standardSuperSimProportionMaxSummary_upToRound'+str(maxRound)+'.csv',
                               index = False)
df_summaryMinSimResults.to_csv('standardSuperSimProportionMinSummary_upToRound'+str(maxRound)+'.csv',
                               index = False)

#Export each teams proportion they actually use
df_teamSuperProps = pd.DataFrame()
df_teamSuperProps['squadNickname'] = teamList
df_teamSuperProps['actualProp'] = teamSuperProps
df_teamSuperProps.to_csv('actualSuperShotProportion_upToRound'+str(maxRound)+'.csv',
                         index = False)

# %% Visualise results

# %% Create an all teams heatmap

#Set-up axes to plot on
whichAx = [[0,0], [0,1],
           [1,0], [1,1],
           [2,0], [2,1],
           [3,0], [3,1]]

#Create figure to plot on
fig, ax = plt.subplots(figsize=(18, 9), nrows = 4, ncols = 2)

#Loop through teams and plot heat grid of their points
for tt in range(0,len(teamList)):

    ##### TODO: test bokeh stacked bar? Team colour palettes...
    
    #Extract current teams data
    df_currTeamSims = df_superSimResults.loc[(df_superSimResults['squadNickname'] == teamList[tt]),]
    
    #Get the number of simulations ran for the current teams shots
    nTeamSims = int(len(df_currTeamSims)/len(superShotProps))
    
    #Initialise array to store data in
    simArray = np.zeros([len(superShotProps)-1,nTeamSims])
    
    #Loop through the proportions
    for pp in range(0,len(propCats)):
        
        #Extract the dataframe of the current proportion
        df_currProp = df_currTeamSims.iloc[pp*nTeamSims:(pp*nTeamSims)+nTeamSims]
        
        #Extract the score
        scoreVals = df_currProp['totalPts'].values
        
        #Sort the values from lowest to highest
        scoreVals.sort()
        
        #Place in array (in reverse order)
        simArray[(pp+1)*-1,:] = scoreVals
    
    #Convert sim to a dataframe for plotting
    df_simArray = pd.DataFrame(simArray)
    #Set the index using the prop categories
    propCats.sort()
    df_simArray.set_index(propCats[::-1], inplace = True)
    
    #Plot heatmap
    sns.heatmap(df_simArray, cmap="RdYlGn", annot = False,
                linewidths = 0, ax = ax[whichAx[tt][0],whichAx[tt][1]])
    
    #Add horizontal separators via horizontal line
    lineWidth = 2
    for ii in range(simArray.shape[0]+1):
        ax[whichAx[tt][0],whichAx[tt][1]].axhline(ii, color = 'white', lw = lineWidth)
    
    #Outline the actual proportion for the team
    topLine = len(df_simArray) - math.ceil(teamSuperProps[tt]*10) - 1
    bottomLine = len(df_simArray) - math.floor(teamSuperProps[tt]*10) - 1
    ax[whichAx[tt][0],whichAx[tt][1]].add_patch(Rectangle(xy = (0-10, bottomLine), 
                                                          width = nTeamSims*2, height = 1, 
                                                          fill = False,  
                                                          edgecolor = 'black', 
                                                          lw = lineWidth,
                                                          zorder = 4))
        
    #Remove x-axis
    ax[whichAx[tt][0],whichAx[tt][1]].get_xaxis().set_ticks([])
    
    #Add x-axis label
    if whichAx[tt][0] == 3:
        ax[whichAx[tt][0],whichAx[tt][1]].set_xlabel('Rebel Power 5 Simulations (n = '+locale.format_string("%d", nTeamSims, grouping=True)+')')
    
    #Set y-ticks
    ax[whichAx[tt][0],whichAx[tt][1]].set_yticks([0.5, 1.5, 2.5, 3.5, 4.5,
                                                  5.5, 6.5, 7.5, 8.5, 9.5])
    
    #Set y-tick labels
    ax[whichAx[tt][0],whichAx[tt][1]].set_yticklabels(list(df_simArray.index),
                                                      fontsize = 8)
    
    #Add y-axis label
    if whichAx[tt][1] == 0:
        ax[whichAx[tt][0],whichAx[tt][1]].set_ylabel('Super Shot Proportion')
    
    #Add colourbar label
    ax[whichAx[tt][0],whichAx[tt][1]].collections[0].colorbar.set_label('Goals Scored')
    
    #Add title
    ax[whichAx[tt][0],whichAx[tt][1]].set_title(teamList[tt],
                                                fontweight = 'bold',
                                                fontsize = 12)
    
    #Print the max score for each team and it's proportion
    maxScore = df_simArray.max().max() #get max
    maxProps = df_simArray[df_simArray.eq(maxScore).any(1)].index #get proportions
    if len(maxProps) > 1:
        #Connect the strings
        maxProps = ' & '.join(maxProps)
    else:
        maxProps = maxProps[0]
    print(teamList[tt]+' max score of '+str(maxScore)+' using '+maxProps+' proportion.') #print result
    
#Set tight plot layout to fill frame
plt.tight_layout()
plt.show()

#Navigate to figures directory
os.chdir('..\\Figures')

#Save all teams figure
plt.savefig('SuperShotSimulations_HeatMap_AllTeams.pdf')
plt.savefig('SuperShotSimulations_HeatMap_AllTeams.png', format = 'png', dpi = 300)

#Close figure
plt.close()

# %% Create individual team heatmaps

#Loop through teams and plot heat grid of their points
for tt in range(0,len(teamList)):
    
    #Create figure to plot on
    fig, ax = plt.subplots(figsize=(9, 3), nrows = 1, ncols = 1)

    #Extract current teams data
    df_currTeamSims = df_superSimResults.loc[(df_superSimResults['squadNickname'] == teamList[tt]),]
    
    #Get the number of simulations ran for the current teams shots
    nTeamSims = int(len(df_currTeamSims)/len(superShotProps))
    
    #Initialise array to store data in
    simArray = np.zeros([len(superShotProps)-1,nTeamSims])
    
    #Loop through the proportions
    for pp in range(0,len(propCats)):
        
        #Extract the dataframe of the current proportion
        df_currProp = df_currTeamSims.iloc[pp*nTeamSims:(pp*nTeamSims)+nTeamSims]
        
        #Extract the score
        scoreVals = df_currProp['totalPts'].values
        
        #Sort the values from lowest to highest
        scoreVals.sort()
        
        #Place in array (in reverse order)
        simArray[(pp+1)*-1,:] = scoreVals
    
    #Convert sim to a dataframe for plotting
    df_simArray = pd.DataFrame(simArray)
    #Set the index using the prop categories
    propCats.sort()
    df_simArray.set_index(propCats[::-1], inplace = True)
    
    #Plot heatmap
    sns.heatmap(df_simArray, cmap="RdYlGn", annot = False,
                linewidths = 0, ax = ax)
    
    #Add horizontal separators via horizontal line
    lineWidth = 2
    for ii in range(simArray.shape[0]+1):
        ax.axhline(ii, color = 'white', lw = lineWidth)
    
    #Outline the actual proportion for the team
    topLine = len(df_simArray) - math.ceil(teamSuperProps[tt]*10) - 1
    bottomLine = len(df_simArray) - math.floor(teamSuperProps[tt]*10) - 1
    ax.add_patch(Rectangle(xy = (0-10, bottomLine), 
                    width = nTeamSims*2, height = 1, 
                    fill = False,  
                    edgecolor = 'black', 
                    lw = lineWidth,
                    zorder = 4))
        
    #Remove x-axis
    ax.get_xaxis().set_ticks([])
    
    #Add x-axis label
    ax.set_xlabel('Rebel Power 5 Simulations (n = '+locale.format_string("%d", nTeamSims, grouping=True)+')')
    
    #Set y-ticks
    ax.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5,
                   5.5, 6.5, 7.5, 8.5, 9.5])
    
    #Set y-tick labels
    ax.set_yticklabels(list(df_simArray.index),
                       fontsize = 10)
    
    #Add y-axis label
    ax.set_ylabel('Super Shot Proportion')
    
    #Add colourbar label
    ax.collections[0].colorbar.set_label('Goals Scored')
    
    #Add title
    ax.set_title(teamList[tt],
                 fontweight = 'bold',
                 fontsize = 12)

    #Set tight plot layout to fill frame
    plt.tight_layout()
    plt.show()
    
    #Save team figure
    plt.savefig('SuperShotSimulations_HeatMap_'+teamList[tt]+'.pdf')
    plt.savefig('SuperShotSimulations_HeatMap_'+teamList[tt]+'.png', format = 'png', dpi = 300)
    
    #Close figure
    plt.close()

# %%
   
    ##### UP TO HERE>>>>>

#Create a boxplot of the simulation results

# #Initialize the figure
# fig, axes = plt.subplots(nrows = 2, ncols = 4, figsize=(15, 7))

# #Set an axes look-up variable
# whichAx = [[0,0],[0,1],[0,2],[0,3],
#             [1,0],[1,1],[1,2],[1,3]]

# #Loop through the teams
# for tt in range(0,len(teamList)):

#     #Get current squad name
#     currSquadName = teamList[tt]
    
#     #Create the boxplot
#     gx = sns.boxplot(x = 'superPropCat', y = 'totalPts',
#                       data = df_superSimResults.loc[(df_superSimResults['squadNickname'] == currSquadName),],
#                       whis = [0, 100], width = 0.65,
#                       color = colourDict[currSquadName],
#                       ax = axes[whichAx[tt][0],whichAx[tt][1]])
    
#     #Set the box plot face and line colours
    
#     #First, identify the box to keep solid based on teams actual super shot proportions
#     solidBarInd = int(np.floor(teamSuperProps[tt]*10))
    
#     #Loop through boxes and fix colours
#     for ii in range(0,len(axes[whichAx[tt][0],whichAx[tt][1]].artists)):
        
#         #Get the current artist
#         artist = axes[whichAx[tt][0],whichAx[tt][1]].artists[ii]
        
#         #If the bar matches the one we want to keep solid, just change lines to black
#         if ii == solidBarInd:
            
#             #Set edge colour to black
#             artist.set_edgecolor('k')
            
#             #Each box has 6 associated Line2D objects (to make the whiskers, fliers, etc.)
#             #Loop over them here, and use black
#             for jj in range(ii*6,ii*6+6):
#                 line = axes[whichAx[tt][0],whichAx[tt][1]].lines[jj]
#                 line.set_color('k')
#                 line.set_mfc('k')
#                 line.set_mec('k')
                
#         else:
            
#             #Set the linecolor on the artist to the facecolor, and set the facecolor to None
#             col = artist.get_facecolor()
#             artist.set_edgecolor(col)
#             artist.set_facecolor('None')
            
#             #Each box has 6 associated Line2D objects (to make the whiskers, fliers, etc.)
#             #Loop over them here, and use the same colour as above
#             for jj in range(ii*6,ii*6+6):
#                 line = axes[whichAx[tt][0],whichAx[tt][1]].lines[jj]
#                 line.set_color(col)
#                 line.set_mfc(col)
#                 line.set_mec(col)
    
#     #Set x labels only for bottom row
#     if whichAx[tt][0] == 1:
#         gx.set(xlabel = 'Proportion of Total Shots as Super Shots')
#     else:
#         gx.set(xlabel = '')
        
#     #Set y label only for first column
#     if whichAx[tt][1] == 0:
#         gx.set(ylabel = 'Simulated Score')
#     else:
#         gx.set(ylabel = '')
        
#     #Rotate x-tick labels, but only for bottom row
#     if whichAx[tt][0] == 1:
#         axes[whichAx[tt][0],whichAx[tt][1]].tick_params('x', labelrotation = 45)
#     else:
#         axes[whichAx[tt][0],whichAx[tt][1]].set_xticklabels([])
    
#     #Point ticks in and make short
#     axes[whichAx[tt][0],whichAx[tt][1]].tick_params(axis = 'both',
#                                                     direction = 'in',
#                                                     length = 1.5)
    
#     #Set title
#     axes[whichAx[tt][0],whichAx[tt][1]].set_title(currSquadName,
#                                                   fontdict = {'fontsize': 12,
#                                                               'fontweight': 'bold'})

# #Set tight layout on figure
# fig.tight_layout()

# #Loop through and set y-axes to be consistent

# #Find maximum value across all axes
# currYmax = 0
# for tt in range(0,len(teamList)):
#     #Get current axes y-max and reset if greater than current
#     if axes[whichAx[tt][0],whichAx[tt][1]].get_ylim()[1] > currYmax:
#         currYmax = axes[whichAx[tt][0],whichAx[tt][1]].get_ylim()[1]
        
# #Round current y-max to ceiling whole number
# currYmax = np.ceil(currYmax)

# #Reset all of the axes ticks to min and new max
# #Also set the tick labels to have 6 ticks here
# for tt in range(0,len(teamList)):
#     axes[whichAx[tt][0],whichAx[tt][1]].set_ylim([axes[whichAx[tt][0],whichAx[tt][1]].get_ylim()[0],
#                                                   currYmax])
#     axes[whichAx[tt][0],whichAx[tt][1]].set_yticks(np.arange(0, currYmax+1, step = currYmax/6))

# #Export figure

# #Change directory
# os.chdir('..\\SuperShotSims')

#Export as PDF and basic png
plt.savefig('SuperShotSimulations_Standard.png', format = 'png', dpi = 300)

#Close figure
plt.close()