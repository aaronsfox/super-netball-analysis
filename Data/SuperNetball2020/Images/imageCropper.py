# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 22:10:29 2020

@author:
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
"""

from PIL import Image, ImageOps

mask = Image.open('mask.png').convert('L')
im = Image.open('A.Brazill.png')

output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
output.putalpha(mask)

output.save('output.png')


# %%

from PIL import Image, ImageOps, ImageDraw

size = (200, 200)
mask = Image.new('L', size, 0)
draw = ImageDraw.Draw(mask) 
draw.ellipse((0, 0) + size, fill=0)


im = Image.open('A.Brazill.png')


output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
output.putalpha(mask)

output.save('output.png')

# %%

from PIL import Image, ImageChops, ImageDraw

####### THIS IS PROBABLY THE ONE, ALTHOUGH UNSURE WHETHER THE
####### CIRCLE IS SYMETRICAL

###### Can't get size right for circle...

im = Image.open('A.Brazill.png')
bigsize = (im.size[0], im.size[0])
mask = Image.new('L', bigsize, 0)
ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
mask = mask.resize(im.size, Image.ANTIALIAS)
# mask = ImageChops.darker(mask, im.split()[-1])
im.putalpha(mask)
im.save('cropped.png')