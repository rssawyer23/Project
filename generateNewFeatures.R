
#input: actiontable
#output: actiontable with new hint features
createHintFeatures <- function(data)
{
  data <- data[order(data$studentID,data$dateTime),]
  #get all instances of a message in the hintGiven column
  temp<- data[data$hintGiven != "",]
  
  #remove worked examples
  temp<- temp[temp$rule != "next",]
  temp <- temp[temp$rule != "prev",]
  
  #remove hint with content 'undefined' and 'no hint available'
  badHint<-c("undefined", "No hint available for this step.", "Conclusion Reached!")
  temp<-temp[!temp$hintGiven %in% badHint,]
  
  #remove hintCount == 0; means student didn't see the hint
  temp<- temp[temp$hintCount != 0,]
  
  #remove duplicate hint request on the same state
  #temp<-temp[!(temp$rule %in% "get" & duplicated(temp[,c("studentID", "rule", "preState", "currPrb","hintGiven")])),]
  
  #remove duplicate hint - forced - on same state
  #temp<-temp[!(duplicated(temp[,c("studentID", "rule", "preState", "currPrb","hintGiven")])),]
  
  
  #all hints received 
  #set hintReceived equal to 1 to represent when a actual hint was given
  temp$hintReceived <- 1
  data<- merge(data,temp, all=TRUE)
  data[is.na(data$hintReceived),]$hintReceived <- 0
  
  temp1<- temp 
  #all hints forced
  temp <- temp[temp$rule != "get",]
  
  temp$proactiveHintReceived <- 1
  data<- merge(data,temp, all=TRUE)
  data[is.na(data$proactiveHintReceived),]$proactiveHintReceived <- 0
  temp<- temp1
  
  #all hints Requested
  temp <- temp[temp$rule == "get",]
  
  temp$hintRequested <- 1
  data<- merge(data,temp, all=TRUE)
  data[is.na(data$hintRequested),]$hintRequested <- 0

  
  data <- data[order(data$studentID,data$dateTime),] 
  data$cumul_hintsReceived<- ave(data$hintReceived,data$studentID,FUN=cumsum)
  data$cumul_proactiveHintsReceived<- ave(data$proactiveHintReceived,data$studentID,FUN=cumsum)
  data$cumul_hintsRequested<- ave(data$hintRequested,data$studentID,FUN=cumsum)
  
  
  
  temp <- data
  
  
  
}


#step is when a student correctly changes the solution (not including deletes)
createStepCount<- function(data)
{
  temp<-data
  #step is 0 for actions that aren't considered steps and 1 for steps
  temp$step <- 0

  temp[(temp$action == 5 | temp$action == 3) & temp$derived != "null",]$step<- 1
  
  temp <- temp[order(temp$studentID,temp$dateTime),]
  temp$cumul_steps<- ave(temp$step,temp$studentID,temp$currPrb,FUN=cumsum)
  temp$cumul_steps_ws<- ave(temp$step,temp$studentID,FUN=cumsum)
  
  temp<- temp
  
}
#TODO
#step is when a student correctly changes the solution including deletes
createStepCountwithDelete<- function(data)
{
  temp<-data
  #step is 0 for actions that aren't considered steps and 1 for steps
  temp$stepwD <- 0
  
  temp[(temp$action == 5 | temp$action == 3 | temp$action == 6) & temp$derived != "null",]$stepwD<- 1
  
  temp <- temp[order(temp$studentID,temp$dateTime),]
  temp$cumul_stepswD<- ave(temp$stepwD,temp$studentID,temp$currPrb,FUN=cumsum)
  temp$cumul_stepswD_ws<- ave(temp$stepwD,temp$studentID,FUN=cumsum)
  temp<- temp
  
}

#step is when a student attempts to change the solution (includes wrong applications)
createStepCount_all<- function(data)
{
  temp<-data
  #step is 0 for actions that aren't considered steps and 1 for steps
  temp$step_all <- 0
  
  temp[temp$action == 3 | temp$action == 5 | temp$action == 6,]$step_all<- 1
  
  temp <- temp[order(temp$studentID,temp$dateTime),]
  temp$cumul_steps_all<- ave(temp$step_all,temp$studentID,temp$currPrb,FUN=cumsum)
  temp$cumul_steps_all_ws<- ave(temp$step_all,temp$studentID,FUN=cumsum)
  temp<- temp
  
}

