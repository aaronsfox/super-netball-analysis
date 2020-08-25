# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 15:19:31 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au

This code develops a win probability model using a random forest implementation.

TODO: add more detailed notes...

TODO: could also consider RF regression for margin prediction...

TODO: current model contains 2020 data --- not accurate due to super shot
and needs to be removed!!!!!

TODO: the home team and away team biggest runs are wrong

Resources:
    
    https://towardsdatascience.com/an-implementation-and-explanation-of-the-random-forest-in-python-77bf308a9b76
    
"""

# %% Import packages

import pandas as pd
pd.options.mode.chained_assignment = None #turn of pandas chained warnings
import os
import json
import math
import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, roc_auc_score, roc_curve, confusion_matrix
from matplotlib import pyplot as plt
import itertools

# %% Load in match data

#Navigate to data directory
os.chdir('..\\MatchData')

#Get the list of .json files
jsonFileList = list()
for file in os.listdir(os.getcwd()):
    if file.endswith('.json'):
        jsonFileList.append(file)
        
#Get the scoreflow data for each match
##### NOTE: clearly only just focusing on score flow...
##### Can add other things here too though...e.g. team ratings (adding now...)...
##### TODO: when this starts to get larger --- consider adding to a function...

#Create blank dictionaries to store data in
    
#Match info
matchInfo = {'id': [], 'homeSquadId': [], 'awaySquadId': [],
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

# %% Import team ratings

#Navigate to directory
os.chdir('..\\TeamRatings')

#Glicko2 ratings
df_glicko2Ratings = pd.read_csv('glicko2Ratings.csv')
                
# %% Convert score flow data to step by step scoring

# Each score event in a match will be recorded here, with specific variables detailing
# the current score setting. These will be: (1) scoreDiff - the current score margin
# with +ve values representing the home team in front; (2) currRun - the current
# score run with +ve values representing the home teams run; (3) homeBiggestRun -
# the current largest run of goals for home team; (4) awayBiggestRun - the current
# largest run of goals for away team; (5) homeLast10 - proportion of goals in last 10
# goals scored by home (if < 10 goals total then the proportion for the game);
# (6) awayLast10 - proportion of goals in last 10 goals scored by away (if < 10
# goals total then the proportion for the game); (7) adjScoreDiff - an adjusted
# score difference relative to the seconds remaining; (8) secondsRem - seconds 
# remaining in the match; (9) homeWin - e value for outcome where 1 is a home
# win and -1 is not, a 0 is a draw
#
# Glicko rating variables include upper and lower bounds for each team, which
# equate to a 95% confidence interval in the teams rating (2 * rating deviation).
# The difference in Glicko rating between the teams is also included, with +ve
# and -ve values reflecting a better vs. worse home team rating. The single team
# rating value is also included.

##### TODO: add variables:
    ##### - next centre pass
    ##### - team ratings (adding now...)
    ##### - lineup info?
    ##### - others...?
    ##### - round (adding now..)
        ##### >>> theoretically could put weighting on the ratings (i.e. earlier vs. later rounds)
    
# An idea for adding extra variables could be to see whether added context helps
# the model, much like is done in the Sloan conference NFL paper...

##### TODO: consider whether < 10 shots for the last10 variables is appropriate...

#Get the unique list of match ID's
matchIdList = df_scoreFlow['matchId'].unique()

#Set a dictionary to store data into
scoringData = {'matchId': [], 'homeSquadId': [], 'awaySquadId': [],
               'homeSquadGlicko': [], 'awaySquadGlicko': [],
               'homeSquadGlickoUB': [], 'homeSquadGlickoLB': [],
               'awaySquadGlickoUB': [], 'awaySquadGlickoLB': [],
               'diffGlickoRating': [], 'roundNo': [],
               'scoreDiff': [], 'currRun': [],
               'homeBiggestRun': [], 'awayBiggestRun': [],
               'homeLast10': [], 'awayLast10': [],
               'adjScoreDiff': [], 'secondsRem': [],
               'homeWin': []}

#Loop through matches
for mm in range(0,len(matchIdList)):
    
    #Set current match ID to variable
    matchId = matchIdList[mm]
    matchInd = matchInfo['id'].index(matchId)
        
    #Identify the two squad ID's for the current match
    homeSquad = matchInfo['homeSquadId'][matchInd]
    awaySquad = matchInfo['awaySquadId'][matchInd]
    
    #Extract and calculate Glicko rating variables for current match
    
    #Get the match competition, year and round
    currComp = matchInfo['competition'][matchInd]
    currYear = matchInfo['year'][matchInd]
    currRound = matchInfo['roundNo'][matchInd]
    
    #Extract the data from the glicko2 ratings dataframe
    homeSquadRating = df_glicko2Ratings.loc[(df_glicko2Ratings['teamId'] == homeSquad) &
                                            (df_glicko2Ratings['competition'] == currComp) & 
                                            (df_glicko2Ratings['year'] == currYear) & 
                                            (df_glicko2Ratings['round'] == currRound),['glicko2Rating','glicko2Deviation']].reset_index()
    awaySquadRating = df_glicko2Ratings.loc[(df_glicko2Ratings['teamId'] == awaySquad) &
                                            (df_glicko2Ratings['competition'] == currComp) & 
                                            (df_glicko2Ratings['year'] == currYear) & 
                                            (df_glicko2Ratings['round'] == currRound),['glicko2Rating','glicko2Deviation']].reset_index()
    
    #Calculate variables to append at each score point
    homeSquadGlicko = homeSquadRating['glicko2Rating'][0]
    homeSquadGlickoUB = homeSquadRating['glicko2Rating'][0] + \
        (2*homeSquadRating['glicko2Deviation'][0])
    homeSquadGlickoLB = homeSquadRating['glicko2Rating'][0] - \
        (2*homeSquadRating['glicko2Deviation'][0])
    awaySquadGlicko = awaySquadRating['glicko2Rating'][0]
    awaySquadGlickoUB = awaySquadRating['glicko2Rating'][0] + \
        (2*homeSquadRating['glicko2Deviation'][0])
    awaySquadGlickoLB = awaySquadRating['glicko2Rating'][0] - \
        (2*homeSquadRating['glicko2Deviation'][0])
    diffGlickoRating = homeSquadGlicko - awaySquadGlicko
    
    #Extract the current matches score flow data
    df_currMatchScoreFlow = df_scoreFlow.loc[(df_scoreFlow['matchId'] == matchId) &
                                             (df_scoreFlow['scorePoints'] == 1),]
    df_currMatchScoreFlow.reset_index(inplace = True)
    
    #Check and see if the home team won the match
    if df_currMatchScoreFlow.loc[(df_currMatchScoreFlow['squadId'] == homeSquad),
                                 ['scorePoints']].sum()[0] > \
        df_currMatchScoreFlow.loc[(df_currMatchScoreFlow['squadId'] == awaySquad),
                                  ['scorePoints']].sum()[0]:
            homeWin = 1
    elif df_currMatchScoreFlow.loc[(df_currMatchScoreFlow['squadId'] == homeSquad),
                                 ['scorePoints']].sum()[0] < \
        df_currMatchScoreFlow.loc[(df_currMatchScoreFlow['squadId'] == awaySquad),
                                  ['scorePoints']].sum()[0]:
            homeWin = -1
    else:
        homeWin = 0
    
    #Loop through scores and calculate data
    for ss in range(0,len(df_currMatchScoreFlow)):
        
        #Set general variables for current score
        scoringData['matchId'].append(matchId)
        scoringData['homeSquadId'].append(homeSquad)
        scoringData['awaySquadId'].append(awaySquad)
        scoringData['homeWin'].append(homeWin)
        scoringData['roundNo'].append(currRound)
        
        #Set general glicko variables for current score
        scoringData['homeSquadGlicko'].append(homeSquadGlicko)
        scoringData['awaySquadGlicko'].append(awaySquadGlicko)
        scoringData['homeSquadGlickoUB'].append(homeSquadGlickoUB)
        scoringData['homeSquadGlickoLB'].append(homeSquadGlickoLB)
        scoringData['awaySquadGlickoUB'].append(awaySquadGlickoUB)
        scoringData['awaySquadGlickoLB'].append(awaySquadGlickoLB)
        scoringData['diffGlickoRating'].append(diffGlickoRating)
        
        #Special case for the first score of each match
        if ss == 0:
            
            #Check to see who got the first score
            if df_currMatchScoreFlow['squadId'][ss] == homeSquad:
                
                #Set the score differential to +1 for the home squad
                scoringData['scoreDiff'].append(1)
                
                #Set the current run for the home team
                scoringData['currRun'].append(1)
                
                #Set the home and away biggest run
                scoringData['homeBiggestRun'].append(1)
                scoringData['awayBiggestRun'].append(0)
                
                #Set the last 10 variable data
                scoringData['homeLast10'].append(1.0)
                scoringData['awayLast10'].append(0.0)
                
            else:
                
                #Set the score differential to -1 for the home squad
                scoringData['scoreDiff'].append(-1)
                
                #Set the current run for the away team
                scoringData['currRun'].append(-1)
                
                #Set the home and away biggest run
                scoringData['homeBiggestRun'].append(0)
                scoringData['awayBiggestRun'].append(1)
                
                #Set the last 10 variable data
                scoringData['homeLast10'].append(0.0)
                scoringData['awayLast10'].append(1.0)
                
            #Set the adjusted and absolute seconds remaining (i.e. match seconds - score seconds)
            remSecs = sum(matchInfo['periodSeconds'][matchInd]) - df_currMatchScoreFlow['matchSeconds'][ss]
            #Check for negative seconds and replace (might occur with scores on end game)
            if remSecs < 0:
                remSecs = 0
            scoringData['secondsRem'].append(remSecs)
            #Get current score diff for adjusted value
            currScore = scoringData['scoreDiff'][len(scoringData['scoreDiff'])-1]
            scoringData['adjScoreDiff'].append(currScore / math.sqrt(remSecs + 1))
              
        else:
            
            #Get the current score
            currScore = scoringData['scoreDiff'][len(scoringData['scoreDiff'])-1]
            
            #Get the current run
            currRun = scoringData['currRun'][len(scoringData['currRun'])-1]
            
            #Check to see who got the current score
            if df_currMatchScoreFlow['squadId'][ss] == homeSquad:
                
                #Add a point to the score diff
                scoringData['scoreDiff'].append(currScore+1)
                
                #Check if the current run is positive and add to it if so
                #If negative reset back to +1
                if currRun > 0:
                    scoringData['currRun'].append(currRun+1)
                else:
                    scoringData['currRun'].append(1)
                
            else:
                
                #Take a point to the score diff
                scoringData['scoreDiff'].append(currScore-1)
                
                #Check if the current run is negative and take from it if so
                #If positive reset back to -1
                if currRun < 0:
                    scoringData['currRun'].append(currRun-1)
                else:
                    scoringData['currRun'].append(-1)
                
            #Set the home and away biggest run
            #Find the largest and smallest run in the dataset
            #Also check whether the team has had a run
            homeMax = max(scoringData['currRun'])
            awayMax = min(scoringData['currRun'])
            if homeMax > 0:
                scoringData['homeBiggestRun'].append(homeMax)
            else:
                scoringData['homeBiggestRun'].append(0)
            if awayMax < 0:
                scoringData['awayBiggestRun'].append(awayMax)
            else:
                scoringData['awayBiggestRun'].append(0)
            
            #Set the last 10 variable data
            if ss < 9:
                #Get all the current scores up to now
                df_lastRun = df_currMatchScoreFlow.iloc[0:ss+1]
                scoringData['homeLast10'].append(len(df_lastRun.loc[(df_lastRun['squadId'] == homeSquad),
                                                                    'squadId']) / (ss+1))
                scoringData['awayLast10'].append(len(df_lastRun.loc[(df_lastRun['squadId'] == awaySquad),
                                                                    'squadId']) / (ss+1))
            else:
                #Get the last 10
                df_lastRun = df_currMatchScoreFlow.iloc[ss-9:ss+1]
                scoringData['homeLast10'].append(len(df_lastRun.loc[(df_lastRun['squadId'] == homeSquad),
                                                                    'squadId']) / 10)
                scoringData['awayLast10'].append(len(df_lastRun.loc[(df_lastRun['squadId'] == awaySquad),
                                                                    'squadId']) / 10)
            
            #Set the adjusted and absolute seconds remaining (i.e. match seconds - score seconds)
            remSecs = sum(matchInfo['periodSeconds'][matchInd]) - df_currMatchScoreFlow['matchSeconds'][ss]
            #Check for negative seconds and replace (might occur with scores on end game)
            if remSecs < 0:
                remSecs = 0
            scoringData['secondsRem'].append(remSecs)
            #Get current score diff for adjusted value
            currScore = scoringData['scoreDiff'][len(scoringData['scoreDiff'])-1]
            scoringData['adjScoreDiff'].append(currScore / math.sqrt(remSecs + 1))


#Convert to dataframe
df_scoringData = pd.DataFrame.from_dict(scoringData)

# %% Train random forest model

#Set random seed to ensure reproducible runs
rSeed = 123
random.seed(rSeed)

#Set a 70:30 split of the match ID's for training and test datasets
#Calculate number of matches for training set
nTrainingMatches = round(len(matchIdList)*0.7)
trainMatchIdList = random.sample(list(matchIdList),nTrainingMatches)
testMatchIdList = list(np.setdiff1d(list(matchIdList),trainMatchIdList))

#Get the data for the model

#First we'll take out any draws in the dataset for simplicity, and relable home
#wins as 1 and losses as zero
df_modelData = df_scoringData.loc[(df_scoringData['homeWin'].isin([-1,1])),]

#Extract the training & test data based on the match list
train = df_modelData.loc[(df_modelData['matchId'].isin(trainMatchIdList)),]
test = df_modelData.loc[(df_modelData['matchId'].isin(testMatchIdList)),]
train.reset_index(inplace = True, drop = True)
test.reset_index(inplace = True, drop = True)

#Get the labels for the training and test datasets
#First replace the home win variable as 1 and 0 for win/loss
train['homeWin'].replace(to_replace = -1, value = 0, inplace = True)
test['homeWin'].replace(to_replace = -1, value = 0, inplace = True)
#Extract the labels for the two datasets
trainLabels = np.array(train.pop('homeWin'))
testLabels = np.array(test.pop('homeWin'))

#Drop the columns we don't want from the datasets
train.drop(['matchId', 'homeSquadId', 'awaySquadId'],
           axis = 1, inplace = True)
test.drop(['matchId', 'homeSquadId', 'awaySquadId'],
          axis = 1, inplace = True)

#Create the random forest model with 100 trees
##### TODO: adjust hyperparameters...
rfModel = RandomForestClassifier(n_estimators = 100,
                                 bootstrap = True,
                                 class_weight = None,
                                 criterion = 'gini',
                                 max_depth = None,
                                 max_leaf_nodes = None,
                                 random_state = rSeed, 
                                 max_features = 'sqrt',
                                 n_jobs = -1, verbose = 1)

#Fit the model on the training data
rfModel.fit(train, trainLabels)

#Print some details about forest
n_nodes = []
max_depths = []
for ind_tree in rfModel.estimators_:
    n_nodes.append(ind_tree.tree_.node_count)
    max_depths.append(ind_tree.tree_.max_depth)  
print(f'Average number of nodes {int(np.mean(n_nodes))}')
print(f'Average maximum depth {int(np.mean(max_depths))}')

# %% Check random forest results

#Define the function to evaluate the model against a 'baseline' performance using
#ROC curve analysis
##### TODO: move to separate function...
def evaluateModel(predictions, probs, train_predictions, train_probs):
    
    baseline = {}
    
    baseline['recall'] = recall_score(testLabels, [1 for _ in range(len(testLabels))])
    baseline['precision'] = precision_score(testLabels, [1 for _ in range(len(testLabels))])
    baseline['roc'] = 0.5
    
    results = {}
    
    results['recall'] = recall_score(testLabels, predictions)
    results['precision'] = precision_score(testLabels, predictions)
    results['roc'] = roc_auc_score(testLabels, probs)
    
    train_results = {}
    train_results['recall'] = recall_score(trainLabels, train_predictions)
    train_results['precision'] = precision_score(trainLabels, train_predictions)
    train_results['roc'] = roc_auc_score(trainLabels, train_probs)
    
    for metric in ['recall', 'precision', 'roc']:
        print(f'{metric.capitalize()} Baseline: {round(baseline[metric], 2)} Test: {round(results[metric], 2)} Train: {round(train_results[metric], 2)}')
    
    # Calculate false positive rates and true positive rates
    base_fpr, base_tpr, _ = roc_curve(testLabels, [1 for _ in range(len(testLabels))])
    model_fpr, model_tpr, _ = roc_curve(testLabels, probs)

    plt.figure(figsize = (8, 6))
    plt.rcParams['font.size'] = 16
    
    # Plot both curves
    plt.plot(base_fpr, base_tpr, 'b', label = 'baseline')
    plt.plot(model_fpr, model_tpr, 'r', label = 'model')
    plt.legend();
    plt.xlabel('False Positive Rate'); plt.ylabel('True Positive Rate'); plt.title('ROC Curves');

#Define the function to visualise the confusion matrix
##### TODO: move to separate function...
def plotConfusionMatrix(cm, classes,
                        normalize = False,
                        title='Confusion matrix',
                        cmap = plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    Source: http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html
    """
    
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.figure(figsize = (10, 10))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title, size = 24)
    plt.colorbar(aspect=4)
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45, size = 14)
    plt.yticks(tick_marks, classes, size = 14)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    
    # Labeling the plot
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt), fontsize = 20,
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
        
    plt.grid(None)
    plt.tight_layout()
    plt.ylabel('True label', size = 18)
    plt.xlabel('Predicted label', size = 18)

