import pandas as pd
import numpy as np
from model import techCommitment
from datetime import datetime

geothermalLCOE = 100
lcoeArray = np.array([44,65,129,26,28,geothermalLCOE])



#emissions in lb/MWh, follows same index rules as lcoe above
emissionsArray = np.array([720,1839,0,0,0,0])*0.000453592

#in $/metric ton of CO2
carbonTax = 40

#reading in generation and load data

genData = pd.read_excel("../dataInputs/cleanedGen.xlsx")
loadData = pd.read_excel("../dataInputs/cleanedLoad.xlsx")

#filter out hour ending data col name
energyTechnologies = genData.columns.to_numpy()[1:len(lcoeArray)+1]

dataFileName = f"ErcotGenCT{carbonTax}GT{geothermalLCOE}"
 

environmentalCost = emissionsArray*carbonTax

maxGeneratingCapacity = np.zeros((len(emissionsArray),len(genData["Coal"])))

#capacity factor array for the two variable generation technologies (wind and solar)
capacityFactors = np.zeros((2,len(genData["Coal"])))

for techIndex,techName in zip(range(0,len(lcoeArray)),energyTechnologies):
    maxGeneratingCapacity[techIndex] = genData[techName].to_numpy()
    if(techName == "Wind"):
        capacityFactors[0] = genData[techName].to_numpy()
    elif(techName == "Solar"):
        capacityFactors[1] = genData[techName].to_numpy()
        


#now getting demand

demand = loadData["ERCOT"].to_numpy()

#now running in batch
for GtLCOE in [80,100,115]:
    print(f"Geothermal LCOE: {GtLCOE}")
    for carbonTax in [100,200]:
        print(f"carbon tax: {carbonTax}")
        #assigning unique values
        lcoeArray = np.array([44,65,129,26,28,GtLCOE])
        dataFileName = f"ErcotGenCT{carbonTax}GT{GtLCOE}"
        environmentalCost = emissionsArray*carbonTax
        
        
        techCommitment.main(dataFileName,energyTechnologies,
                    lcoeArray,environmentalCost,carbonTax,
                    maxGeneratingCapacity,capacityFactors,
                    demand)