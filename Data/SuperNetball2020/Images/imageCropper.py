# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 22:10:29 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
"""

from PIL import Image, ImageChops, ImageDraw

##### CODE WORKS! WITH MANUAL ASPECTS OF COURSE!!!!
##### NEED TO ADJUST AND USE WITHIN LOOP FOR ALL

##### PERHAPS STORE A CROPPED VERSION OF FILES (i.e. different name)...

###### Can't get size right for circle...
#w = 440, h = 248
im = Image.open('A.Brazill.png')
bigsize = (im.size[0], im.size[1])
mask = Image.new('L', bigsize, 0)
# ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
ImageDraw.Draw(mask).ellipse([(220-124,0),(220+124,248)], fill=255)
# mask = mask.resize(im.size, Image.ANTIALIAS)
mask = ImageChops.darker(mask, im.split()[-1])
im.putalpha(mask)
im.save('cropped.png')