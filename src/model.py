#will be using pyomo

from fileinput import filename
from pyomo.environ import *
from pyomo.opt import SolverFactory
from pytest import param
import pandas as pd
import numpy as np

class unitCommitment:
    def writeDataFile(data_name,genCost,varCost,envCost,maxGenCap,demand):
        ##writing data file for model instance

        with open(''+str(data_name)+'.dat', 'w') as f:
            
            #plant set
            f.write('set plant := ')
            for i in range(len(genCost)):
                f.write('%d ' % i)
            f.write(';\n\n')
            
            #horizon (time) set
            f.write('set horizon := ')
            for i in range(len(demand)):
                f.write('%d ' % i)
            f.write(';\n\n')
            
            #capital cost parameter
            f.write('param capCost := \n')
            for i in range(len(genCost)):
                if(i != len(genCost)-1):
                    f.write('%d %d \n' % (i,genCost[i]))
                else:
                    f.write('%d %d' % (i,genCost[i]))                    
            f.write(';\n\n')
                        
            #operating cost parameter
            f.write('param opCost := \n')
            for i in range(len(varCost)):
                if(i != len(varCost)-1):
                    f.write('%d %d \n' % (i,varCost[i]))
                else:
                    f.write('%d %d' % (i,varCost[i]))                    
            f.write(';\n\n')    
            
            #env cost parameter
            f.write('param envCost := \n')
            for i in range(len(envCost)):
                if(i != len(envCost)-1):
                    f.write('%d %d \n' % (i,envCost[i]))
                else:
                    f.write('%d %d' % (i,envCost[i]))
            f.write(';\n\n')  
                        
            #max capacity parameter
            f.write('param maxCapacity := \n')
            for i in range(len(maxGenCap)):
                if(i != len(maxGenCap)-1):
                    f.write('%d %d \n' % (i,maxGenCap[i]))
                else:
                    f.write('%d %d' % (i,maxGenCap[i]))                    
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
        
    def main(genCapCost,varOpCost,envCost,maxGenCap,demandInput):
        #### read in data ####
        #parameters
        generatorCapitalCost = genCapCost
        variableOperatingCost = varOpCost
        environmentalCost = envCost
        maxGeneratingCapacity = maxGenCap
        demand = demandInput


        # creating optimization model with pyomo
        model = AbstractModel()

        #SETS
        model.plant = RangeSet(0,len(generatorCapitalCost)-1)
        model.horizon = RangeSet(0,len(demand)-1)


        #PARAMETERS
        model.capCost = Param(model.plant)
        model.opCost = Param(model.plant)
        model.envCost = Param(model.plant)
        model.maxCapacity = Param(model.plant)
        model.demand = Param(model.horizon)


        #DECISION VARIABLES
        model.x = Var(model.plant,model.horizon,domain=NonNegativeReals)
        model.i = Var(model.plant,model.horizon,domain=Binary)


        #OBJECTIVE (minimize cost)
        def minCost_rule(model):
            return sum(sum(model.x[j,t]*(model.opCost[j]+model.envCost[j]) + model.i[j,t]*(model.capCost[j]) for t in model.horizon) for j in model.plant)

        model.SystemCost = Objective(rule = minCost_rule, sense = minimize)

        #CONSTRAINTS
        #meeting demand
        def meetDemand_rule(model,t):
            return sum(model.x[j,t] for j in model.plant) >= model.demand[t]
            
        model.meetDemand = Constraint(model.horizon,rule=meetDemand_rule)

        #abiding max generating capacity
        def belowMaxCap_rule(model,j,t):
            return model.x[j,t] <= model.i[j,t]*model.maxCapacity[j]

        model.belowCap = Constraint(model.plant,model.horizon,rule=belowMaxCap_rule)

        unitCommitment.writeDataFile("data",generatorCapitalCost,
                      variableOperatingCost,environmentalCost,
                      maxGeneratingCapacity,demandInput)

        # load in data for the system
        data = DataPortal()
        data.load(filename="data.dat", model=model)
        instance = model.create_instance(data)

        solver = SolverFactory('glpk')
        result = solver.solve(instance)
        #instance.display()
        
        #saving data into dataframe
        columnNames = []
        for i in range(len(genCapCost)):
            columnNames.append("Generator %d" % (i+1))
            
        #creating dataframe
        df = pd.DataFrame(0, index=np.arange(len(demand)), columns=columnNames)
        
        #assigning generation values to df
        for x in range(len(genCapCost)):
            for t in range(len(demand)):
                df[("Generator %d" % (x+1))][t] = instance.x._data[x,t].value
                
        df.index.name='Timestep'
            
        #saving to excel
        df.to_excel("outputUnitCommitment.xlsx")
        

#results are in plant,time

##   running test   ##
genCapCost = [1,2,3,4]
variableOperatingCost = [3,4,5,6]
environmentalCost = [1,2,3,4]
maxGeneratingCapacity = [2,3,4,5]
demand = [1,2,3,4]

unitCommitment.main(genCapCost,variableOperatingCost,environmentalCost,maxGeneratingCapacity,demand)