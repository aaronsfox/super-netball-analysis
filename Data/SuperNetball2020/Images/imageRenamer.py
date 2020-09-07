# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 19:59:38 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Short script to rename downloaded SSN photos.
    
    This is really only applicable to run once when .png files
    have their original names from the Super Netball webpage.
    
    There is the potential for a few names to require correction
    due to not being the standard format (e.g. O'Brien)
    
"""
# %% Import packages

import os

# %% Rename files

#Get file list
fileList = list()
for file in os.listdir(os.getcwd()):
    if file.endswith('.png'):
        fileList.append(file)
        
#Loop through files and rename
for ff in range(0,len(fileList)):
    
    #Get current last name
    lastName = fileList[ff].split('_')[1].split('-')[0].capitalize()
    
    #Get current first initial
    initial = fileList[ff].split('_')[1].split('-')[1][0].capitalize()
    
    #Set rename string
    renameFile = initial+'.'+lastName+'.png'
    
    #Rename file
    os.rename(fileList[ff],renameFile)
    
# %% ----- End of imageRenamer.py ----- %% #
