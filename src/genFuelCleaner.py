from time import daylight
import numpy as np
import pandas as pd
import calendar











#takes input of 15 minute interval generation fuel file and outputs on hourly basis 
#the generation of each of the main fuel types

fileName = "../dataInputs/rawData/IntGenbyFuel2021.xlsx"


monthSheetList = []

#going through and converting to 3 letter
for month in list(calendar.month_name):
    if month == "":
        continue
    monthSheetList.append(month[0:3])

genCategories  = ["Biomass","Coal","Gas","Gas -CC","Hydro","Nuclear","Other","Solar","Wind"]

#dataset worked with
masterDataset = np.zeros((9,24*365))

#one extra row for daylight savings time
excelFileDataset = np.zeros((9,24*365+1))

# for merging single cols together
priorIndex = 0
#going through on a daily basis over the whole year
for month in range(0,12):
    print(month)
    if(month == 10):
        daylightSavingsTime = True
    else:
        daylightSavingsTime = False
        
    monthGen = pd.read_excel(fileName, monthSheetList[month])
    totalDays = calendar.monthrange(2021, month+1)[1]
    
    for hour in range(1,24):
        hourData = np.zeros(totalDays*9)
        #need to sum up the 15 minute intervals
        for period in range(0,4):
            if(period == 0):
                hourStr = f"{hour}:00"
            else:
                hourStr = f"{hour-1}:{15*period}"
            quarterData = monthGen[hourStr].to_numpy()
            hourData += quarterData
                
        resizedArray = np.reshape(hourData,(totalDays,9))
            
            
        if((hour == 1)):
            monthArray = resizedArray
        else:
            monthArray = np.concatenate((monthArray,resizedArray),axis=1)
            
        
    
    #getting next day (0:00) and transposing for array merging
    hourData = np.zeros(totalDays*9)
    #need to sum up the 15 minute intervals
    for period in range(0,4):
        if(period == 0):
            hourStr = "0:00"
        else:
            hourStr = f"23:{15*period}"
        quarterData = monthGen[hourStr].to_numpy()
        hourData += quarterData
    
    resizedArray = np.reshape(hourData,(totalDays,9))
    #adding data on
    monthArray = np.transpose(np.concatenate((monthArray,resizedArray),axis=1))
    
    
    #if daylight savings time is true (in this case the 7th of November), insert one added speical DST entry
    #TO DO: add specific hour of dst (might need to change array)
    if(daylightSavingsTime):
        hourData = np.zeros(9)
        for period in range(0,4):
            if(period == 0):
                hourStr = "02:00 (DST)"
            else:
                hourStr = f"01:{15*period} (DST)"
            quarterData = monthGen[hourStr].to_numpy()
            quarterData  = quarterData[~np.isnan(quarterData)]
            hourData += quarterData
            
        #dont need to transpose/reshape array as will be simply a 1d array in correct format
        singleDaylightHourArray = hourData
        
        
    #now creating one single column dataset for each generator type
    for genType in range(0,9):            
        singleColArray = [None]*(totalDays*24)
        for hour in range(0,24):
            singleColArray[hour::24] = monthArray[genType+hour*9]
        #assigning to final data array
        masterDataset[genType][priorIndex:(priorIndex+len(singleColArray))] = singleColArray

        
    priorIndex += len(singleColArray)



#inserting extra daylight savings hour (will manually remove hour)
for genType in range(0,9):
    excelFileDataset[genType] = np.insert(masterDataset[genType],7442,singleDaylightHourArray[genType])


            
finalDF = pd.DataFrame(np.transpose(excelFileDataset),columns=genCategories)


finalDF.to_excel("../dataInputs/cleanHistGenFormatData.xlsx")


print("done transforming data")