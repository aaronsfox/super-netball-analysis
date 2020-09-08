# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 22:10:29 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
"""

# %% Import packages

from PIL import Image, ImageChops, ImageDraw
import os

# %% Crop and resave images

#Get file list
fileList = list()
for file in os.listdir(os.getcwd()):
    if file.endswith('.png'):
        fileList.append(file)

#Loop through files
for ff in range(0,len(fileList)):

    #Open image
    im = Image.open(fileList[ff])
    
    #Get image size
    w = im.size[0]
    h = im.size[1]
    
    #Create mask
    mask = Image.new('L', (w,h), 0)
    
    #Draw the ellipse
    ImageDraw.Draw(mask).ellipse([((w/2)-(h/2),0),((w/2)+(h/2),h)], fill=255)
    
    #Set the transparency on the mask
    mask = ImageChops.darker(mask, im.split()[-1])
    
    #Add mask to image
    im.putalpha(mask)
    
    #Save image
    im.save(fileList[ff][0:-4]+'_cropped.png')
    
# %% ----- End of imageCropper.py ----- %% #