#Get the random forest training predictions and probability
rfTrainPredictions = rfModel.predict(train)
rfTrainProbs = rfModel.predict_proba(train)[:, 1]

#Get the random forest test predictions and probability
rfTestPredictions = rfModel.predict(test)
rfTestProbs = rfModel.predict_proba(test)[:, 1]

#Evaluate the model using ROC curve analysis
evaluateModel(rfTestPredictions, rfTestPredictions,
              rfTrainPredictions, rfTrainProbs)

##### Addition of team ratings makes model do alright --- ROC of 0.79

#Create the confusion matrix
confMat = confusion_matrix(testLabels, rfTestPredictions)
plotConfusionMatrix(confMat, classes = ['Loss', 'Win'], normalize = True,
                    title = 'Match Outcome Confusion Matrix')

#### Given errors in runs, model still does fine without them when tested...

##### Confusion matrix looks OK, but given we expect our win/loss prediction 
##### to actually be wrong sometimes (i.e. with in-game probability), not sure
##### how 'good' this needs to be???

#Check feature importance
featureImportance = pd.DataFrame({'feature': list(train.columns),
                                  'importance': rfModel.feature_importances_}).\
                                   sort_values('importance', ascending = False)
featureImportance

# %% Optimise hyperparameters through random search

##### TODO: add this to actual model...

