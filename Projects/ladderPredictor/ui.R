#Load packages
library(shiny)
library(shinyWidgets)
library(shinythemes)
library(reactable)

#Create dataframe with starting ladder
#Columns for dataframe
Team <- c("Swifts", "Lightning", "GIANTS", "Fever", "Firebirds", "Magpies", "Thunderbirds", "Vixens")
P <- c(10, 10, 10, 9, 10, 10, 10, 9)
W <- c(7, 7, 6, 7, 4, 3, 3, 2)
D <- c(0, 0, 0, 0, 0, 0, 0, 0)
L <- c(3, 3, 4, 2, 6, 7, 7, 7)
GF <- c(603, 588, 602, 616, 631, 581, 547, 467)
GA <- c(557, 582, 560, 542, 621, 632, 598, 543)
Pts <- c(28, 28, 24, 16, 16, 12, 12, 8)
Per <- round(GF / GA * 100, 2)
#Construct the dataframe
ladderData <- data.frame(Team, P, W, D, L, GF, GA, Pts, Per)

#Set colours for teams
feverCol <- "#00953b"
firebirdsCol <- "#4b2c69"
giantsCol <- "#f57921"
lightningCol <- "#fdb61c"
magpiesCol <- "#494b4a"
swiftsCol <- "#0082cd"
thunderbirdsCol <- "#e54078"
vixensCol <- "#00a68e"

#Set list for generic game labels
gameLabels <- c("G1", "G2", "G3", "G4")

#Set list for remaining rounds
roundLabels <- c("R8", "R11", "R12", "R13", "R14")

#Set list for games within round
matchUpLabels <- list(

  #Round 8
  list(c("Fever", "Vixens")),

  #Round 11
  list(c("Lightning", "GIANTS"), c("Fever", "Firebirds"), c("Vixens", "Magpies"), c("Swifts", "Thunderbirds")),

  #Round 12
  list(c("Lightning", "Thunderbirds"), c("Fever", "Magpies"), c("Vixens", "Firebirds"), c("Swifts", "GIANTS")),

  #Round 13
  list(c("GIANTS", "Fever"), c("Firebirds", "Lightning"), c("Magpies", "Swifts"), c("Thunderbirds", "Vixens")),

  #Round 14
  list(c("Firebirds", "Magpies"), c("Fever", "Thunderbirds"), c("Swifts", "Lightning"), c("GIANTS", "Vixens"))

)

#Set match-up labels to round names
names(matchUpLabels) <- roundLabels

#Create the round tabs and game tabs within these

#Create empty list to store tabs in
matchTabsetList <- list()

for (rr in 1:length(roundLabels)) {

  #Append a list within the broader matchup list for the current round
  #Also rename it to current round
  matchTabsetList[[length(matchTabsetList)+1]] <- list()
  names(matchTabsetList)[length(matchTabsetList)] <- roundLabels[rr]

  #Loop through the games within a round
  for (gg in 1:length(matchUpLabels[rr][[1]])) {

    #Create the tab panel for current game and append to round list
    matchTabsetList[rr][[1]][[length(matchTabsetList[rr][[1]])+1]] <- tabPanel(gameLabels[gg],
                                                                               #Header for game
                                                                               h4(paste(matchUpLabels[rr][[1]][[gg]][1],matchUpLabels[rr][[1]][[gg]][2], sep = ' vs. ')),
                                                                               #Radio button for including game
                                                                               radioButtons(paste(roundLabels[rr],gameLabels[gg], sep = "_"),
                                                                                            "Include?", c("Yes", "No"), selected = "No"),
                                                                               #Slider input for the two teams
                                                                               #Team 1
                                                                               sliderInput(paste(matchUpLabels[rr][[1]][[gg]][1], roundLabels[rr], sep = ""),
                                                                                           paste(matchUpLabels[rr][[1]][[gg]][1], "Score", sep = " "),
                                                                                           value = 0, min = 0, max = 100),
                                                                               #Team 2
                                                                               sliderInput(paste(matchUpLabels[rr][[1]][[gg]][2], roundLabels[rr], sep = ""),
                                                                                           paste(matchUpLabels[rr][[1]][[gg]][2], "Score", sep = " "),
                                                                                           value = 0, min = 0, max = 100)
    )
  }
}



