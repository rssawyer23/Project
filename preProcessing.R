#This file contains all data-preprocessing functions

#This function removes collaborators (students who worked together on DT, which could affect behavior)
removeCollabs<-function(data, collabs)
{
  data <- data[!data$studentID %in% collabs$studentID,]
}

#Removes columns that have all identical values and columns "course" and "collaborators"
removeCols<- function(data)
{
  colsToRemove <- list()
  for(i in 1:ncol(data))
  {
    temp <- data
   
    #temp <- temp[temp[,i]  != 0,]
    #if(nrow(temp) == 0)
    if(dim(table(temp[,i])) == 1)
    {
      colsToRemove <- c(colsToRemove, colnames(temp[i]))
    }
  }
  #remove those columns
  data <- data[,!(colnames(data) %in% colsToRemove)]
  data <- data[,!(colnames(data) %in% c("collaborators","course", "RLPolicy", "RLPolicyType","IMMED_easyProblemCountSolved","IMMED_NewLevel","PPType"))]
  temp <- data
}

removeStudents<- function(data)
{
  temp <- data.frame(unclass(table(data$studentID)))
  temp <- temp[temp[[1]] < 100,]
  temp <- rownames(temp)
  temp <- data[!(data$studentID %in% temp),] 
  temp <- droplevels(temp)
}


#combines all pre-processing functions
preProcessing <- function(data,collabs)
{
  temp <- removeCollabs(data,collabs)
  temp <- removeCols(temp)
  temp <- removeStudents(temp)
  
}