# unitCommitmentModel
 ENTR 490 optimization model


Will optimize a energy system given the next x hours under varying decarbonization scenarios

Goal: explore geothermal's role in a decarbonized future through energy optimization case studies and real time data

Information: check out the model formulation: https://github.com/julflore000/unitCommitmentModel/blob/main/modelFormulation.pdf

Data sources:
1. ERCOT load: https://www.ercot.com/gridinfo/load/load_hist
2. ERCOT fuel sources: 
3. ERCOT Generators from: https://www.eia.gov/electricity/data/eia860/ and then filtered out
* 10M = 0 - 10 minutes
* 1H = 10 minutes - 1 hour
* 12H = 1 hour - 12 hours
* OVER = More than 12 hours

See Layout excel file for generator information:  https://www.eia.gov/electricity/data/eia860/