# %% Check predicted probabilities against actual results

# This check puts the predicted probabilities into 5% bins and then checks how
# what ratio of samples within the bins actually results in a win. Theoretically,
# the bin which contains predicted probabilities of 45-50% should have the same
# or a similar proportion of win labels (i.e. 45-50%)

#Set variables that will serve as the data for XY plot
avgPredProb = list()
actualProb = list()

#Set the ranges to bin the probabilities
probBins = np.linspace(0,1,21)

#Loop through the probability bins and calculate values
for pp in range(0,len(probBins)-1):
    
    #Get the indices of values that meet the current criteria
    valInds = np.where(np.logical_and(rfTestProbs > probBins[pp],
                                      rfTestProbs <= probBins[pp+1]))
        
    #Get the probability values and average, append to list
    avgPredProb.append(np.mean(rfTestProbs[valInds[0]]))
    
    #Extract the win/loss variable from the test set based on the indices
    binWins = testLabels[valInds[0]]
    
    #Calculate the rate of wins in the current bin relative to the total, append to list
    actualProb.append(np.count_nonzero(binWins == 1) / len(binWins))
    
#Plot the probability bins (x-axis) vs. the actual probabilities in the data (y-axis)
fig = plt.figure()
plt.scatter(np.array(avgPredProb), np.array(actualProb), color='k')
#Set axes limits
plt.xlim(0,1)
plt.ylim(0,1)
#Plot line of equality
plt.plot([0,1], [0,1], 'k--', alpha = 0.75, zorder = 0)
#Set labels
plt.xlabel('Average Predicted Win Probability',{'fontSize': 14})
plt.ylabel('Actual Proportion of Games Won', {'fontSize': 14})
plt.title('Test Data Binned to 5% Probability Intervals', {'fontSize': 16})
fig.tight_layout()

