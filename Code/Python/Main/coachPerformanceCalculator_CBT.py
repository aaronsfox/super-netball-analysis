# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 12:54:44 2021

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    This looks at the basic numbers for coach records from CBT.
    
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

# %% Load dataset

#Go to directory
os.chdir('..\\..\\..\\Data\\Coaching_CBT')

#Load data
df_coachResults = pd.read_csv('coachRecords.csv')

# %% Run calculations

#Calculate win percentage
df_coachResults['winPer'] = df_coachResults['win'] / df_coachResults['played'] * 100

# %% Plot win percentage

#Create bar figure for ranked win percentage
fig, ax = plt.subplots(figsize = (7,9))

#Plot the bar chart
sns.barplot(x = 'winPer', y = 'coach',
            data = df_coachResults,
            order = df_coachResults.sort_values('winPer', ascending = False)['coach'].values.flatten(),
            ax = ax)

#Make each bar blue vs. orange for above vs. below average
for patch in ax.patches:

    #Check value and allocate colour
    if patch.get_width() >= 50:
        patch.set_facecolor('#003399')
    else:
        patch.set_facecolor('#cc5200')
        
#Set x-limits to 0-100
ax.set_xlim([0,105])

#Add gridlines at each 20 percent interval
for vv in [20,40,60,80,100]:
    plt.axvline(x = vv, lw = 1, ls = '--', c = '#d3d3d3', zorder = 0)
    
#Set labels
ax.set_xlabel('Total Coaching Win Percentage (%)')
ax.set_ylabel('')

#Add figure title
ax.set_title('Commonwealth Bank Trophy (1997 - 2007)',
             ha = 'center',
             fontsize = 13, fontweight = 'bold')

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
                                     ['played']].to_numpy().flatten()[0])
    
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