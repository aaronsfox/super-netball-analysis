#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

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
Per <- round(ladderGoalsFor / ladderGoalsAgainst * 100, 2)
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
ui <- fluidPage(
    
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

# Define server logic required to draw a histogram
server <- function(input, output, session) {
    
    
    #Current ladder table output
    output$currentLadderTable <- renderReactable({
        
        reactable(
            
            #Set data
            ladderData,
            
            #Set pagination
            pagination = FALSE,
            
            #Set parameters
            highlight = TRUE,
            searchable = FALSE,
            
            #Set the default sort column
            defaultSorted = c("Pts","Per"),
            defaultSortOrder = "desc",
            
            #Set row style for finalists
            rowStyle = function(index) {
                if (index == 4) list(borderBottom = "2px solid #555")
            },
            
            #Create a list of columns
            columns = list(
                
                #Create the team column
                Team = colDef(name = "Team",
                              sortable = FALSE,
                              style = list(fontSize = "12px", fontWeight = "bold"),
                              headerStyle = list(fontWeight = 700),
                              cell = function(value) {
                                  image <- img(src = sprintf("/Images/%s.png", value), height = "30px", alt = value)
                                  tagList(
                                      div(style = list(display = "inline-block", width = "30px"), image)
                                  )
                                  }
                              ),
                
                #Create games played column
                P = colDef(
                    name = "P",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                ),
                
                #Create wins column
                W = colDef(
                    name = "W",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                ),
                
                #Create draws column
                D = colDef(
                    name = "D",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                ),
                
                #Create losses column
                L = colDef(
                    name = "L",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                ),
                
                #Create goals for column
                GF = colDef(
                    name = "GF",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                ),
                
                #Create goals against column
                GA = colDef(
                    name = "GA",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                ),
                
                #Create points column
                Pts = colDef(
                    name = "Pts",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                ),
                
                #Create percentage column
                Per = colDef(
                    name = "Per",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                    format = colFormat(digits = 2)
                )
                
            ),
            
            #Set reactable options
            showSortIcon = FALSE,
            borderless = TRUE
            
        )
        
    })
    
    
    
    #Generate the predicted ladder dataframe upon clicking the action button
    predictedLadder <- eventReactive(input$runPrediction, {
        
        #Create a new copy of the starting ladder to alter
        ladderPredict <- data.frame(Team, P, W, D, L, GF, GA, Pts, Per)
        
        #Loop through rounds
        for (rr in 1:length(roundLabels)) {
            
            #Loop through games within round
            for (gg in 1:length(matchUpLabels[rr][[1]])) {
                
                #Get the current games radio button value for inclusion
                useGame <- input[[paste(roundLabels[rr],gameLabels[gg], sep = "_")]]
                
                if (useGame == "Yes") {
                    
                    #Get the two team names
                    team1 <- matchUpLabels[rr][[1]][[gg]][1]
                    team2 <- matchUpLabels[rr][[1]][[gg]][2]
                    
                    #Get row indexes for two teams
                    teamInd1 <- which(ladderPredict$Team == team1)
                    teamInd2 <- which(ladderPredict$Team == team2)
                    
                    #Get the two teams slider values
                    score1 <- input[[paste(matchUpLabels[rr][[1]][[gg]][1], roundLabels[rr], sep = "")]]
                    score2 <- input[[paste(matchUpLabels[rr][[1]][[gg]][2], roundLabels[rr], sep = "")]]
                    
                    #Add to each teams played column
                    ladderPredict$P[teamInd1] <- ladderPredict$P[teamInd1] + 1
                    ladderPredict$P[teamInd2] <- ladderPredict$P[teamInd2] + 1
                    
                    #Add goals for and against for the two teams
                    #Goals for
                    ladderPredict$GF[teamInd1] <- ladderPredict$GF[teamInd1] + score1
                    ladderPredict$GF[teamInd2] <- ladderPredict$GF[teamInd2] + score2
                    #Goals against
                    ladderPredict$GA[teamInd1] <- ladderPredict$GA[teamInd1] + score2
                    ladderPredict$GA[teamInd2] <- ladderPredict$GA[teamInd2] + score1
                    
                    #Add to points based on win vs. loss vs. draw
                    if (score1 > score2) {
                        #Give team1 the win + team2 the loss
                        ladderPredict$Pts[teamInd1] <- ladderPredict$Pts[teamInd1] + 4
                        ladderPredict$W[teamInd1] <- ladderPredict$W[teamInd1] + 1
                        ladderPredict$L[teamInd2] <- ladderPredict$L[teamInd2] + 1
                    } else if (score2 > score1) {
                        #Give team2 the win + team1 the loss
                        ladderPredict$Pts[teamInd2] <- ladderPredict$Pts[teamInd2] + 4
                        ladderPredict$W[teamInd2] <- ladderPredict$W[teamInd2] + 1
                        ladderPredict$L[teamInd1] <- ladderPredict$L[teamInd1] + 1
                    } else if (score1 == score2) {
                        #Share the points for a draw
                        ladderPredict$Pts[teamInd1] <- ladderPredict$Pts[teamInd1] + 2
                        ladderPredict$Pts[teamInd2] <- ladderPredict$Pts[teamInd2] + 2
                        ladderPredict$D[teamInd1] <- ladderPredict$D[teamInd1] + 1
                        ladderPredict$D[teamInd2] <- ladderPredict$D[teamInd2] + 1
                    }
                    
                } #end useGame if statement
                
            } #end games loop
            
        } #end rounds loop
        
        #Recalculate percentage
        ladderPredict$Per <- round(ladderPredict$GF / ladderPredict$GA * 100, 2)
        
        #Re-sort dataframe by total points and percentage
        ladderPredict <- ladderPredict[with(ladderPredict, order(-Pts, -Per)), ]
        
        return(ladderPredict)
        
    })
    
    
    
    #Render predicted ladder
    output$predictedLadderTable <- renderReactable({
        
        reactable(
            
            #Set data
            #Grab it from the predict ladder function
            predictedLadder(),
            
            #Set pagination
            pagination = FALSE,
            
            #Set parameters
            highlight = TRUE,
            searchable = FALSE,
            
            #Set the default sort column
            defaultSorted = c("Pts","Per"),
            defaultSortOrder = "desc",
            
            #Set row style for finalists
            rowStyle = function(index) {
                if (index == 4) list(borderBottom = "2px solid #555")
            },
            
            #Create a list of columns
            columns = list(
                
                #Create the team column
                Team = colDef(name = "Team",
                              sortable = FALSE,
                              style = list(fontSize = "12px", fontWeight = "bold"),
                              headerStyle = list(fontWeight = 700),
                              cell = function(value) {
                                  image <- img(src = sprintf("/Images/%s.png", value), height = "30px", alt = value)
                                  tagList(
                                      div(style = list(display = "inline-block", width = "30px"), image)
                                  )
                              }
                ),
                
                #Create games played column
                P = colDef(
                    name = "P",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                ),
                
                #Create wins column
                W = colDef(
                    name = "W",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                ),
                
                #Create draws column
                D = colDef(
                    name = "D",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                ),
                
                #Create losses column
                L = colDef(
                    name = "L",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                ),
                
                #Create goals for column
                GF = colDef(
                    name = "GF",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                ),
                
                #Create goals against column
                GA = colDef(
                    name = "GA",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                ),
                
                #Create points column
                Pts = colDef(
                    name = "Pts",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                ),
                
                #Create percentage column
                Per = colDef(
                    name = "Per",
                    sortable = FALSE,
                    defaultSortOrder = "desc",
                    align = "center",
                    class = "cell number",
                    headerStyle = list(fontWeight = 700),
                    format = colFormat(digits = 2)
                )
                
            ),
            
            #Set reactable options
            showSortIcon = FALSE,
            borderless = TRUE
            
        )
        
    })
    
    
}

# Run the application 
shinyApp(ui = ui, server = server)