##### Whole model is not too bad, seems to overestimate probability at lower values
##### but underestimate probability at higher values. For example, when on average
##### it predicts win probability at ~10%, the actual win probability is at 30%.
##### In comparison, when predicting probability at ~90%, the actual win probability
##### is at ~70%

##### The addition of team ratings, even at their most basic makes the model fairly
##### accurate in its predictions...

##### Hyperparameter tuning may be a good option:
    ##### https://towardsdatascience.com/hyperparameter-tuning-the-random-forest-in-python-using-scikit-learn-28d2aa77dd74


# %% Test plot of win probability across a match

#Extract samples from a match ID
#Grab the first match from the test probability set
sampleMatchId = testMatchIdList[0]

#Figure out which match this is
df_sampleMatch = df_matchInfo.loc[(df_matchInfo['id'] == sampleMatchId),]

##### This looks like a somewhat imbalanced match between the Magic and Steel
##### (i.e. a 7 goal win to the Magic [home team]). Given it is round 2 though,
##### both teams had an identical glicko2 rating given they both won their first
##### games 

#Check the score flow for this match
df_sampleScoringData = df_scoringData.loc[(df_scoringData['matchId'] == sampleMatchId),]

##### The Steel get out to a bit of a lead early on in the match, but then the Magic
##### take over, holding the lead and pushing it out towards the end of the match