#bad step is when the student tried to apply a rule, but did it incorrectly -- includes wrong rule applications and entering in wrong in the prompt box
createStepCount_badStep<- function(data)
{
  temp<-data
  #step is 0 for actions that aren't considered steps and 1 for steps
  temp$step_bad <- 0
  
  temp[(temp$action == 3 | temp$action == 5 | temp$action == 6) & (temp$error ==1 | temp$error ==2 | temp$error == 10),]$step_bad<- 1
  
  temp <- temp[order(temp$studentID,temp$dateTime),]
  temp$cumul_steps_bad<- ave(temp$step_bad,temp$studentID,temp$currPrb,FUN=cumsum)
  temp$cumul_steps_bad_ws<- ave(temp$step_bad,temp$studentID,FUN=cumsum)
  temp<- temp
  
}

#time between steps
#This is the cumulative step time(which is really between every action) between steps 
#may have bugs if step time has bugs
createStepTime<- function(data)
{
  data <- data[order(data$studentID,data$dateTime),]
  temp<-data
  temp$cumul_stepTime<- ave(temp$stepTime,temp$studentID,temp$currPrb,temp$cumul_steps,FUN=cumsum)
  temp<-temp
  
}

#time between steps
createStepTime_all<- function(data)
{
  data <- data[order(data$studentID,data$dateTime),]
  temp<-data
  temp$cumul_stepTime_all<- ave(temp$stepTime,temp$studentID,temp$currPrb,temp$cumul_steps_all,FUN=cumsum)
  temp<-temp
}

#time between steps
createStepTime_wD<- function(data)
{
  data <- data[order(data$studentID,data$dateTime),]
  temp<-data
  temp$cumul_stepTime_wD<- ave(temp$stepTime,temp$studentID,temp$currPrb,temp$cumul_stepswD,FUN=cumsum)
  temp<-temp
}

#time between steps
createStepTime_bad<- function(data)
{
  data <- data[order(data$studentID,data$dateTime),]
  temp<-data
  temp$cumul_stepTime_bad<- ave(temp$stepTime,temp$studentID,temp$currPrb,temp$cumul_steps_bad,FUN=cumsum)
  temp<-temp
}




createProblemFeatures<-function(data)
{
  #problemDifficult: represents the prof path
  data <- data[order(data$studentID,data$dateTime),]
  temp <- data
  temp$problemDifficulty <- 0
  temp[substring(temp$currPrb,3,3) == 0,]$problemDifficulty <- 1 #level 1
  temp[substring(temp$currPrb,3,3) == 1,]$problemDifficulty<- 2 #hard
  temp[substring(temp$currPrb,3,3) == "-",]$problemDifficulty<- 0 #easy

  temp$easyProblem<- 0
  temp[substring(temp$currPrb,3,3) == "-" & temp$problemType == "PS",]$easyProblem<- 1 #easy
  
  temp$difficultProblem<- 0
  temp[substring(temp$currPrb,3,3) == "1" & temp$problemType == "PS",]$difficultProblem<- 1 #hard
  
  temp$easyWE<- 0
  temp[substring(temp$currPrb,3,3) == "-" & temp$problemType == "WE",]$easyWE<- 1 #easy
  
  temp$difficultWE<- 0
  temp[substring(temp$currPrb,3,3) == "1" & temp$problemType == "WE",]$difficultWE<- 1 #hard
  temp<-temp
  #f4: cumulative of easy problems solved
  #f5: cumulative of easy WE solved
  #f6: cumulative of difficult problems solved
  #f7: cumulative of difficult WE solved
  
  temp <- temp[order(temp$studentID,temp$dateTime),]
  data<- temp
  temp<- temp[!(duplicated(temp[,c("studentID","currPrb")])),]
  temp$cumul_easyProblem<- ave(temp$easyProblem,temp$studentID,FUN=cumsum)
  temp<-temp[,c("studentID","currPrb","cumul_easyProblem")]
  temp<-merge(data,temp, by=c("studentID","currPrb"))
  data<-temp
  data <- data[order(data$studentID,data$dateTime),]
  
  temp<-data
  temp<- temp[!(duplicated(temp[,c("studentID","currPrb")])),]
  temp$cumul_easyWE<- ave(temp$easyWE,temp$studentID,FUN=cumsum)
  temp<-temp[,c("studentID","currPrb","cumul_easyWE")]
  temp<-merge(data,temp,by=c("studentID","currPrb"))
  data<-temp
  data <- data[order(data$studentID,data$dateTime),]
  
  temp<- data
  temp<- temp[!(duplicated(temp[,c("studentID","currPrb")])),]
  temp$cumul_difficultProblem<- ave(temp$difficultProblem,temp$studentID,FUN=cumsum)
  temp<-temp[,c("studentID","currPrb","cumul_difficultProblem")]
  temp<-merge(data,temp, by=c("studentID","currPrb"))
  data<-temp
  data <- data[order(data$studentID,data$dateTime),]
  
  
  temp<- data
  temp<- temp[!(duplicated(temp[,c("studentID","currPrb")])),]
  temp$cumul_difficultWE<- ave(temp$difficultWE,temp$studentID,FUN=cumsum)
  temp<-temp[,c("studentID","currPrb","cumul_difficultWE")]
  temp<-merge(data,temp,by=c("studentID","currPrb"))
  data<-temp
  data <- data[order(data$studentID,data$dateTime),]

  
  #percentageDiffPS: percentage of diff PS out of all PS solved at that point
  #percentageDiffWE: percentage of diff WE out of all WE solved at that point
  #percentageWE: percentage of WE out of WE+PS solved at that point
  #percentageDiff: number of difficult problems(PS and WE) out of all problems
  temp<-data
  
  temp$percentageDiffPS <- (temp$cumul_difficultProblem)/(temp$cumul_easyProblem + temp$cumul_difficultProblem)
  temp[is.nan(temp$percentageDiffPS),]$percentageDiffPS <- 0
  temp$percentageDiffWE <-(temp$cumul_difficultWE)/(temp$cumul_easyWE + temp$cumul_difficultWE)
  temp[is.nan(temp$percentageDiffWE),]$percentageDiffWE <- 0
  temp$percentageWE <- (temp$cumul_easyWE+temp$cumul_difficultWE)/(temp$cumul_easyProblem+temp$cumul_easyWE + temp$cumul_difficultProblem + temp$cumul_difficultWE)
  temp[is.nan(temp$percentageWE),]$percentageWE <- 0
  temp$percentageDiff <- (temp$cumul_difficultProblem+temp$cumul_difficultWE)/(temp$cumul_easyProblem+temp$cumul_easyWE + temp$cumul_difficultProblem + temp$cumul_difficultWE)
  temp[is.nan(temp$percentageDiff),]$percentageDiff <- 0
  temp <- temp[order(temp$studentID,temp$dateTime),]
  temp<-temp
}

