#will be using pyomo

from fileinput import filename
from pyomo.environ import *
from pyomo.opt import SolverFactory
from pytest import param
import pandas as pd
import numpy as np
import os.path


class unitCommitment:
    def writeDataFile(data_name,lcoe,envCost,maxGenCap,demand):
        ##writing data file for model instance

        with open('../modelInputs/'+str(data_name)+'.dat', 'w') as f:
            
            #power source set
            f.write('set tech := ')
            for i in range(len(lcoe)):
                f.write('%d ' % i)
            f.write(';\n\n')
            
            #horizon (time) set
            f.write('set horizon := ')
            for i in range(len(demand)):
                f.write('%d ' % i)
            f.write(';\n\n')
 
            
            #capital cost parameter
            f.write('param lcoe := \n')
            for i in range(len(lcoe)):
                if(i != len(lcoe)-1):
                    f.write('%d %d \n' % (i,lcoe[i]))
                else:
                    f.write('%d %d' % (i,lcoe[i]))                    
            f.write(';\n\n')
                         
            
            #env cost parameter
            f.write('param envCost := \n')
            for i in range(len(envCost)):
                if(i != len(envCost)-1):
                    f.write('%d %d \n' % (i,envCost[i]))
                else:
                    f.write('%d %d' % (i,envCost[i]))
            f.write(';\n\n')  


                        
            #max capacity parameter (need special table format as 2d param)
            
            #writing column info
            f.write('param maxCapacity:' + '\t')
            for t in range(0,len(demand)):
                if t != 'name':
                    f.write(str(t) + '\t')
            f.write(':=\n\n')
             #now filling in data for 2d param max capacity
           
            for t in range(0,len(lcoe)):    
                for d in  range(0,len(demand)):
                    #first cell entry in row
                    if d==0:
                        f.write(str(t) + '\t' + str(maxGenCap[t][d]) + '\t') 
                    else:
                        #then filling in other data
                        f.write(str(maxGenCap[t][d]) + '\t')            
                f.write('\n')
            f.write(';\n\n')
            
            

            
            #demand parameter
            f.write('param demand := \n')
            for i in range(len(demand)):
                if(i != len(demand)-1):
                    f.write('%d %d \n' % (i,demand[i]))
                else:
                    f.write('%d %d' % (i,demand[i]))                    
            f.write(';\n\n')
            
        print("Completed data file")     
    
    #def generateData()
            #checks if load file already exisits
    #    fileName = "%s_Load.xlsx" % (datetime.today().strftime('%m_%d_%Y'))
    #    if(exists(fileName)):
            #print("Load file for %s already exits, stopping scraping")
    #    print(exists(fileName))
    
    
    def main(dataFileName,technologyNames,lcoePerTech,envCost,maxGenCap,demandInput):
        
        
        
        
        #### read in data ####
        lcoe = lcoePerTech
        environmentalCost = envCost
        maxGeneratingCapacity = maxGenCap
        demand = demandInput


        # creating optimization model with pyomo
        model = AbstractModel()

        ################### SETS  ###################
        model.tech = RangeSet(0,len(lcoePerTech)-1)
        model.horizon = RangeSet(0,len(demand)-1)

        ################### PARAMETERS  ###################
        model.lcoe = Param(model.tech)
        model.envCost = Param(model.tech)
        model.maxCapacity = Param(model.tech,model.horizon)
        model.demand = Param(model.horizon)


        ################### DECISION VARIABLES  ###################
        model.x = Var(model.tech,model.horizon,domain=NonNegativeReals)




        ################### START OBJECTIVE (min sys costs) ###################
        def minCost_rule(model):

            return sum(sum(model.x[j,t]*(model.lcoe[j]+model.envCost[j]) for t in model.horizon) for j in model.tech)

        model.SystemCost = Objective(rule = minCost_rule, sense = minimize)

        ################### END OBJECTIVE (min sys costs) ###################




        ################### START CONSTRAINTS ###################
        #meeting demand
        def meetDemand_rule(model,t):
            return sum(model.x[j,t] for j in model.tech) >= model.demand[t]
            
        model.meetDemand = Constraint(model.horizon,rule=meetDemand_rule)

        #abiding max generating capacity
        def belowMaxCap_rule(model,j,t):
            return model.x[j,t] <= model.maxCapacity[j,t]

        model.belowCap = Constraint(model.tech,model.horizon,rule=belowMaxCap_rule)


        ################### END CONSTRAINTS ###################





        ################### WRITING DATA ###################
        if(os.path.isfile(f"../modelOutputs/{dataFileName}.dat")):
            print(f"Data file {dataFileName} already exists!\n Skipping loading in data from relevant files")
        else:
            print(f"Data file {dataFileName} does not exist.\n Loading in data from relevant files")
            unitCommitment.writeDataFile(dataFileName,lcoe,
                      environmentalCost,
                      maxGeneratingCapacity,
                      demandInput)
        # load in data for the system
        data = DataPortal()
        data.load(filename=f"../modelInputs/{dataFileName}.dat", model=model)
        instance = model.create_instance(data)

        solver = SolverFactory('glpk')
        result = solver.solve(instance)
        #instance.display()
        
        #saving data into dataframe
        columnNames = technologyNames
            
        #creating dataframe
        df = pd.DataFrame(0, index=np.arange(len(demand)), columns=columnNames)
        
        #assigning generation values to df
        for x,techName in zip(range(len(lcoe)),technologyNames):
            for t in range(len(demand)):
                df[techName][t] = instance.x._data[x,t].value
                
        df.index.name='Timestep'
            
        #saving to excel
        outputFileLocation = "../modelOutputs/outputUnitCommitment.xlsx"
        
        df.to_excel("../modelOutputs/outputUnitCommitment.xlsx")
        
        print(f"Model results saved to: {outputFileLocation}")
        

#results are in plant,time

##   running test   ##
fileName = "test"
energyTechnologies = ["Solar","Gas","Wind"]
lcoe = [10,15,12]
environmentalCost = [0,5,0]
maxGeneratingCapacity = [[0,1,2,3,1,0],[5,5,5,5,5,5],[3,2,1,1,1,3]]
demand = [1,2,3,4,5,6]

unitCommitment.main(fileName,energyTechnologies,
                    lcoe,
                    environmentalCost,
                    maxGeneratingCapacity,
                    demand)

print("test run done!")
