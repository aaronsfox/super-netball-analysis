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
##### Can add other things here too though...e.g. team ratings...
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
for ff in range(574,len(jsonFileList)):
    
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
# remaining in the match; (9) homeWin - labl value for outcome where 1 is a home
# win and -1 is not, a 0 is a draw

##### TODO: add variables:
    ##### - next centre pass
    ##### - team ratings
    ##### - lineup info?
    ##### - others...?
    
# An idea for adding extra variables could be to see whether added context helps
# the model, much like is done in the Sloan conference NFL paper...

##### TODO: consider whether < 10 shots for the last10 variables is appropriate...

#Get the unique list of match ID's
matchIdList = df_scoreFlow['matchId'].unique()

#Set a dictionary to store data into
scoringData = {'matchId': [], 'homeSquadId': [], 'awaySquadId': [],
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
    
    #Extract the current matches score flow data
    df_currMatchScoreFlow = df_scoreFlow.loc[(df_scoreFlow['matchId'] == matchId),]
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

#First we'll take out any draws in the dataset for simplicity, and relable home
#wins as 1 and losses as zero
df_modelData = df_scoringData.loc[(df_scoringData['homeWin'].isin([-1,1])),]

#Create a dataframe for the model with only the necessary variables
##### NOTE: this is where dataframes can be combined if needed

#Drop the columns we don't want
df_modelData.drop(['matchId', 'homeSquadId', 'awaySquadId'],
                  axis = 1, inplace = True)

#Replace the -1 for losses with zero
df_modelData['homeWin'].replace(to_replace = -1, value = 0, inplace = True)

#Extract the labels for the homeWin variable
labels = np.array(df_modelData.pop('homeWin'))

#Create the train test split for the model
#Currently at a 70:30 split
train, test, train_labels, test_labels = train_test_split(df_modelData,
                                                          labels, 
                                                          stratify = labels,
                                                          test_size = 0.3, 
                                                          random_state = rSeed)

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
rfModel.fit(train, train_labels)

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
    
    baseline['recall'] = recall_score(test_labels, [1 for _ in range(len(test_labels))])
    baseline['precision'] = precision_score(test_labels, [1 for _ in range(len(test_labels))])
    baseline['roc'] = 0.5
    
    results = {}
    
    results['recall'] = recall_score(test_labels, predictions)
    results['precision'] = precision_score(test_labels, predictions)
    results['roc'] = roc_auc_score(test_labels, probs)
    
    train_results = {}
    train_results['recall'] = recall_score(train_labels, train_predictions)
    train_results['precision'] = precision_score(train_labels, train_predictions)
    train_results['roc'] = roc_auc_score(train_labels, train_probs)
    
    for metric in ['recall', 'precision', 'roc']:
        print(f'{metric.capitalize()} Baseline: {round(baseline[metric], 2)} Test: {round(results[metric], 2)} Train: {round(train_results[metric], 2)}')
    
    # Calculate false positive rates and true positive rates
    base_fpr, base_tpr, _ = roc_curve(test_labels, [1 for _ in range(len(test_labels))])
    model_fpr, model_tpr, _ = roc_curve(test_labels, probs)

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

##### Somehow model got worse with more than 50 games of data!!!!!

#Create the confusion matrix
confMat = confusion_matrix(test_labels, rfTestPredictions)
plotConfusionMatrix(confMat, classes = ['Loss', 'Win'], normalize = True,
                    title = 'Match Outcome Confusion Matrix')

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
    binWins = test_labels[valInds[0]]
    
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

##### Hyperparameter tuning may be a good option:
    ##### https://towardsdatascience.com/hyperparameter-tuning-the-random-forest-in-python-using-scikit-learn-28d2aa77dd74


# %%