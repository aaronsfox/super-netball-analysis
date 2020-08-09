#This code is currently set to grab matches from the 2020 Suncorp Super
#Netball season using the superNetballR package. As such it needs to be
#installed using:

#remotes::install_github("SteveLane/superNetballR")

#Load appropriate packages
library(dplyr)
library(superNetballR)
library(jsonlite)

#Download matches and save as .json
#2017 competition ID = 10083 (10084 finals)
#2018 competition ID = 10393 (10394 finals)
#2019 competition ID = 10724 (10725 finals)
#2020 competition ID = 11108
##### TODO: set as relevant loop
#NOTE: an error 'please install xml2 package' will occur with invalid match numbers
r1_g1 <- downloadMatch("11108",1,1)
r1_g2 <- downloadMatch("11108",1,2)
r1_g3 <- downloadMatch("11108",1,3)
r1_g4 <- downloadMatch("11108",1,4)

#Write as .json files
write_json(r1_g1,"r1_g1_SSN2020.json")
write_json(r1_g2,"r1_g2_SSN2020.json")
write_json(r1_g3,"r1_g3_SSN2020.json")
write_json(r1_g4,"r1_g4_SSN2020.json")

r2_g1 <- downloadMatch("11108",2,1)
r2_g2 <- downloadMatch("11108",2,2)
r2_g3 <- downloadMatch("11108",2,3)
r2_g4 <- downloadMatch("11108",2,4)

write_json(r2_g1,"r2_g1_SSN2020.json")
write_json(r2_g2,"r2_g2_SSN2020.json")
write_json(r2_g3,"r2_g3_SSN2020.json")
write_json(r2_g4,"r2_g4_SSN2020.json")

