import supportClasses as s
import propulsionUnitClass as unit
import numpy as np
import sqlite3 as sql
from random import randint

class Airplane:

    def __init__(self,emptyAirframeWeight):
        self.W0 = emptyAirframeWeight;

    # Performs a random search of the design space to find a combination with the desired thrust to weight ratio.
    # Will optimize based off of flight time at that ratio.
    def RSOptimizeThrustToWeight(self,desiredThrustToWeight,reqCruiseSpeed,altitude,maxIterations=1000000):

        db = sql.connect("Database/components.db")
        dbcur = db.cursor()

        iteration = 0

        # Get numbers of components from database
        dbcur.execute("select count(*) from Props")
        numProps = int(dbcur.fetchall()[0][0])
        dbcur.execute("select count(*) from Motors")
        numMotors = int(dbcur.fetchall()[0][0])
        dbcur.execute("select count(*) from Batteries")
        numBatteries = int(dbcur.fetchall()[0][0])
        dbcur.execute("select count(*) from ESCs")
        numESCs = int(dbcur.fetchall()[0][0])
        
        bestFlightTime = 1
        bestUnit = None
        
        while(iteration < maxIterations):
            iteration = iteration+1
            print(iteration,"out of",maxIterations)
            propID = randint(1,numProps)
            motorID = randint(1,numMotors)
            battID = randint(1,numBatteries)
            numCells = randint(2,5)
            escID = randint(1,numESCs)
        
            #Fetch prop data
            formatString = """select * from Props where id = {ID}"""
            command = formatString.format(ID = propID)
            results = dbcur.execute(command)
            propInfo = np.asarray(results.fetchone()).flatten()
#            print(propInfo[1])
            prop = s.Propeller(propInfo[1],propInfo[2],propInfo[3],propInfo[4:])
        
            #Fetch motor data
            formatString = """select * from Motors where id = {ID}"""
            command = formatString.format(ID = motorID)
            results = dbcur.execute(command)
            motorInfo = np.asarray(results.fetchone()).flatten()
#            print(motorInfo)
            motor = s.Motor(motorInfo[1],motorInfo[2],motorInfo[3],motorInfo[5],motorInfo[4],motorInfo[6])
        
            #Fetch ESC data
            formatString = """select * from ESCs where id = {ID}"""
            command = formatString.format(ID = escID)
            results = dbcur.execute(command)
            escInfo = np.asarray(results.fetchone()).flatten()
#            print(escInfo)
            esc = s.ESC(escInfo[1], escInfo[5], escInfo[2], escInfo[4])
        
            #Fetch battery data
            formatString = """select * from Batteries where id = {ID}"""
            command = formatString.format(ID = battID)
            results = dbcur.execute(command)
            batteryInfo = np.asarray(results.fetchone()).flatten()
#            print(batteryInfo)
            batt = s.Battery(batteryInfo[1], numCells, batteryInfo[3], batteryInfo[6], batteryInfo[5], batteryInfo[4],batteryInfo[2])
        
            if batt.R == 0 and esc.R == 0 and motor.R == 0:
                iteration = iteration - 1
                continue
        
            currUnit = unit.PropulsionUnit(prop,motor,batt,esc,altitude)
            totalWeight = self.W0 + currUnit.GetWeight()
            reqThrust = desiredThrustToWeight*totalWeight
            currFlightTime = currUnit.CalcBattLife(reqCruiseSpeed,reqThrust)

            if(currFlightTime==None):
                continue
            elif(currFlightTime>bestFlightTime):
                bestFlightTime = currFlightTime
                bestUnit = currUnit
                print("New Best Flight Time:",bestFlightTime)
        
        if bestUnit == None:
            print("No suitable combination found")
            return
        self.pu = bestUnit
        self.W = self.W0 + self.pu.GetWeight()/16
        print("Maximum flight time found:",bestFlightTime,"min")
        print("Prop:",self.pu.prop.name)
        print("Motor:",self.pu.motor.name,"(Kv =",self.pu.motor.Kv,")")
        print("Battery:",self.pu.batt.name,"(Capacity =",self.pu.batt.cellCap,", Voltage =",self.pu.batt.V0,")")
        print("ESC:",self.pu.esc.name)
        print("Total Weight",self.W,"lbs")
        print("Throttle setting for max flight:",self.pu.CalcCruiseThrottle(reqCruiseSpeed,reqThrust))
        print("Current draw:",self.pu.Im,"A")
        self.pu.PlotThrustCurves(30,11,51)
        self.pu.prop.PlotCoefs()
        
        db.close()
