#will be using pyomo

from fileinput import filename
from pyomo.environ import *
from pyomo.opt import SolverFactory
from pytest import param
import pandas as pd
import numpy as np
from os.path import exists

class unitCommitment:
    def writeDataFile(data_name,genCost,varCost,envCost,startUpCost,rampRate,maxGenCap,minGenCap,demand):
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
 
             #ramp period set
            f.write('set rampPeriod := ')
            for i in range(1,len(demand)):
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
 
            #startup cost parameter
            f.write('param startUpCost := \n')
            for i in range(len(startUpCost)):
                if(i != len(startUpCost)-1):
                    f.write('%d %d \n' % (i,startUpCost[i]))
                else:
                    f.write('%d %d' % (i,startUpCost[i]))
            f.write(';\n\n') 

            #ramp rate parameter
            f.write('param rampRate := \n')
            for i in range(len(rampRate)):
                if(i != len(rampRate)-1):
                    f.write('%d %d \n' % (i,rampRate[i]))
                else:
                    f.write('%d %d' % (i,rampRate[i]))
            f.write(';\n\n') 
                        
            #max capacity parameter
            f.write('param maxCapacity := \n')
            for i in range(len(maxGenCap)):
                if(i != len(maxGenCap)-1):
                    f.write('%d %d \n' % (i,maxGenCap[i]))
                else:
                    f.write('%d %d' % (i,maxGenCap[i]))                    
            f.write(';\n\n')
 
            #min capacity parameter
            f.write('param minCapacity := \n')
            for i in range(len(minGenCap)):
                if(i != len(minGenCap)-1):
                    f.write('%d %d \n' % (i,minGenCap[i]))
                else:
                    f.write('%d %d' % (i,minGenCap[i]))                    
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
    
    
    def main(genCapCost,varOpCost,envCost,startUpCost,rampRate,maxGenCap,minGenCap,demandInput):
        #### read in data ####
        generatorCapitalCost = genCapCost
        variableOperatingCost = varOpCost
        environmentalCost = envCost
        maxGeneratingCapacity = maxGenCap
        minGeneratingCapacity = minGenCap
        demand = demandInput


        # creating optimization model with pyomo
        model = AbstractModel()

        ################### SETS  ###################
        model.plant = RangeSet(0,len(generatorCapitalCost)-1)
        model.horizon = RangeSet(0,len(demand)-1)
        model.rampPeriod = RangeSet(1,len(demand)-1)

        ################### PARAMETERS  ###################
        model.capCost = Param(model.plant)
        model.opCost = Param(model.plant)
        model.envCost = Param(model.plant)
        model.startUpCost = Param(model.plant)
        model.rampRate = Param(model.plant)
        model.maxCapacity = Param(model.plant)
        model.minCapacity = Param(model.plant)
        model.demand = Param(model.horizon)


        ################### DECISION VARIABLES  ###################
        model.x = Var(model.plant,model.horizon,domain=NonNegativeReals)
        model.i = Var(model.plant,model.horizon,domain=Binary)
        model.s = Var(model.plant,model.rampPeriod,domain=Binary)




        ################### START OBJECTIVE (min sys costs) ###################
        def minCost_rule(model):
            operatingCosts = sum(sum(model.x[j,t]*(model.opCost[j]+model.envCost[j]) 
                                     + model.i[j,t]*(model.capCost[j]) for t in model.horizon) for j in model.plant)
            
            startUpCosts = sum(sum(model.s[j,r]*model.startUpCost[j] for r in model.rampPeriod) for j in model.plant)
            
            return operatingCosts + startUpCosts

        model.SystemCost = Objective(rule = minCost_rule, sense = minimize)

        ################### END OBJECTIVE (min sys costs) ###################




        ################### START CONSTRAINTS ###################
        #meeting demand
        def meetDemand_rule(model,t):
            return sum(model.x[j,t] for j in model.plant) >= model.demand[t]
            
        model.meetDemand = Constraint(model.horizon,rule=meetDemand_rule)

        #abiding max generating capacity
        def belowMaxCap_rule(model,j,t):
            return model.x[j,t] <= model.i[j,t]*model.maxCapacity[j]

        model.belowCap = Constraint(model.plant,model.horizon,rule=belowMaxCap_rule)

        #abiding min generating capacity
        def aboveMinCap_rule(model,j,t):
            return model.x[j,t] >= model.i[j,t]*model.minCapacity[j]

        model.aboveCap = Constraint(model.plant,model.horizon,rule=aboveMinCap_rule)

        #Ramp 1 constraint (ramping up)
        def rampUp_rule(model,j,r):
            return model.x[j,r] - model.x[j,r-1] <= model.i[j,r]*model.rampRate[j] + model.s[j,r]*model.minCapacity[j]

        model.rampUp = Constraint(model.plant,model.rampPeriod,rule=rampUp_rule)

        #Ramp 2 constraint (ramping down)
        def rampDown_rule(model,j,r):
            return model.x[j,r-1] - model.x[j,r] <= model.i[j,r-1]*model.rampRate[j] + model.minCapacity[j]*(model.i[j,r-1]-model.i[j,r]-model.s[j,r])

        model.rampDown = Constraint(model.plant,model.rampPeriod,rule=rampDown_rule)

        #Switch plant on decision variable constraint
        def switchOn_rule(model,j,r):
            return model.s[j,r] == 1- model.i[j,r]-model.i[j,r-1]

        model.switchOn = Constraint(model.plant,model.rampPeriod,rule=switchOn_rule)


        ################### END CONSTRAINTS ###################





        ################### WRITING DATA ###################
        unitCommitment.writeDataFile("data",generatorCapitalCost,
                      variableOperatingCost,environmentalCost,
                      startUpCost,rampRate,
                      maxGeneratingCapacity,minGeneratingCapacity,
                      demandInput)

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
startCost = [1,2,3,4]
rampRate = [1,2,3,3]
maxGeneratingCapacity = [2,3,4,5]
minGeneratingCapacity = [0,1,2,3]
demand = [1,2,3,4]

unitCommitment.main(genCapCost,variableOperatingCost,
                    environmentalCost,startCost,rampRate,
                    maxGeneratingCapacity,minGeneratingCapacity,
                    demand)

print("test run done!")