# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 09:44:24 2021

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    This script runs some basic analyses to examine how well coaches have performed
    over the ANZC and SSN era.
    
    Some notable limitations at the moment:
        - Done on a seasonal basis, so if there were swaps or a coach missed a
          game then this wouldn't be accounted for
    
"""

# %% Import packages

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#Set plot parameters
from matplotlib import rcParams
# rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = 'Arial'
rcParams['font.weight'] = 'bold'
rcParams['axes.labelsize'] = 12
rcParams['axes.titlesize'] = 16
rcParams['axes.linewidth'] = 1.5
rcParams['hatch.linewidth'] = 1.5
rcParams['axes.labelweight'] = 'bold'
rcParams['legend.fontsize'] = 10
rcParams['xtick.major.width'] = 1.5
rcParams['ytick.major.width'] = 1.5
rcParams['legend.framealpha'] = 0.0
rcParams['savefig.dpi'] = 300
rcParams['savefig.format'] = 'pdf'

#Set team colour palettes
colourDict = {'Fever': '#00953b',
              'Firebirds': '#4b2c69',
              'Giants': '#f57921',
              'Lightning': '#fdb61c',
              'Magpies': '#494b4a',
              'Swifts': '#0082cd',
              'Thunderbirds': '#e54078',
              'Vixens': '#00a68e',
              'Magic': '#000000',
              'Mystics': '#0000cd',
              'Pulse': '#ffff00',
              'Steel': '#00b7eb',
              'Tactix': '#ee161f'}

# %% Set-up 

#Navigate to data directory
os.chdir('..\\..\\..\\Data\\Coaching_ANZC-SSN')

#Load datasets
df_coach = pd.read_csv('coachSummaries.csv')
df_premiership = pd.read_csv('premiershipSummaries.csv')
df_results = pd.read_csv('seasonWinLossSummaries.csv')

# %% Analyse coach records

#Get unique list of coaches
coachList = list(df_coach['coach'].unique())

#Loop through result records and attach the appropriate coach
attachCoach = []
for rr in range(len(df_results)):
    
    #Get the team and year for the current record
    team = df_results['team'][rr]
    year = df_results['year'][rr]
    
    #Find the coach for the team and year combination
    coach = df_coach.loc[(df_coach['team'] == team) &
                         (df_coach['year'] == year),]['coach'].to_list()[0]
    
    #Append to list
    attachCoach.append(coach)
    
#Append created list to dataframe
df_results['coach'] = attachCoach

#Create dictionary to store summary results
coachResults ={'coach': [],
               'totalPlayed': [], 'totalWin': [], 'totalDraw': [], 'totalLoss': [],
               'regularPlayed': [], 'regularWin': [], 'regularDraw': [], 'regularLoss': [],
               'finalsPlayed': [], 'finalsWin': [], 'finalsLoss': [],
               'GF': [], 'GA': [], 'Gdiff': [], 'yearsCoached': [],
               'premierships': [], 'runnersUp': [], 'minorPremierships': []}

#Loop through coaches and calculate records
for coach in coachList:
    
    #Append coach to distionary
    coachResults['coach'].append(coach)
    
    #Extract the years where the current coach was active
    df_currCoach = df_results.loc[df_results['coach'] == coach].reset_index(drop = True)
    
    #Add up all records
    #Played
    coachResults['totalPlayed'].append(np.sum(df_currCoach['played']) + np.sum(df_currCoach['finalsWin']) + np.sum(df_currCoach['finalsLoss']))
    coachResults['regularPlayed'].append(np.sum(df_currCoach['played']))
    coachResults['finalsPlayed'].append(np.sum(df_currCoach['finalsWin']) + np.sum(df_currCoach['finalsLoss']))
    #Wins
    coachResults['totalWin'].append(np.sum(df_currCoach['win']) + np.sum(df_currCoach['finalsWin']))
    coachResults['regularWin'].append(np.sum(df_currCoach['win']))
    coachResults['finalsWin'].append(np.sum(df_currCoach['finalsWin']))
    #Draws (same for both)
    coachResults['totalDraw'].append(np.sum(df_currCoach['draw']))
    coachResults['regularDraw'].append(np.sum(df_currCoach['draw']))
    #Losses
    coachResults['totalLoss'].append(np.sum(df_currCoach['loss']) + np.sum(df_currCoach['finalsLoss']))
    coachResults['regularLoss'].append(np.sum(df_currCoach['loss']))
    coachResults['finalsLoss'].append(np.sum(df_currCoach['finalsLoss']))
    #Goals
    coachResults['GF'].append(np.sum(df_currCoach['GF']))
    coachResults['GA'].append(np.sum(df_currCoach['GA']))
    coachResults['Gdiff'].append(np.sum(df_currCoach['Gdiff']))
    #Years coached
    coachResults['yearsCoached'].append(len(df_currCoach))
    
    #Check if any premierships, runners up or minor premierships
    #Set counters
    premierships = 0
    runnersUp = 0
    minorPremierships = 0
    for ii in range(len(df_currCoach)):
        
        #Set current year and team
        year = df_currCoach['year'][ii]
        team = df_currCoach['team'][ii]
        
        #Get results
        p = len(df_premiership.loc[(df_premiership['year'] == year) &
                                   (df_premiership['premiers'] == team),])
        r = len(df_premiership.loc[(df_premiership['year'] == year) &
                                   (df_premiership['runnerUp'] == team),])
        m = len(df_premiership.loc[(df_premiership['year'] == year) &
                                   (df_premiership['minorPremiers'] == team),])
        
        #Add to counters
        premierships += p
        runnersUp += r
        minorPremierships += m
        
    #Append to dictionary
    coachResults['premierships'].append(premierships)
    coachResults['runnersUp'].append(runnersUp)
    coachResults['minorPremierships'].append(minorPremierships)
    
#Convert to dataframe
df_coachResults = pd.DataFrame.from_dict(coachResults)

#Calculate win percentages
df_coachResults['totalWinPer'] = df_coachResults['totalWin'] / df_coachResults['totalPlayed'] * 100
df_coachResults['regularWinPer'] = df_coachResults['regularWin'] / df_coachResults['regularPlayed'] * 100
df_coachResults['finalsWinPer'] = df_coachResults['finalsWin'] / df_coachResults['finalsPlayed'] * 100

# %% Visualise win percentage

#Create bar figure for ranked win percentage
fig, ax = plt.subplots(figsize = (7,9))

#Condense win percentage and coach names into own dataframe
df_winPer = pd.DataFrame(list(zip(df_coachResults['coach'],
                                  df_coachResults['totalWinPer'])),
                         columns =['coach', 'winPer'])
        
#Plot the bar chart
sns.barplot(x = 'winPer', y = 'coach',
            data = df_winPer,
            order = df_winPer.sort_values('winPer', ascending = False)['coach'].values.flatten(),
            ax = ax)

#Make each bar blue vs. orange for above vs. below average
for patch in ax.patches:

    #Check value and allocate colour
    if patch.get_width() >= 50:
        patch.set_facecolor('#003399')
    else:
        patch.set_facecolor('#cc5200')
        
#Set x-limits to 0-100
ax.set_xlim([0,100])

#Add gridlines at each 20 percent interval
for vv in [20,40,60,80]:
    plt.axvline(x = vv, lw = 1, ls = '--', c = '#d3d3d3', zorder = 0)
    
#Set labels
ax.set_xlabel('Total Coaching Win Percentage (%)')
ax.set_ylabel('')

#Tight layout
plt.tight_layout()

#Set figure colouring
fig.patch.set_facecolor('#fffaf0')
ax.set_facecolor('#fffaf0')

#Add text displaying percentage and number of games
for pp in range(len(ax.patches)):
    
    #Get the current coach
    coach = ax.get_yticklabels()[pp].get_text()
    
    #Get their percentage and number of games
    winPer = ax.patches[pp].get_width()
    nGames = int(df_coachResults.loc[df_coachResults['coach'] == coach,
                                     ['totalPlayed']].to_numpy().flatten()[0])
    
    #Add text next to bar
    ax.text(ax.patches[pp].get_width() + 1,
            ax.patches[pp].get_y() + (ax.patches[pp].get_height() / 2),
            f'{np.round(winPer,2)}% / {nGames} games',
            va = 'center', ha = 'left',
            fontsize = 8, fontweight = 'bold')

# #### TODO: save figure
# plt.savefig('coachWinPer.png', format = 'png', 
#             facecolor = fig.get_facecolor(), edgecolor = 'none',
#             dpi = 300)

# plt.close()

# %% Visualise average win percentage each year

#Add win percentage each year to the results dataframe
df_results['winPer'] = (df_results['win'] + df_results['finalsWin'].replace(np.nan, 0)) / (df_results['played'] + df_results['finalsWin'].replace(np.nan, 0) + df_results['finalsLoss'].replace(np.nan, 0)) * 100

#Create figure
fig, ax = plt.subplots(figsize = (7,9))

#Create mean & sd point plot    
sns.pointplot(x = 'winPer', y = 'coach', data = df_results,
              join = False, ci = 'sd',
              capsize = 0.25,
              order = df_winPer.sort_values('winPer', ascending = False)['coach'].values.flatten(),
              ax = ax)

#Make each blue vs. orange for above vs. below average
#Set colour list for points
pointColours = []
for pp in range(len(ax.collections[0].get_offsets().data)):
    
    #Check value and allocate colour
    if ax.collections[0].get_offsets().data[pp][0] >= 50:
        pointColours.append('#003399')
    else:
        pointColours.append('#cc5200')
#Set point face and edge colours
ax.collections[0].set_facecolor(pointColours)
ax.collections[0].set_edgecolor(pointColours)

#Colour the lines
#There are 3 for every point
for pp in range(len(ax.collections[0].get_offsets().data)):
    ax.lines[pp*3].set_color(pointColours[pp])
    ax.lines[pp*3+1].set_color(pointColours[pp])
    ax.lines[pp*3+2].set_color(pointColours[pp])
    
#Add individual points
sns.stripplot(x = 'winPer', y = 'coach', data = df_results,
              size = 3, color = 'grey', dodge = False, jitter = False,
              order = df_winPer.sort_values('winPer', ascending = False)['coach'].values.flatten(),
              ax = ax)
    
#Set x-limits to 0-100
ax.set_xlim([-2,100])

#Add gridlines at each 20 percent interval
for vv in [20,40,60,80]:
    plt.axvline(x = vv, lw = 1, ls = '--', c = '#d3d3d3', zorder = 0)
    
#Set labels
ax.set_xlabel('Average Win Percentage (%) per Season')
ax.set_ylabel('')

#Tight layout
plt.tight_layout()

#Set figure colouring
fig.patch.set_facecolor('#fffaf0')
ax.set_facecolor('#fffaf0')

#### TODO: save figure
# plt.savefig('coachWinPer.png', format = 'png', 
#             facecolor = fig.get_facecolor(), edgecolor = 'none',
#             dpi = 300)

# plt.close()

# %% Plot a selection of coach results across years

#Set coaches to plot
plotCoaches = ['Noeline Taurua',
               'Simone McKinnis',
               'Roselee Jencke',
               'Julie Fitzgerald',
               'Jane Woodlands-Thompson',
               'Stacey Marinkovich']

#Create figure to plot on
fig, ax = plt.subplots(figsize = (12,7), nrows = 2, ncols = 3,
                       sharex = True, sharey = True)

#Set axes to plot on
whichAx = [[0,0], [0,1], [0,2],
           [1,0], [1,1], [1,2]]

#Set common x and y limits
ax[0,0].set_xlim([2007,2022])
ax[0,0].set_ylim([0,105])

#Loop through coaches and plot data
for cc in range(len(plotCoaches)):
    
    #Extract yearly data for coach
    df_currCoach = df_results.loc[df_results['coach'] == plotCoaches[cc],].reset_index(drop = True)
    
    #Get years coached
    year = df_currCoach.sort_values('year', ascending = True)['year'].values
    
    #Get teams coached
    team = df_currCoach.sort_values('year', ascending = True)['team'].values
    
    #Get win percentage for the year
    winPer = df_currCoach.sort_values('year', ascending = True)['winPer'].values
    
    #Get colours based on team
    setColours = []
    for tt in range(len(team)):
        setColours.append(colourDict[team[tt]])
    
    #Plot the data as a bar chart
    ax[whichAx[cc][0],whichAx[cc][1]].bar(year, winPer,
                                          color = setColours)
    
    #Make bars skinny
    #Add lollipop point too
    newWidth = 0.25
    for pp in range(len(ax[whichAx[cc][0],whichAx[cc][1]].patches)):
        #Collect details
        currWidth = ax[whichAx[cc][0],whichAx[cc][1]].patches[pp].get_width()
        diff = currWidth - newWidth
        #Set width
        ax[whichAx[cc][0],whichAx[cc][1]].patches[pp].set_width(newWidth)
        #Recentre bar
        ax[whichAx[cc][0],whichAx[cc][1]].patches[pp].set_x(ax[whichAx[cc][0],whichAx[cc][1]].patches[pp].get_x() + (diff * .5))
        #Add lollipop point
        #Get the x,y coordinate to plot
        xPt,yPt = ax[whichAx[cc][0],whichAx[cc][1]].patches[pp].get_x(),ax[whichAx[cc][0],whichAx[cc][1]].patches[pp].get_height()
        #Plot the point
        ax[whichAx[cc][0],whichAx[cc][1]].scatter(xPt+(newWidth/2), yPt,
                                                  color = setColours[pp],
                                                  s = 75, zorder = 4)
        
    #Clean up axes border lines
    ax[whichAx[cc][0],whichAx[cc][1]].set_ylabel('')
    ax[whichAx[cc][0],whichAx[cc][1]].set_xlabel('')
    ax[whichAx[cc][0],whichAx[cc][1]].spines['top'].set_visible(False)
    ax[whichAx[cc][0],whichAx[cc][1]].spines['left'].set_visible(False)
    ax[whichAx[cc][0],whichAx[cc][1]].spines['right'].set_visible(False)
    
    #Add gridlines at each 20 percent interval
    for vv in [20,40,60,80,100]:
        ax[whichAx[cc][0],whichAx[cc][1]].axhline(y = vv, lw = 1, ls = '--', c = '#d3d3d3', zorder = 0)
        
    #Shorten y-axis ticks to nothing
    ax[whichAx[cc][0],whichAx[cc][1]].tick_params(axis = 'y',
                                                  which = 'both',
                                                  length = 0)
    
    #Add plot title
    ax[whichAx[cc][0],whichAx[cc][1]].set_title(plotCoaches[cc],
                                                fontsize = 12, fontweight = 'bold',
                                                pad = 7)

#Fix up x-ticks
ax[whichAx[-1][0],whichAx[-1][1]].set_xticks(np.linspace(2008,2021,14).astype(int))
for cc in range(len(plotCoaches)):
    #Add labels
    ax[whichAx[cc][0],whichAx[cc][1]].set_xticklabels(labels = ax[whichAx[-1][0],whichAx[-1][1]].get_xticklabels(),
                                                      rotation = 45)
    #Ensure visibility
    ax[whichAx[cc][0],whichAx[cc][1]].xaxis.set_tick_params(which = 'both', labelbottom = True)    
    #Set face colour here too
    ax[whichAx[cc][0],whichAx[cc][1]].set_facecolor('#fffaf0')
    
#Tight layout
plt.tight_layout()

#Set figure colouring
fig.patch.set_facecolor('#fffaf0')

#### TODO: save figure
# plt.savefig('coachWinPer_yearly.png', format = 'png', 
#             facecolor = fig.get_facecolor(), edgecolor = 'none',
#             dpi = 300)

# plt.close()