#Figure out which rows in the test probabilities correspond to this match
testMatchIdVals = df_modelData.loc[(df_modelData['matchId'].isin(testMatchIdList)),
                                   ['matchId']]
testMatchIdVals.reset_index(inplace = True)
idMask = testMatchIdVals['matchId'] == sampleMatchId

#Extract the model test probabilities for the current match based on the mask
#This assumes they are in progressive order in the array, which they should be...
sampleMatchProbs = rfTestProbs[idMask]

#Plot probability (< 50% = away probability favour)
fig = plt.figure()
plt.plot(sampleMatchProbs)

##### The first probabiliyt value seems off for what this game set-up was, the
##### second value seems like where it should start. The model seems to do what 
##### it should, albeit it is a bit too reactive to the initial scoreline (i.e.
##### the Steel got up a bit early, and the Magic's probability was shifted quite
##### low --- although this could be common for netball). Still, it is reactive in
##### certain places jumping from 80% to 40% seemingly from one goal --- this could
##### be due to the model including factors that aren't that contextual to the current
##### game time (i.e. the Steel's best run in this instance was high from early, but
##### this should hold less weight in the later match situation). 

# %% Test another plot

#Extract samples from a match ID
#Grab the first match from the test probability set
sampleMatchId = testMatchIdList[123]