# Define UI for application that draws a histogram
fluidPage(
  
  # #Set theme
  # theme = shinytheme("cosmo"),
  
  #Add css tags
  tags$style(type = 'text/css',
             
             "h4 {font-weight: bold}"),
  
  # Application title
  titlePanel("Super Netball 2021: Ladder Predictor"),
  
  # Sidebar with a slider input for number of bins 
  sidebarLayout(
    
    sidebarPanel(
      
      #Set colours for sliders
      #This is based on match ordering
      setSliderColor(c(feverCol, vixensCol,
                       lightningCol, giantsCol, feverCol, firebirdsCol,
                       vixensCol, magpiesCol, swiftsCol, thunderbirdsCol,
                       lightningCol, thunderbirdsCol, feverCol, magpiesCol,
                       vixensCol, firebirdsCol, swiftsCol, giantsCol,
                       giantsCol, feverCol, firebirdsCol, lightningCol,
                       magpiesCol, swiftsCol, thunderbirdsCol, vixensCol,
                       firebirdsCol, magpiesCol, feverCol, thunderbirdsCol, 
                       swiftsCol, lightningCol, giantsCol, vixensCol),
                     c(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16, 17, 18,
                       19,20,21,22,23,24,25,26,27,28,29,30,31,32, 33, 34)),
      
      #Add tab panel for game/round selection
      tabsetPanel(type = "tabs",
                  
                  #Round 8 panel
                  tabPanel("R8",
                           
                           tabsetPanel(type = "tabs",
                                       
                                       #Game 1
                                       matchTabsetList$R8[[1]]
                                       
                           )
                  ),
                  
                  #Round 11 panel
                  tabPanel("R11",
                           
                           tabsetPanel(type = "tabs",
                                       
                                       #Game 1
                                       matchTabsetList$R11[[1]],
                                       #Game 2
                                       matchTabsetList$R11[[2]],
                                       #Game 3
                                       matchTabsetList$R11[[3]],
                                       #Game 4
                                       matchTabsetList$R11[[4]]
                                       
                           )
                  ),
                  
                  #Round 12 panel
                  tabPanel("R12",
                           
                           tabsetPanel(type = "tabs",
                                       
                                       #Game 1
                                       matchTabsetList$R12[[1]],
                                       #Game 2
                                       matchTabsetList$R12[[2]],
                                       #Game 3
                                       matchTabsetList$R12[[3]],
                                       #Game 4
                                       matchTabsetList$R12[[4]]
                                       
                           )
                  ),
                  
                  #Round 13 panel
                  tabPanel("R13",
                           
                           tabsetPanel(type = "tabs",
                                       
                                       #Game 1
                                       matchTabsetList$R13[[1]],
                                       #Game 2
                                       matchTabsetList$R13[[2]],
                                       #Game 3
                                       matchTabsetList$R13[[3]],
                                       #Game 4
                                       matchTabsetList$R13[[4]]
                                       
                           )
                  ),
                  
                  
                  #Round 14 panel
                  tabPanel("R14",
                           
                           tabsetPanel(type = "tabs",
                                       
                                       #Game 1
                                       matchTabsetList$R14[[1]],
                                       #Game 2
                                       matchTabsetList$R14[[2]],
                                       #Game 3
                                       matchTabsetList$R14[[3]],
                                       #Game 4
                                       matchTabsetList$R14[[4]]
                                       
                           )
                  )
                  
      ),
      
    ),
    
    # Show a plot of the generated distribution
    mainPanel(
      
      #Tab panels for current and predicted ladders
      tabsetPanel(
        
        #Tab for current ladder
        tabPanel("Current Ladder",
                 
                 reactableOutput("currentLadderTable")
                 
        ),
        
        #Tab panel for predicted ladder
        tabPanel("Predicted Ladder",
                 
                 #Add blank header buffer and button for predictions
                 h5(" "),
                 actionButton("runPrediction", "Run Prediction!"),
                 h5(" "),
                 
                 #Add the predicted table
                 reactableOutput("predictedLadderTable")
                 
                 
        )
        
      )
      
    )
  )
)