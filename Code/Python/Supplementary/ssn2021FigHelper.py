# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 20:29:59 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au

This helper script contains a series of functions that are used for
plotting figures from the Super Netball 2021 season data.

Currently pretty much identical to 2020 helper script.

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

# %% totalPointsOneVsTwo

def totalPointsOneVsTwo(round2Plot = None, matchInfo = None,
                        teamInfo = None, df_scoreFlow = None,
                        colourDict = None, bokehOptions = None,
                        showPlot = False, exportPNG = True,
                        exportHTML = True):
    
    # Function for plotting total team points from standard vs. super shots
    # in each game of the round
    #
    # Input:    round2Plot - integer of the round to take data from
    #           matchInfo - matchInfo dictionary pulled from data import
    #           teamInfo - teamInfo dictionary pulled from data import
    #           df_scoreFlow - datframe of score flow data pulled from data import
    #           colourDict - dictionary matching team nicknames to colour plots
    #           bokehOptions - dictionary dictating Bokeh figure options
    
    #Check inputs
    if round2Plot is None:
        raise ValueError('A round to plot data from is required.')
    
    if matchInfo is None or teamInfo is None:
        raise ValueError('Both the match info and team info dictionaries from data import are required.')
        
    if df_scoreFlow is None:
        raise ValueError('The score flow dataframe from data import is required.')
    
    if colourDict is None:
        #Use default colour scheme
        colourDict = {'Fever': '#00953b',
                      'Firebirds': '#4b2c69',
                      'GIANTS': '#f57921',
                      'Lightning': '#fdb61c',
                      'Magpies': '#494b4a',
                      'Swifts': '#0082cd',
                      'Thunderbirds': '#e54078',
                      'Vixens': '#00a68e'}
        
    if bokehOptions is None:
        #Use basic options
        bokehOptions = dict(tools = ['wheel_zoom,box_zoom'])
    
    #Set blank lists to fill with plots and source
    figPlot = list()
    figSource = list()
    
    #Loop through the four round matches
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
                                      (df_scoreFlow['roundNo'] == round2Plot) &
                                      (df_scoreFlow['scoreName'] == 'goal') & 
                                      (df_scoreFlow['squadId'] == teamId1),
                                      ['scorePoints']].sum()[0] + \
            df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                             (df_scoreFlow['roundNo'] == round2Plot) &
                             (df_scoreFlow['scoreName'] == '2pt Goal') & 
                             (df_scoreFlow['squadId'] == teamId1),
                             ['scorePoints']].sum()[0]
        team2Score = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                      (df_scoreFlow['roundNo'] == round2Plot) &
                                      (df_scoreFlow['scoreName'] == 'goal') & 
                                      (df_scoreFlow['squadId'] == teamId2),
                                      ['scorePoints']].sum()[0] + \
            df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                             (df_scoreFlow['roundNo'] == round2Plot) &
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
                                         (df_scoreFlow['roundNo'] == round2Plot) &
                                         (df_scoreFlow['scoreName'] == 'goal') & 
                                         (df_scoreFlow['squadId'] == teamId1),
                                         ['scorePoints']].sum()
        twoPointTeam1 = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                         (df_scoreFlow['roundNo'] == round2Plot) &
                                         (df_scoreFlow['scoreName'] == '2pt Goal') & 
                                         (df_scoreFlow['squadId'] == teamId1),
                                         ['scorePoints']].sum()
        
        #Team 2
        standardTeam2 = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                         (df_scoreFlow['roundNo'] == round2Plot) &
                                         (df_scoreFlow['scoreName'] == 'goal') & 
                                         (df_scoreFlow['squadId'] == teamId2),
                                         ['scorePoints']].sum()
        twoPointTeam2 = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                         (df_scoreFlow['roundNo'] == round2Plot) &
                                         (df_scoreFlow['scoreName'] == '2pt Goal') & 
                                         (df_scoreFlow['squadId'] == teamId2),
                                         ['scorePoints']].sum()
        
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
    
    #Show grid
    if showPlot is True:       
        show(grid)
    
    #Export grid as both .png and .html
    if exportPNG is True or exportHTML is True:
        
        #First, check if the directory exists and needs making
        if os.path.isdir('round'+str(round2Plot)+'-totalteampoints-onevstwo') is False:
            os.mkdir('round'+str(round2Plot)+'-totalteampoints-onevstwo')
            
        #Navigate to directory
        os.chdir('round'+str(round2Plot)+'-totalteampoints-onevstwo')
    
        #Check and export PNG if required
        if exportPNG is True:
            export_png(grid, filename = 'round'+str(round2Plot)+'-totalteampoints-onevstwo.png')
    
        #Check and export HTML if required
        if exportHTML is True:
            output_file('round'+str(round2Plot)+'-totalteampoints-onevstwo.html')
            save(grid)
    
        #Navigate back up to original directory
        os.chdir('..')
        
# %% quarterPointsOneVsTwo