replaceInteractionID<-function(data)
{
  data$temp <- 1
  data <- data[order(data$studentID,data$dateTime),]
  data$newInteraction<- ave(data$temp,data$studentID,FUN=cumsum)
  data <- data[,!(colnames(data) %in% c("interaction"))]
  temp<- data
}

createSkipCount<-function(data)
{
  data$skip <- 0
  data <- data[order(data$studentID,data$dateTime),]
  data[(data$action == 10),]$skip<- 1
  
  data$skipCount<- ave(data$skip,data$studentID,FUN=cumsum)
  
  temp<-data
}

createRestartCount<-function(data)
{
  data$restart <- 0
  data <- data[order(data$studentID,data$dateTime),]
  
  data[(data$action == 9),]$skip<- 1
  data$restartCount<- ave(data$restart,data$studentID,FUN=cumsum)
  
  temp<-data
}

createViewRuleDescriptionCount<-function(data)
{
  data$view <- 0
  data <- data[order(data$studentID,data$dateTime),]
  data[(data$action == 4),]$view<- 1
  data$viewCount<- ave(data$view,data$studentID,FUN=cumsum)
  data$viewCount_prb<- ave(data$view,data$studentID,data$currPrb,FUN=cumsum)
  
  temp<-data
}

createSelectNodeCount<-function(data)
{
  data$select <- 0
  data <- data[order(data$studentID,data$dateTime),]
  data[(data$action == 1),]$select<- 1
  data$selectCount<- ave(data$select,data$studentID,FUN=cumsum)
  data$SelectCount_prb<- ave(data$select,data$studentID,data$currPrb,FUN=cumsum)
  
  temp<-data
}

createDeSelectNodeCount<-function(data)
{
  data$deselect <- 0
  data <- data[order(data$studentID,data$dateTime),]
  data[(data$action == 2),]$deselect<- 1
  data$deSelectCount<- ave(data$deselect,data$studentID,FUN=cumsum)
  data$deSelectCount_prb<- ave(data$deselect,data$studentID,data$currPrb,FUN=cumsum)
  temp<-data
}


createAllStats<- function(data)
{
  data<-replaceInteractionID(data)
  data<-createHintFeatures(data)
  data<-createProblemFeatures(data)
  data<- createStepCount(data)
  data<- createStepCountwithDelete(data)
  data<- createStepCount_all(data)
  data<- createStepCount_badStep(data)
  data<-createStepTime(data)
  data<-createStepTime_all(data)
  data<-createStepTime_wD(data)
  data<-createStepTime_bad(data)
  data<-createSkipCount(data)
  data<-createRestartCount(data)
  data<-createViewRuleDescriptionCount(data)
  data<-createSelectNodeCount(data)
  data<-createDeSelectNodeCount(data)
}


