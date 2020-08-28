#This code is currently set to grab matches from the 2020 Suncorp Super
#Netball season using the superNetballR package. As such it needs to be
#installed using:

# library(remotes)

# remotes::install_github("SteveLane/superNetballR")

#Load appropriate packages
library(dplyr)
library(superNetballR)
library(jsonlite)

#Download matches and save as .json
#2017 competition ID = 10083 (10084 finals)
#2018 competition ID = 10393 (10394 finals)
#2019 competition ID = 10724 (10725 finals)
#2020 competition ID = 11108

#Set 2020 competition ID
compID = "11108"

#Set round to grab
getRound = 7 ##### Change this for whichever round is desired

#Loop through the four matches and save as .json
for (mm in 1:4) {
  #Download match
  matchData <- downloadMatch(compID,getRound,mm)
  #Save as .json
  write_json(matchData,paste("../../../Data/SuperNetball2020/r",getRound,"_g",mm,"_SSN2020.json",sep=""))
}

##### TODO: set as relevant loop when comp complete
#NOTE: an error 'please install xml2 package' will occur with invalid match numbers