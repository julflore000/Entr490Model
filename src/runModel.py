import pandas as pd
import numpy as np
from model import techCommitment
from datetime import datetime


#first starting with simply LCOE for energy cost
#from: https://www.lazard.com/media/451419/lazards-levelized-cost-of-energy-version-140.pdf



## main technologies by index
# 0-CC: Natural Gas Fired Combined Cycle" 'Natural Gas Fired Combustion Turbine'
# 1-ST: 'Conventional Steam Coal', 'Natural Gas Steam Turbine'
# 2-NU: 'Nuclear'
# 3-W: onshore wind
# 4-S: solar
# 5-GT: geothermal energy<- still need to input possible generation
#geothermal LCOE is last in LCOE array
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


# for tracking elapsed time
startRun = datetime.now()
start_time = startRun.strftime("%H:%M:%S")
print("Run started:", start_time)

techCommitment.main(dataFileName,energyTechnologies,
                    lcoeArray,environmentalCost,carbonTax,
                    maxGeneratingCapacity,capacityFactors,
                    demand)


#getting end time
endRun = datetime.now()
end_time = endRun.strftime("%H:%M:%S")
print("Run over:", end_time)

#printing total model runtime
print("Total model time took: ",str(endRun-startRun))