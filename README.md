# Energy Mix Optimization Model
 ENTR 490 optimization model for Dsider


Will optimize a energy system given the next x hours under varying decarbonization scenarios
* Currently setting up model to run test cases

Goal: explore geothermal's role in a decarbonized future through energy optimization case studies and real time data

Information: check out the model formulation: https://github.com/julflore000/unitCommitmentModel/blob/main/modelFormulation.pdf

Data sources:
1. ERCOT load: https://www.ercot.com/gridinfo/load/load_hist
2. ERCOT max generator capacity from: https://www.ercot.com/gridinfo/generation (used max value reached for thermal)
* Note, the generation data accounts for daylight savings time going away on day 3/14/2021 and showing up on 11/7/21 by adding a specific DST value.

* Process for cleaning up generation data
* Since the hist gen is only on 15 minute intervals the data doesn't fully line with the load, therefore after summing up the 15 minute generations across the hour, we then find the percentage of that technology for the total generation in the hour. Once the total generation percentage is calculated, we multiply by the respective load to find the generation of that technology at that hour
* cleanedGen: represents the maximum generation of that technology at that hour. It is assumed thermal tech (coal, gas, nuclear) will not have time dependency, however wind and solar are obviously variable.


