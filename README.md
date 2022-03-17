# Energy Mix Optimization Model
 ENTR 490 optimization model for Geothermal Case Study


Will optimize a energy system given the next x hours under varying decarbonization scenarios
* Model is set up to run various carbon tax scenarios: now working on geothermal capacity and scenario identifications

Goal: explore geothermal's role in a decarbonized future through energy optimization case studies and real time data

Information: check out the model formulation: https://github.com/julflore000/unitCommitmentModel/blob/main/modelFormulation.pdf

Data sources:
1. ERCOT load: https://www.ercot.com/gridinfo/load/load_hist
2. ERCOT max generator capacity from: https://www.ercot.com/gridinfo/generation (used max value reached for thermal)
* Note, the generation data accounts for daylight savings time going away on day 3/14/2021 and showing up on 11/7/21 by adding a specific DST value.

* Process for cleaning up generation data
* Since the hist gen is only on 15 minute intervals the data doesn't fully line with the load, therefore after summing up the 15 minute generations across the hour, we then find the percentage of that technology for the total generation in the hour. Once the total generation percentage is calculated, we multiply by the respective load to find the generation of that technology at that hour
* cleanedGen: represents the maximum generation of that technology at that hour. It is assumed thermal tech (coal, gas, nuclear) will not have time dependency, however wind and solar are obviously variable.


# Model Results

* See excel sheet for geothermal interacting with NG under LCOE and carbon tax
* Nuclear never deployed as $129 is too high even with highest geothermal LCOE ($115)
* In simple arithmetic, we are able to see when geothermal is deployed vs NG
* Geothermal deployed when LCOE < NG LCOE + Env cost
* Model inputs
    * NG LCOE = 44
    * Then if given the geothermal LCOE of say 115
    * required env cost (which is equal to pollution*carbonTax which for NG = 0.326587*carbonTax)
    * Then carbonTax = (115-44)/.32 ~= $220
    * See spreadsheet in modelOutputs geothermalDeployedConditions.xlsx for given carbonTax and geothermal LCOE for it to be widely deployed