#Figure out which match this is
df_sampleMatch = df_matchInfo.loc[(df_matchInfo['id'] == sampleMatchId),]

##### This looks like a close match (3 goal home win) between NSW Swifts and
##### Adelaide thunderbirds. The home teams rating is a fair bit higher than
##### the away team here - so should start off somewhat imbalanced.

#Check the score flow for this match
df_sampleScoringData = df_scoringData.loc[(df_scoringData['matchId'] == sampleMatchId),]

##### The Steel get out to a bit of a lead early on in the match, but then the Magic
##### take over, holding the lead and pushing it out towards the end of the match

#Figure out which rows in the test probabilities correspond to this match
testMatchIdVals = df_modelData.loc[(df_modelData['matchId'].isin(testMatchIdList)),
                                   ['matchId']]
testMatchIdVals.reset_index(inplace = True)
idMask = testMatchIdVals['matchId'] == sampleMatchId

#Extract the model test probabilities for the current match based on the mask
#This assumes they are in progressive order in the array, which they should be...
sampleMatchProbs = rfTestProbs[idMask]

#Plot probability (< 50% = away probability favour)
fig = plt.figure()
plt.plot(sampleMatchProbs)

##### The team ratings seem to be taking over in this instance, while despite the
##### match being close --- the lowly ranked away team is never given a chance. This
##### could be accurate, but also doesn't seem to fit right with the close nature of
##### netball and games turning quickly. It could also be the fact that there are a few
##### variables relating to team rating that could skew model

# %%

##### TODO: There are a few key issues to iron out