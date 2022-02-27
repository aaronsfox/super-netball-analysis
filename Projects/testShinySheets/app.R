#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(googlesheets4)

# Define UI for application that draws a histogram
ui <- fluidPage(
    
    #Create a few test dropdown boxes
    selectInput("team1", "Select team", c("", "Team 1", "Team 2", "Team 3")),
    selectInput("team2", "Select team", c("", "Team 1", "Team 2", "Team 3")),
    selectInput("team3", "Select team", c("", "Team 1", "Team 2", "Team 3")),
    
    #Action button to save results
    actionButton("saveResults", "Save!")
    
)

# Define server logic required to draw a histogram
server <- function(input, output) {

    #Save data to sheet on click
    eventReactive(input$saveResults, {
        
        #Convert drop down responses to dataframe
        df <- data.frame(team1, team2, team3)
        
        #Output to google sheets
        gSheet <- gs4_get("https://docs.google.com/spreadsheets/d/1HnbVsPpXqMhyvtNzwyUc_BOp6v2Eg01USEDgHUidpxw/edit?usp=sharing")
        sheet_append(gSheet , data = df)
        
        #
        
    })
    
}

# Run the application 
shinyApp(ui = ui, server = server)
