#Code works through each season of the SSN and ANZ Championships to create Glicko2
#ratings for each team at each round. Currently this code is written to reset teams
#back to a default value at the start of each year in considering any team changes.
#
#The ratings developed here will be used as inputs to hopefully improve the ability
#of the developed win probability model.

#Set the .libPaths() to the conda environment library
.libPaths("C:/Users/aafox/AppData/Local/Continuum/anaconda3/envs/super_netball_analysis_r/Lib/R/library")

#Load packages


#Start with SSN competition data

# # Read in all json files collected using superNetballR package
# filenames <- list.files("data/", pattern="*.json", full.names=TRUE)
# myJSON <- lapply(filenames, function(x) fromJSON(file=x)) # a list in which each element is one of your original JSON files