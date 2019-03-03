#loading required packages
require(xlsx)

#setting working directory
#THIS SHOULD BE A FOLDER THAT !!ONLY!! CONTAINS CHEMICAL DATA EXCEL SHEETS FOR YOUR FLOWER SAMPLES
setwd("C:/Users/Theresa/Documents/Di Stilio Lab/data-Marie database") #CHANGE filepath to appropriate folder

#loading in dataframe (df) of n-alkane RTs, # of carbons, and names under the Jeff orchid method
#CHANGE filepath to location of this csv
alkanes_for_Kovats <- read.csv("C:/Users/Theresa/Documents/Di Stilio Lab/JEFFMETHOD_alkanes_for_Kovats2.csv")


###############################################################################################
#FUNCTIONS FOR DATA ANALYSIS!
#Running these functions by themselves won't do any of the analysis, but will allow R to store 
#them as functions that you can call on your data.
#To do this, highlight the full text of these functions and then hit ctrl+R to
#store these functions.
###############################################################################################

##returns Kovats index for a compound given the RT of the unknown compound (RT.unknown) and 
##a dataframe (alkane.df) of n-alkane retention times for your particular run method (column heading = RT)
##and number of carbons each contains (column heading= number of carbons; number.of.carbons in R).
##For use with temperature programmed chromatography
get_Kovats_index <- function(RT.of.unknown, alkane.df){
  smaller.alkane.row<-max(which(alkane.df$RT < RT.of.unknown))
  smaller.alkane.n<-alkane.df$number.of.carbons[smaller.alkane.row]
  smaller.alkane.RT<-alkane.df$RT[smaller.alkane.row]
  larger.alkane.row<-min(which(alkane.df$RT>RT.of.unknown))
  larger.alkane.n<-alkane.df$number.of.carbons[larger.alkane.row]
  larger.alkane.RT<-alkane.df$RT[larger.alkane.row]
  Kovats<-100*(smaller.alkane.n + (larger.alkane.n - smaller.alkane.n)*((RT.of.unknown-smaller.alkane.RT)/(larger.alkane.RT-smaller.alkane.RT)))
  return(Kovats)
}

###a function to go through each row in an individual excel spreadsheet of analytical chem data
###outputted by Agilent Chemstation (chemstation.excel) and find Kovats indices for all rows where there
###where no hits, or where hit percentage is below a specified number (percentage.threshold).
###also input spreadsheet of alkanes, number of carbons, and their RTs for calculating Kovats indices (alkane.df)


apply_Kovats_to_chem_sheet<-function(chemstation.excel.filename, alkane.df, percentage.threshold){
  chem.df<-read.xlsx(chemstation.excel.filename, sheetName="LibRes", startRow=9) #reads excel sheet into dataframe
  chem.df<-chem.df[which(is.na(chem.df$RT..min.)==FALSE),]#retains only entries associated with an RT (1st hits and also lines with no hits)
  chem.df$Hit.Name<-as.vector(chem.df$Hit.Name)
  indices.to.calc.Kovats<- which(chem.df$RT..min. < max(alkane.df$RT) & chem.df$RT..min. > min(alkane.df$RT)  & (chem.df$Quality < percentage.threshold | is.na(chem.df$Quality ))) 
  
  for (i in indices.to.calc.Kovats){
    chem.df$Hit.Name[i]<- get_Kovats_index(RT.of.unknown=chem.df$RT..min.[i], alkane.df=alkane.df)  
  } 
  #print(chem.df)
  #if %match (quality column) is lower than the percentage threshold, 
    #or if %match is NA (meaning there are no matches), then find the Kovats index and replace the hit name with that number
  filename<-strsplit(chemstation.excel.filename, ".xls")[[1]]  #splits file name so it does not have .xls file extension
  write.csv(chem.df, file=paste(filename, "_KOVATS.csv", sep="")) 
  #writes a csv of the new file, with Kovats in place, to the same working directory
  #with same filename as before, but with _KOVATS added to the end
}

################################################################################################
#ACTUALLY calling the function stored above on each of the chem excel files in your working
#directory!
#Just highlight everything below then hit ctrl+R to execute
#When it is done running, you should have a new csv for each of your excel files named
# (name_of_excel)_KOVATS.csv
################################################################################################

all.files<-list.files() #lists all files in your working directory; should be all of your chemstation excel files
percentage.threshold<-90 #you can change the percentage threshold to whatever you like.

for (i in all.files){
  apply_Kovats_to_chem_sheet(chemstation.excel.filename=i,alkane.df=alkanes_for_Kovats,
                             percentage.threshold=percentage.threshold) 
}



