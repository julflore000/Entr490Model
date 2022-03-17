import pandas as pd
import numpy as np
from model import techCommitment
from datetime import datetime

geothermalLCOE = 80
lcoeArray = np.array([44,65,129,26,28,geothermalLCOE])



#emissions in metric ton/MWh, follows same index rules as lcoe above
emissionsArray = np.array([720,1839,0,0,0,0])*0.000453592

#would be in $/lb of CO2
carbonTax = 40

#reading in generation and load data

genData = pd.read_excel("../dataInputs/cleanedGen.xlsx")
loadData = pd.read_excel("../dataInputs/cleanedLoad.xlsx")

#filter out hour ending data col name
energyTechnologies = genData.columns.to_numpy()[1:len(lcoeArray)+1]

dataFileName = "ErcotGenBase"
 

environmentalCost = emissionsArray*carbonTax

maxGeneratingCapacity = np.zeros((len(emissionsArray),len(genData["Coal"])))

for techIndex,techName in zip(range(0,len(lcoeArray)),energyTechnologies):
    maxGeneratingCapacity[techIndex] = genData[techName].to_numpy()


#now getting demand

demand = loadData["ERCOT"].to_numpy()


#now running in batch
for GtLCOE in range(87,116,7):
    print(f"Geothermal LCOE: {GtLCOE}")
    for carbonTax in range(100,201,32):
        print(f"carbon tax: {carbonTax}")
        #assigning unique values
        lcoeArray = np.array([44,65,129,26,28,GtLCOE])
        dataFileName = f"ErcotGenCT{carbonTax}GT{GtLCOE}"
        environmentalCost = emissionsArray*carbonTax
        
        
        techCommitment.main(dataFileName,energyTechnologies,
                    lcoeArray,environmentalCost,carbonTax,
                    maxGeneratingCapacity,
                    demand)