def quarterPointsOneVsTwo(round2Plot = None, matchInfo = None,
                          teamInfo = None, df_scoreFlow = None,
                          colourDict = None, bokehOptions = None,
                          showPlot = False, exportPNG = True,
                          exportHTML = True):
    
    # Function for plotting quarter team points from standard vs. super shots
    # in each game of the round
    #
    # Input:    round2Plot - integer of the round to take data from
    #           matchInfo - matchInfo dictionary pulled from data import
    #           teamInfo - teamInfo dictionary pulled from data import
    #           df_scoreFlow - datframe of score flow data pulled from data import
    #           colourDict - dictionary matching team nicknames to colour plots
    #           bokehOptions - dictionary dictating Bokeh figure options
    
    #Check inputs
    if round2Plot is None:
        raise ValueError('A round to plot data from is required.')
    
    if matchInfo is None or teamInfo is None:
        raise ValueError('Both the match info and team info dictionaries from data import are required.')
        
    if df_scoreFlow is None:
        raise ValueError('The score flow dataframe from data import is required.')
    
    if colourDict is None:
        #Use default colour scheme
        colourDict = {'Fever': '#00953b',
                      'Firebirds': '#4b2c69',
                      'GIANTS': '#f57921',
                      'Lightning': '#fdb61c',
                      'Magpies': '#494b4a',
                      'Swifts': '#0082cd',
                      'Thunderbirds': '#e54078',
                      'Vixens': '#00a68e'}
        
    if bokehOptions is None:
        #Use basic options
        bokehOptions = dict(tools = ['wheel_zoom,box_zoom'])
    
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
                                      (df_scoreFlow['roundNo'] == round2Plot) &
                                      (df_scoreFlow['scoreName'] == 'goal') & 
                                      (df_scoreFlow['squadId'] == teamId1),
                                      ['scorePoints']].sum()[0] + \
            df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                             (df_scoreFlow['roundNo'] == round2Plot) &
                             (df_scoreFlow['scoreName'] == '2pt Goal') & 
                             (df_scoreFlow['squadId'] == teamId1),
                             ['scorePoints']].sum()[0]
        team2Score = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                      (df_scoreFlow['roundNo'] == round2Plot) &
                                      (df_scoreFlow['scoreName'] == 'goal') & 
                                      (df_scoreFlow['squadId'] == teamId2),
                                      ['scorePoints']].sum()[0] + \
            df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                             (df_scoreFlow['roundNo'] == round2Plot) &
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
                                                  (df_scoreFlow['roundNo'] == round2Plot) &
                                                  (df_scoreFlow['scoreName'] == 'goal') & 
                                                  (df_scoreFlow['squadId'] == teamId1) & 
                                                  (df_scoreFlow['period'] == qq+1),
                                                  ['scorePoints']].sum()[0])
            twoPointTeam1.append(df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                                  (df_scoreFlow['roundNo'] == round2Plot) &
                                                  (df_scoreFlow['scoreName'] == '2pt Goal') & 
                                                  (df_scoreFlow['squadId'] == teamId1) & 
                                                  (df_scoreFlow['period'] == qq+1),
                                                  ['scorePoints']].sum()[0])
            
        #Team 2
        standardTeam2 = list()
        twoPointTeam2 = list()
        for qq in range(0,4):
            standardTeam2.append(df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                                  (df_scoreFlow['roundNo'] == round2Plot) &
                                                  (df_scoreFlow['scoreName'] == 'goal') & 
                                                  (df_scoreFlow['squadId'] == teamId2) & 
                                                  (df_scoreFlow['period'] == qq+1),
                                                  ['scorePoints']].sum()[0])
            twoPointTeam2.append(df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                                  (df_scoreFlow['roundNo'] == round2Plot) &
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

    #Show grid
    if showPlot is True:       
        show(grid)
    
    #Export grid as both .png and .html
    if exportPNG is True or exportHTML is True:
        
        #First, check if the directory exists and needs making
        if os.path.isdir('round'+str(round2Plot)+'-quarterteampoints-onevstwo') is False:
            os.mkdir('round'+str(round2Plot)+'-quarterteampoints-onevstwo')
            
        #Navigate to directory
        os.chdir('round'+str(round2Plot)+'-quarterteampoints-onevstwo')
    
        #Check and export PNG if required
        if exportPNG is True:
            export_png(grid, filename = 'round'+str(round2Plot)+'-quarterteampoints-onevstwo.png')
    
        #Check and export HTML if required
        if exportHTML is True:
            output_file('round'+str(round2Plot)+'-quarterteampoints-onevstwo.html')
            save(grid)
    
        #Navigate back up to original directory
        os.chdir('..')
        
# %% teamShotRatiosInnerVsOuter

def teamShotRatiosInnerVsOuter(round2Plot = None, matchInfo = None,
                               teamInfo = None, df_scoreFlow = None,
                               colourDict = None, bokehOptions = None,
                               showPlot = False, exportPNG = True,
                               exportHTML = True):
    
    # Function for plotting ratio of standard vs. super shots by teams in
    # in each game of the round
    #
    # Input:    round2Plot - integer of the round to take data from
    #           matchInfo - matchInfo dictionary pulled from data import
    #           teamInfo - teamInfo dictionary pulled from data import
    #           df_scoreFlow - datframe of score flow data pulled from data import
    #           colourDict - dictionary matching team nicknames to colour plots
    #           bokehOptions - dictionary dictating Bokeh figure options
    
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
                                      (df_scoreFlow['roundNo'] == round2Plot) &
                                      (df_scoreFlow['scoreName'] == 'goal') & 
                                      (df_scoreFlow['squadId'] == teamId1),
                                      ['scorePoints']].sum()[0] + \
            df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                             (df_scoreFlow['roundNo'] == round2Plot) &
                             (df_scoreFlow['scoreName'] == '2pt Goal') & 
                             (df_scoreFlow['squadId'] == teamId1),
                             ['scorePoints']].sum()[0]
        team2Score = df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                      (df_scoreFlow['roundNo'] == round2Plot) &
                                      (df_scoreFlow['scoreName'] == 'goal') & 
                                      (df_scoreFlow['squadId'] == teamId2),
                                      ['scorePoints']].sum()[0] + \
            df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                             (df_scoreFlow['roundNo'] == round2Plot) &
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
                                               (df_scoreFlow['roundNo'] == round2Plot) &
                                               (df_scoreFlow['squadId'] == teamId1) & 
                                               (df_scoreFlow['periodCategory'] == ratios[qq]) &
                                               (df_scoreFlow['shotCircle'] == 'innerCircle'),
                                               ['shotCircle']].count()[0])
            outerTeam1.append(df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                               (df_scoreFlow['roundNo'] == round2Plot) &
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
                                               (df_scoreFlow['roundNo'] == round2Plot) &
                                               (df_scoreFlow['squadId'] == teamId2) & 
                                               (df_scoreFlow['periodCategory'] == ratios[qq]) &
                                               (df_scoreFlow['shotCircle'] == 'innerCircle'),
                                               ['shotCircle']].count()[0])
            outerTeam2.append(df_scoreFlow.loc[(df_scoreFlow['matchNo'] == gg+1) & 
                                               (df_scoreFlow['roundNo'] == round2Plot) &
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
    
    #Show grid
    if showPlot is True:       
        show(grid)
    
    #Export grid as both .png and .html
    if exportPNG is True or exportHTML is True:
        
        #First, check if the directory exists and needs making
        if os.path.isdir('round'+str(round2Plot)+'-teamshotratios-innervsouter') is False:
            os.mkdir('round'+str(round2Plot)+'-teamshotratios-innervsouter')
            
        #Navigate to directory
        os.chdir('round'+str(round2Plot)+'-teamshotratios-innervsouter')
    
        #Check and export PNG if required
        if exportPNG is True:
            export_png(grid, filename = 'round'+str(round2Plot)+'-teamshotratios-innervsouter.png')
    
        #Check and export HTML if required
        if exportHTML is True:
            output_file('round'+str(round2Plot)+'-teamshotratios-innervsouter.html')
            save(grid)
    
        #Navigate back up to original directory
        os.chdir('..')
        
# %% playerTwoPointTotals

def playerTwoPointTotals(round2Plot = None, df_scoreFlow = None,
                         df_playerInfo = None, df_teamInfo = None,
                         colourDict = None, showPlot = False,
                         exportPNG = True, exportHTML = True):

    # Function for plotting total points from super shots for individual
    # players
    #
    # Input:    round2Plot - integer of the round to take data from
    #           df_scoreFlow - dataframe of score flow data pulled from data import
    #           df_playerInfo - dataframe of player info pulled from data import
    #           df_teamInfo - dataframe of team pulled from data import
    #           colourDict - dictionary matching team nicknames to colour plots
    
    #Check inputs
    if round2Plot is None:
        raise ValueError('A round to plot data from is required.')
    
    if df_scoreFlow is None or df_playerInfo is None or df_teamInfo is None:
        raise ValueError('The score flow, player and team info dataframes from data import is required.')
    
    if colourDict is None:
        #Use default colour scheme
        colourDict = {'Fever': '#00953b',
                      'Firebirds': '#4b2c69',
                      'GIANTS': '#f57921',
                      'Lightning': '#fdb61c',
                      'Magpies': '#494b4a',
                      'Swifts': '#0082cd',
                      'Thunderbirds': '#e54078',
                      'Vixens': '#00a68e'}
    
    #Set blank lists to fill with plots and source
    figPlot = list()
    figSource = list()

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
    figSource.append(ColumnDataSource(data = dict(players = players,
                                                  counts = totals,
                                                  fullNames = fullNames,
                                                  squadNames = squadNames,
                                                  color = tuple(twoPointTotalsPalette))))
    
    #Create figure
    figPlot.append(figure(x_range = players, plot_height = 400, plot_width = 800,
                          title = 'Total Points from Super Shots',
                          toolbar_location = None,
                          tools = 'hover', 
                          tooltips = [("Player", "@fullNames"), ("Team", "@squadNames"), ("Total Points from Super Shots", "@counts")]))
    
    #Add bars
    figPlot[0].vbar(x = 'players', top = 'counts', width=0.6,
                    color = 'color', source = figSource[0])
    
    #Set figure parameters
    figPlot[0].y_range.start = 0
    figPlot[0].x_range.range_padding = 0.1
    figPlot[0].xaxis.major_label_orientation = 1
    figPlot[0].xgrid.grid_line_color = None
    figPlot[0].title.align = 'center'
    figPlot[0].yaxis.axis_label = 'Total Points'
    
    #Show figure
    if showPlot is True:       
        show(figPlot[0])
    
    #Export grid as both .png and .html
    if exportPNG is True or exportHTML is True:
        
        #First, check if the directory exists and needs making
        if os.path.isdir('round'+str(round2Plot)+'-player-twopointtotals') is False:
            os.mkdir('round'+str(round2Plot)+'-player-twopointtotals')
            
        #Navigate to directory
        os.chdir('round'+str(round2Plot)+'-player-twopointtotals')
    
        #Check and export PNG if required
        if exportPNG is True:
            export_png(figPlot[0], filename = 'round'+str(round2Plot)+'-player-twopointtotals.png')
    
        #Check and export HTML if required
        if exportHTML is True:
            output_file('round'+str(round2Plot)+'-player-twopointtotals.html')
            save(figPlot[0])
    
        #Navigate back up to original directory
        os.chdir('..')
        
# %% playerTwoPointDifferentials

def playerTwoPointDifferentials(round2Plot = None, df_scoreFlow = None,
                                df_playerInfo = None, df_teamInfo = None,
                                colourDict = None, showPlot = False,
                                exportPNG = True, exportHTML = True):
    
    # Function for plotting point differential from super vs. standard shots
    # for individual players
    #
    # Input:    round2Plot - integer of the round to take data from
    #           df_scoreFlow - dataframe of score flow data pulled from data import
    #           df_playerInfo - dataframe of player info pulled from data import
    #           df_teamInfo - dataframe of team pulled from data import
    #           colourDict - dictionary matching team nicknames to colour plots
    
    #Check inputs
    if round2Plot is None:
        raise ValueError('A round to plot data from is required.')
    
    if df_scoreFlow is None or df_playerInfo is None or df_teamInfo is None:
        raise ValueError('The score flow, player and team info dataframes from data import is required.')
    
    if colourDict is None:
        #Use default colour scheme
        colourDict = {'Fever': '#00953b',
                      'Firebirds': '#4b2c69',
                      'GIANTS': '#f57921',
                      'Lightning': '#fdb61c',
                      'Magpies': '#494b4a',
                      'Swifts': '#0082cd',
                      'Thunderbirds': '#e54078',
                      'Vixens': '#00a68e'}
    
    #Set blank lists to fill with plots and source
    figPlot = list()
    figSource = list()
    
    #Extract a dataframe of all Goals
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
    figSource.append(ColumnDataSource(data = dict(players = players,
                                                  counts = differentials,
                                                  fullNames = fullNames,
                                                  squadNames = squadNames,
                                                  color = tuple(twoPointDifferentialPalette))))
    
    #Create figure
    figPlot.append(figure(x_range = players, plot_height = 400, plot_width = 800,
                          title = 'Differential in Points from Super vs. Standard Shots',
                          toolbar_location = None,
                          tools = 'hover', 
                          tooltips = [("Player", "@fullNames"), ("Team", "@squadNames"), ("Differential in Points from Standard vs. Super Shots", "@counts")]))
    
    #Add bars
    figPlot[0].vbar(x = 'players', top = 'counts', width=0.6,
                    color = 'color', source = figSource[0])
    
    #Set figure parameters
    figPlot[0].x_range.range_padding = 0.1
    figPlot[0].xaxis.major_label_orientation = 1
    figPlot[0].xgrid.grid_line_color = None
    figPlot[0].title.align = 'center'
    figPlot[0].yaxis.axis_label = 'Points from Two-Point Shots - Points from One-Point Shots'
    
    #Show figure
    if showPlot is True:       
        show(figPlot[0])
    
    #Export grid as both .png and .html
    if exportPNG is True or exportHTML is True:
        
        #First, check if the directory exists and needs making
        if os.path.isdir('round'+str(round2Plot)+'-player-twopointdifferentials') is False:
            os.mkdir('round'+str(round2Plot)+'-player-twopointdifferentials')
            
        #Navigate to directory
        os.chdir('round'+str(round2Plot)+'-player-twopointdifferentials')
    
        #Check and export PNG if required
        if exportPNG is True:
            export_png(figPlot[0], filename = 'round'+str(round2Plot)+'-player-twopointdifferentials.png')
    
        #Check and export HTML if required
        if exportHTML is True:
            output_file('round'+str(round2Plot)+'-player-twopointdifferentials.html')
            save(figPlot[0])
    
        #Navigate back up to original directory
        os.chdir('..')
    
# %% playerTwoPointRelativeDifferentials

def playerTwoPointRelativeDifferentials(round2Plot = None, df_scoreFlow = None,
                                        df_playerInfo = None, df_teamInfo = None,
                                        colourDict = None, showPlot = False,
                                        exportPNG = True, exportHTML = True):
    
    # Function for plotting point differential from super vs. standard shots
    # for individual players
    #
    # Input:    round2Plot - integer of the round to take data from
    #           df_scoreFlow - dataframe of score flow data pulled from data import
    #           df_playerInfo - dataframe of player info pulled from data import
    #           df_teamInfo - dataframe of team pulled from data import
    #           colourDict - dictionary matching team nicknames to colour plots
    
    #Check inputs
    if round2Plot is None:
        raise ValueError('A round to plot data from is required.')
    
    if df_scoreFlow is None or df_playerInfo is None or df_teamInfo is None:
        raise ValueError('The score flow, player and team info dataframes from data import is required.')
    
    if colourDict is None:
        #Use default colour scheme
        colourDict = {'Fever': '#00953b',
                      'Firebirds': '#4b2c69',
                      'GIANTS': '#f57921',
                      'Lightning': '#fdb61c',
                      'Magpies': '#494b4a',
                      'Swifts': '#0082cd',
                      'Thunderbirds': '#e54078',
                      'Vixens': '#00a68e'}
    
    #Set blank lists to fill with plots and source
    figPlot = list()
    figSource = list()
    
    #Extract a dataframe of all Goals
    df_allGoals = df_scoreFlow.loc[(df_scoreFlow['scoreName'].isin(['goal','2pt Goal'])) & 
                                   (df_scoreFlow['roundNo'] == round2Plot),]
    
    #Get the unique list of players who scored any goal
    playerList_allGoals = list(df_allGoals['playerId'].unique())

    #Loop through and sum the total one and two point value for each player
    #Calculate the relative differential with +ve reflecting more two point points
    playerList_2ptDifferentialRelative = list()
    playerList_bothGoals = list()
    
    #Loop through player list
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
    figSource.append(ColumnDataSource(data = dict(players = players,
                                                  counts = differentials,
                                                  fullNames = fullNames,
                                                  squadNames = squadNames,
                                                  color = tuple(twoPointDifferentialPalette))))
    
    #Create figure
    figPlot.append(figure(x_range = players, plot_height = 400, plot_width = 800,
                          title = 'Relative Differential in Points from Super vs. Standard Shots',
                          toolbar_location = None,
                          tools = 'hover', 
                          tooltips = [("Player", "@fullNames"), ("Team", "@squadNames"), ("Ratio of Points from Super:Standard Shots", "@counts")]))
    
    #Add bars
    figPlot[0].vbar(x = 'players', top = 'counts', width=0.6,
                    color = 'color', source = figSource[0])
    
    #Set figure parameters
    figPlot[0].y_range.start = 0
    figPlot[0].x_range.range_padding = 0.1
    figPlot[0].xaxis.major_label_orientation = 1
    figPlot[0].xgrid.grid_line_color = None
    figPlot[0].title.align = 'center'
    figPlot[0].yaxis.axis_label = 'Points from Super Shots / Points from Standard Shots'
    
    #Show figure
    if showPlot is True:       
        show(figPlot[0])
    
    #Export grid as both .png and .html
    if exportPNG is True or exportHTML is True:
        
        #First, check if the directory exists and needs making
        if os.path.isdir('round'+str(round2Plot)+'-player-twopointdifferentialsrelative') is False:
            os.mkdir('round'+str(round2Plot)+'-player-twopointdifferentialsrelative')
            
        #Navigate to directory
        os.chdir('round'+str(round2Plot)+'-player-twopointdifferentialsrelative')
    
        #Check and export PNG if required
        if exportPNG is True:
            export_png(figPlot[0], filename = 'round'+str(round2Plot)+'-player-twopointdifferentialsrelative.png')
    
        #Check and export HTML if required
        if exportHTML is True:
            output_file('round'+str(round2Plot)+'-player-twopointdifferentialsrelative.html')
            save(figPlot[0])
    
        #Navigate back up to original directory
        os.chdir('..')
        
# %% totalPlusMinusLineUps

def totalPlusMinusLineUps(teamInfo = None, df_lineUp = None,
                          absPlusMinus = True, perPlusMinus = True,
                          perDivider = 15, minLineUpDuration = 5,
                          colourDict = None, showPlot = False,
                          exportPNG = True, exportHTML = True):

    # Function for plotting the absolute plus minus for team line-ups across 
    # all currently completed games.
    #
    # Input:    teamInfo - dictionary of team info pulled from data import
    #           df_lineUp - dataframe of lineup data pulled from data import
    #           absPlusMinus - boolean of whether to calculate absolute plus/minus
    #           perPlusMinus - boolean of whether to calculate per mins plus/minus
    #           perDivider - factor (in minutes) to calculate per mins plus/minus
    #           minLineUpDuration - minimum no. of minutes to consider a new lineup
    #           colourDict - dictionary matching team nicknames to colour plots
    
    #Check inputs
    if teamInfo is None:
        raise ValueError('Team info dictionary is required.')
    
    if df_lineUp is None:
        raise ValueError('The dataframe with lineup data from data import is required.')
    
    if colourDict is None:
        #Use default colour scheme
        colourDict = {'Fever': '#00953b',
                      'Firebirds': '#4b2c69',
                      'GIANTS': '#f57921',
                      'Lightning': '#fdb61c',
                      'Magpies': '#494b4a',
                      'Swifts': '#0082cd',
                      'Thunderbirds': '#e54078',
                      'Vixens': '#00a68e'}
        
    #Set blank lists to fill with plots and source
    if absPlusMinus is True:
        figPlotAbs = list()
        figSourceAbs = list()
    if perPlusMinus is True:
        figPlotPer = list()
        figSourcePer = list()
    
    #Get alphabetical list of squad nicknames
    plotSquadNames = teamInfo['squadNickname']
    plotSquadNames = sorted(plotSquadNames)
    
    #Get the id's for the team names ordering
    plotSquadId = list()
    for tt in range(0,len(plotSquadNames)):
        plotSquadId.append(teamInfo['squadId'][teamInfo['squadNickname'].index(plotSquadNames[tt])])
   
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
            #Get lineup
            currLineUp = df_lineUpChecker['lineUpName'][dd]
            #Check for empty slot in lineup
            for pp in range(0,len(currLineUp)):
                if not currLineUp[pp]:
                    #Replace with an 'N/A'
                    currLineUp[pp] = 'N/A'
            #Combine player names
            combinedLineUpName.append(", ".join(currLineUp))
        #Append to dataframe
        df_lineUpChecker['combinedLineUpName'] = combinedLineUpName
            
        #Extract the unique lineups for the current team
        uniqueLineUps = df_lineUpChecker['combinedLineUpName'].unique()
        
        #Loop through unique lineups and sum the duration and plus/minus data
        lineUpDuration = list()
        lineUpPlusMinus = list()
        analyseLineUps = list()
        for uu in range(0,len(uniqueLineUps)):
            #Get a separated dataframe
            df_currLineUp = df_lineUpChecker.loc[(df_lineUpChecker['combinedLineUpName'] == uniqueLineUps[uu]),]
            #Sum data and append to list if greater than specified minutes (converted to seconds here)
            if sum(df_currLineUp['durationSeconds']) >= (minLineUpDuration*60):
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
        
        #Add a per minute column to dataframe
        if perPlusMinus is True:
            perPlusMinusVal = list()
            for mm in range(0,len(df_lineUpPlusMinus)):
                perFac = perDivider / df_lineUpPlusMinus['lineUpDuration'][mm]
                perPlusMinusVal.append(df_lineUpPlusMinus['lineUpPlusMinus'][mm]*perFac)
            #Append to dataframe
            df_lineUpPlusMinus['lineUpPerPlusMinus'] = perPlusMinusVal
        
        #Create source for figures
        if absPlusMinus is True:
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
        if perPlusMinus is True:
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
        if absPlusMinus is True:
            figPlotAbs.append(figure(x_range = list(df_lineUpPlusMinus['analyseLineUps']), plot_height = 300, plot_width = 400,
                                     title = plotSquadNames[tt]+' Lineups Plus/Minus (Min. '+str(minLineUpDuration)+' Minutes Played)',
                                     toolbar_location = None,
                                     tools = 'hover', 
                                     tooltips = [("GS", "@lineUpGS"), ("GA", "@lineUpGA"), ("WA", "@lineUpWA"), 
                                              ("C", "@lineUpC"), ("WD", "@lineUpWD"), ("GD", "@lineUpGD"), ("GK", "@lineUpGK"),
                                              ("Minutes Played", "@durations"), ("Plus/Minus", "@plusMinus")]))
        if perPlusMinus is True:
            figPlotPer.append(figure(x_range = list(df_lineUpPlusMinus['analyseLineUps']), plot_height = 300, plot_width = 400,
                                     title = plotSquadNames[tt]+' Lineups Plus/Minus per '+str(perDivider)+' Minute (Min. '+str(minLineUpDuration)+' Minutes Played)',
                                     toolbar_location = None,
                                     tools = 'hover', 
                                     tooltips = [("GS", "@lineUpGS"), ("GA", "@lineUpGA"), ("WA", "@lineUpWA"), 
                                              ("C", "@lineUpC"), ("WD", "@lineUpWD"), ("GD", "@lineUpGD"), ("GK", "@lineUpGK"),
                                              ("Minutes Played", "@durations"), ("Plus/Minus per "+str(perDivider)+" Mins", "@plusMinus")]))
        
        #Add bars
        if absPlusMinus is True:
            figPlotAbs[tt].vbar(x = 'analyseLineUps', top = 'plusMinus', width=0.6,
                                color = colourDict[plotSquadNames[tt]], source = figSourceAbs[tt])
        if perPlusMinus is True:
            figPlotPer[tt].vbar(x = 'analyseLineUps', top = 'plusMinus', width=0.6,
                                color = colourDict[plotSquadNames[tt]], source = figSourcePer[tt])
        
        #Set figure parameters
        if absPlusMinus is True:
            # figPlot[tt].y_range.start = 0
            figPlotAbs[tt].x_range.range_padding = 0.1
            figPlotAbs[tt].xaxis.major_label_orientation = 1
            figPlotAbs[tt].xgrid.grid_line_color = None
            figPlotAbs[tt].title.align = 'center'
            figPlotAbs[tt].yaxis.axis_label = 'Total Plus/Minus'
            figPlotAbs[tt].xaxis.major_label_text_font_size = '0pt'  # current solution to turn off long x-tick labels
            figPlotAbs[tt].xaxis.major_tick_line_color = None  # turn off x-axis major ticks
            
        if perPlusMinus is True:
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
    if absPlusMinus is True:
        gridAbs = gridplot([[figPlotAbs[0], figPlotAbs[1], figPlotAbs[2], figPlotAbs[3]],
                            [figPlotAbs[4], figPlotAbs[5], figPlotAbs[6], figPlotAbs[7]]],
                           plot_height = 300, plot_width = 400)
    if perPlusMinus is True:
        gridPer = gridplot([[figPlotPer[0], figPlotPer[1], figPlotPer[2], figPlotPer[3]],
                            [figPlotPer[4], figPlotPer[5], figPlotPer[6], figPlotPer[7]]],
                           plot_height = 300, plot_width = 400)
    
    #Show grid
    if showPlot is True:
        show(gridAbs)
        show(gridPer)
        
    #Export grid as both .png and .html
    if exportPNG is True or exportHTML is True:
        
        #Absolute plus minus first
        if absPlusMinus is True:
        
            #First, check if the directory exists and needs making
            if os.path.isdir('total-absolutePlusMinus-teamLineUps') is False:
                os.mkdir('total-absolutePlusMinus-teamLineUps')
                
            #Navigate to directory
            os.chdir('total-absolutePlusMinus-teamLineUps')
        
            #Check and export PNG if required
            if exportPNG is True:
                export_png(gridAbs, filename = 'total-absolutePlusMinus-teamLineUps.png')
        
            #Check and export HTML if required
            if exportHTML is True:
                output_file('total-absolutePlusMinus-teamLineUps.html')
                save(gridAbs)
        
            #Navigate back up to original directory
            os.chdir('..')
            
        #Per plus minus
        if perPlusMinus is True:
            
            #First, check if the directory exists and needs making
            if os.path.isdir('total-per'+str(perDivider)+'PlusMinus-teamLineUps') is False:
                os.mkdir('total-per'+str(perDivider)+'PlusMinus-teamLineUps')
                
            #Navigate to directory
            os.chdir('total-per'+str(perDivider)+'PlusMinus-teamLineUps')
        
            #Check and export PNG if required
            if exportPNG is True:
                export_png(gridPer, filename = 'total-per'+str(perDivider)+'PlusMinus-teamLineUps.png')
        
            #Check and export HTML if required
            if exportHTML is True:
                output_file('total-per'+str(perDivider)+'PlusMinus-teamLineUps.html')
                save(gridPer)
        
            #Navigate back up to original directory
            os.chdir('..')

# %% playerPlusMinus

def playerPlusMinus(teamInfo = None, playerInfo = None, df_individualLineUp = None,
                    absPlusMinus = True, perPlusMinus = True,
                    perDivider = 15, minDuration = 10, nPlayers = 20,
                    colourDict = None, showPlot = False,
                    exportPNG = True, exportHTML = True):

    # Function for plotting the absolute and per plus minus for players across 
    # all currently completed games.
    #
    # Input:    teamInfo - dictionary of team info pulled from data import
    #           playerInfo - dictionary of player info pulled from data import
    #           df_individualLineUp - dataframe of individual lineup data pulled from data import
    #           absPlusMinus - boolean of whether to calculate absolute plus/minus
    #           perPlusMinus - boolean of whether to calculate per mins plus/minus
    #           perDivider - factor (in minutes) to calculate per mins plus/minus
    #           minDuration - minimum no. of minutes to include a player
    #           nPlayers - number of players to plot from the leader
    #           colourDict - dictionary matching team nicknames to colour plots
    
    #Check inputs
    if teamInfo is None:
        raise ValueError('Team info dictionary is required.')
        
    if playerInfo is None:
        raise ValueError('Player info dictionary is required.')
    
    if df_individualLineUp is None:
        raise ValueError('The dataframe with individual lineup data from data import is required.')
    
    if colourDict is None:
        #Use default colour scheme
        colourDict = {'Fever': '#00953b',
                      'Firebirds': '#4b2c69',
                      'GIANTS': '#f57921',
                      'Lightning': '#fdb61c',
                      'Magpies': '#494b4a',
                      'Swifts': '#0082cd',
                      'Thunderbirds': '#e54078',
                      'Vixens': '#00a68e'}
    
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
        
        #Check if player total is greater than minimum minutes and get data if so
        if sum(df_currPlayer['durationSeconds']) > (minDuration*60):
            #Append duration and plus/minus
            playerDuration.append(sum(df_currPlayer['durationSeconds'])/60)
            playerPlusMinus.append(sum(df_currPlayer['plusMinus']))
            #Calculate per plus minus
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
    if absPlusMinus is True:
        figPlotAbs = list()
        figSourceAbs = list()
        
        #Create source for figure
        figSourceAbs.append(ColumnDataSource(data = dict(players = list(df_playerPlusMinus['analysePlayer'].iloc[0:nPlayers]),
                                                         counts = list(df_playerPlusMinus['playerPlusMinus'].iloc[0:nPlayers]),
                                                         duration = list(df_playerPlusMinus['playerDuration'].iloc[0:nPlayers]),
                                                         squad = list(df_playerPlusMinus['analyseSquad'].iloc[0:nPlayers]),
                                                         colours = tuple(df_playerPlusMinus['analyseColour'].iloc[0:nPlayers]))))
        
        #Create figure
        figPlotAbs.append(figure(x_range = list(df_playerPlusMinus['analysePlayer'].iloc[0:nPlayers]), plot_height = 400, plot_width = 800,
                                 title = 'Top '+str(nPlayers)+' Players for Total Plus/Minus (min. '+str(minDuration)+' minutes played)',
                                 toolbar_location = None,
                                 tools = 'hover', 
                                 tooltips = [("Player", "@players"), ("Team", "@squad"), ("Total Minutes", "@duration"), ("Player Total Plus/Minus", "@counts")]))
        
        #Add bars
        figPlotAbs[0].vbar(x = 'players', top = 'counts', width=0.6,
                        color = 'colours', source = figSourceAbs[0])
        
        #Set figure parameters
        figPlotAbs[0].y_range.start = 0
        figPlotAbs[0].x_range.range_padding = 0.1
        figPlotAbs[0].xaxis.major_label_orientation = 1
        figPlotAbs[0].xgrid.grid_line_color = None
        figPlotAbs[0].title.align = 'center'
        figPlotAbs[0].yaxis.axis_label = 'Total Plus/Minus'
        
        # #Show figure
        # show(figPlotAbs[0])
        
    #Create per plus minus figure
    if perPlusMinus is True:
        
        #Create figure for total player plus minus (top 20 players)
        figPlotPer = list()
        figSourcePer = list()
        
        #Create source for figure
        figSourcePer.append(ColumnDataSource(data = dict(players = list(df_playerPlusMinus['analysePlayer'].iloc[0:nPlayers]),
                                                         counts = list(df_playerPlusMinus['playerPlusMinusPer15'].iloc[0:nPlayers]),
                                                         duration = list(df_playerPlusMinus['playerDuration'].iloc[0:nPlayers]),
                                                         squad = list(df_playerPlusMinus['analyseSquad'].iloc[0:nPlayers]),
                                                         colours = tuple(df_playerPlusMinus['analyseColour'].iloc[0:nPlayers]))))
        
        #Create figure
        figPlotPer.append(figure(x_range = list(df_playerPlusMinus['analysePlayer'].iloc[0:nPlayers]), plot_height = 400, plot_width = 800,
                                 title = 'Top '+str(nPlayers)+' Players for Total Plus/Minus Per '+str(perDivider)+' Minutes (min. '+str(minDuration)+' minutes played)',
                                 toolbar_location = None,
                                 tools = 'hover', 
                                 tooltips = [("Player", "@players"), ("Team", "@squad"), ("Total Minutes", "@duration"), ("Player Total Plus/Minus Per "+str(perDivider), "@counts")]))
        
        #Add bars
        figPlotPer[0].vbar(x = 'players', top = 'counts', width=0.6,
                        color = 'colours', source = figSourcePer[0])
        
        #Set figure parameters
        figPlotPer[0].y_range.start = 0
        figPlotPer[0].x_range.range_padding = 0.1
        figPlotPer[0].xaxis.major_label_orientation = 1
        figPlotPer[0].xgrid.grid_line_color = None
        figPlotPer[0].title.align = 'center'
        figPlotPer[0].yaxis.axis_label = 'Total Plus/Minus Per '+str(perDivider)+' Minutes Played'
        
        # #Show figure
        # show(figPlotPer[0])
    
    #Export figure as PNG and HTML
    if exportPNG is True or exportHTML is True:
        
        #Absolute plus minus
        if absPlusMinus is True:
        
            #Seems like storing html in same folder causes figures to overwrite?
            #Make directory to store
            if os.path.isdir('total-absolutePlusMinus-players') is False:
                os.mkdir('total-absolutePlusMinus-players')
            os.chdir('total-absolutePlusMinus-players')
            
            #PNG
            if exportPNG is True:
                export_png(figPlotAbs[0], filename = 'total-absolutePlusMinus-players.png')
            
            #HTML
            if exportHTML is True:
                output_file('total-absolutePlusMinus-players.html')
                save(figPlotAbs[0])
            
            #Navigate back up
            os.chdir('..') 
            
        #Per plus minus
        if perPlusMinus is True:
            
            #Make directory to store
            os.mkdir('total-per'+str(perDivider)+'PlusMinus-players')
            os.chdir('total-per'+str(perDivider)+'PlusMinus-players')
            
            if exportPNG is True:
                #PNG
                export_png(figPlotPer[0], filename = 'total-per'+str(perDivider)+'PlusMinus-players.png')
            
            if exportHTML is True:
                #HTML
                output_file('total-per'+str(perDivider)+'PlusMinus-players.html')
                save(figPlotPer[0])

            #Navigate back up
            os.chdir('..') 
            
# %% relativePlayerPlusMinus


def relativePlayerPlusMinus(teamInfo = None, playerInfo = None, df_individualLineUp = None,
                            perDivider = 15, minDurationOn = 10,
                            minDurationOff = 5, nPlayers = 20,
                            colourDict = None, showPlot = False,
                            exportPNG = True, exportHTML = True):

    # Function for plotting the relative on vs. off plus/minus for players across 
    # all currently completed games.
    #
    # Input:    teamInfo - dictionary of team info pulled from data import
    #           playerInfo - dictionary of player info pulled from data import
    #           df_individualLineUp - dataframe of individual lineup data pulled from data import
    #           absPlusMinus - boolean of whether to calculate absolute plus/minus
    #           perPlusMinus - boolean of whether to calculate per mins plus/minus
    #           perDivider - factor (in minutes) to calculate per mins plus/minus
    #           minDurationOn - minimum no. of minutes on court to include a player
    #           minDurationOff - minimum no. of minutes off court to include a player
    #           nPlayers - number of players to plot from the leader
    #           colourDict - dictionary matching team nicknames to colour plots
    
    #Check inputs
    if teamInfo is None:
        raise ValueError('Team info dictionary is required.')
        
    if playerInfo is None:
        raise ValueError('Player info dictionary is required.')
    
    if df_individualLineUp is None:
        raise ValueError('The dataframe with individual lineup data from data import is required.')
    
    if colourDict is None:
        #Use default colour scheme
        colourDict = {'Fever': '#00953b',
                      'Firebirds': '#4b2c69',
                      'GIANTS': '#f57921',
                      'Lightning': '#fdb61c',
                      'Magpies': '#494b4a',
                      'Swifts': '#0082cd',
                      'Thunderbirds': '#e54078',
                      'Vixens': '#00a68e'}
    
    #Get unique list of players from the lineup dataframe
    plotPlayers = list(df_individualLineUp['playerId'].unique())
    
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
        
        #Check if player total is greater than designated
        if sum(df_currPlayerOn['durationSeconds']) > (minDurationOn*60) and sum(df_currPlayerOff['durationSeconds']) > (minDurationOff*60):
            #Append duration and plus/minus when on vs. off
            playerDurationOn.append(sum(df_currPlayerOn['durationSeconds'])/60)
            playerPlusMinusOn.append(sum(df_currPlayerOn['plusMinus']))
            playerDurationOff.append(sum(df_currPlayerOff['durationSeconds'])/60)
            playerPlusMinusOff.append(sum(df_currPlayerOff['plusMinus']))
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
    figSource.append(ColumnDataSource(data = dict(players = list(df_playerPlusMinusRel['analysePlayer'].iloc[0:nPlayers]),
                                                  counts = list(df_playerPlusMinusRel['relPerformancePer15'].iloc[0:nPlayers]),
                                                  durationOn = list(df_playerPlusMinusRel['playerDurationOn'].iloc[0:nPlayers]),
                                                  durationOff = list(df_playerPlusMinusRel['playerDurationOff'].iloc[0:nPlayers]),
                                                  squad = list(df_playerPlusMinusRel['analyseSquad'].iloc[0:nPlayers]),
                                                  colours = tuple(df_playerPlusMinusRel['analyseColour'].iloc[0:nPlayers]))))
    
    #Create figure
    figPlot.append(figure(x_range = list(df_playerPlusMinusRel['analysePlayer'].iloc[0:nPlayers]), plot_height = 400, plot_width = 800,
                          title = 'Top '+str(nPlayers)+' Players for Plus/Minus per '+str(perDivider)+' Minute when On vs. Off Court (min. '+str(minDurationOn)+' minutes on & '+str(minDurationOff)+' minutes off court)',
                          toolbar_location = None,
                          tools = 'hover', 
                          tooltips = [("Player", "@players"), ("Team", "@squad"), ("Minutes On-Court", "@durationOn"), ("Minutes Off-Court", "@durationOff"), ("Relative Plus/Minus per "+str(perDivider)+" Minutes", "@counts")]))
    
    #Add bars
    figPlot[0].vbar(x = 'players', top = 'counts', width=0.6,
                    color = 'colours', source = figSource[0])
    
    #Set figure parameters
    figPlot[0].y_range.start = 0
    figPlot[0].x_range.range_padding = 0.1
    figPlot[0].xaxis.major_label_orientation = 1
    figPlot[0].xgrid.grid_line_color = None
    figPlot[0].title.align = 'center'
    figPlot[0].yaxis.axis_label = 'Relative Plus/Minus per '+str(perDivider)+' Minutes'
    
    # #Show figure
    # show(figPlot[0])
    
    #Export figure as PNG and HTML
    if exportPNG is True or exportHTML is True:
    
        #Seems like storing html in same folder causes figures to overwrite?
        #Make directory to store
        if os.path.isdir('total-relativePer'+str(perDivider)+'PlusMinus-players') is False:
            os.mkdir('total-relativePer'+str(perDivider)+'PlusMinus-players')
        os.chdir('total-relativePer'+str(perDivider)+'PlusMinus-players')
        
        #PNG
        if exportPNG is True:
            export_png(figPlot[0], filename = 'total-relativePer'+str(perDivider)+'PlusMinus-players.png')
        
        #HTML
        if exportHTML is True:
            output_file('total-relativePer'+str(perDivider)+'PlusMinus-players.html')
            save(figPlot[0])
        
        #Navigate back up
        os.chdir('..')
        
# %%
