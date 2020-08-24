#Code grabs matches from Super Netball and ANZ Champiosnhips for use in
#training the win probability model. The code uses the superNetballR package
#which can be installed using:

# library(remotes)
# remotes::install_github("SteveLane/superNetballR")

#Set the .libPaths() to the conda environment library
.libPaths("C:/Users/aafox/AppData/Local/Continuum/anaconda3/envs/super_netball_analysis_r/Lib/R/library")

#Load packages
library(dplyr)
library(superNetballR)
library(jsonlite)

#Get Super Netball competition data (regular season only)

#Set competition ID's
ssnCompIds = c("10083","10393","10724")
ssnYears = c("2017","2018","2019")

#Set number of rounds for each season
ssnRoundNo = 14

#Set number of weekly matches
ssnMatchNo = 4

#Loop through years and rounds to download match data and store
for(yy in 1:length(ssnCompIds)) {
  for (rr in 1:ssnRoundNo) {
    for (mm in 1:ssnMatchNo) {
      
      #Get the current round and years match data
      matchData = downloadMatch(ssnCompIds[yy],rr,mm)
      
      #Save as .json
      fileName = paste("MatchData/SSN_",ssnYears[yy],"_r",rr,"_g",mm,".json",sep = "")
      write_json(matchData,fileName)
      
    } #end match no loop
  } #end round no loop
} #end comp ID loop


#### TODO: ANZ champs games --- note that sometimes these seem to have
#### variable match numbers within rounds...

#### Other matches outside of SSN 2017, 2018, 2019 kindly provided by Mitch Mooney
