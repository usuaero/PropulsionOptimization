import propulsionUnitClass as unit
import sqlite3 as sql
import supportClasses as s
import numpy as np
from random import randint
import multiprocessing as mp
import math

dbFile = "Database/components.db"

def setGlobalCursor():
    global dbcur
    dbcur = sql.connect(dbFile).cursor()

def getCombination(args):

    reqCruiseSpeed = args[0]
    reqThrust = args[1]
    altitude = args[2]

    # Get numbers of components from database
    dbcur.execute("select count(*) from Props")
    numProps = int(dbcur.fetchall()[0][0])
    dbcur.execute("select count(*) from Motors")
    numMotors = int(dbcur.fetchall()[0][0])
    dbcur.execute("select count(*) from Batteries")
    numBatteries = int(dbcur.fetchall()[0][0])
    dbcur.execute("select count(*) from ESCs")
    numESCs = int(dbcur.fetchall()[0][0])
    
    currFlightTime = None
    while currFlightTime is None or math.isnan(currFlightTime):

        print(args[3])
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
        print(propInfo)
        prop = s.Propeller(propInfo[1],propInfo[2],propInfo[3],propInfo[4],propInfo[5:])

        #Fetch motor data
        formatString = """select * from Motors where id = {ID}"""
        command = formatString.format(ID = motorID)
        results = dbcur.execute(command)
        motorInfo = np.asarray(results.fetchone()).flatten()
        print(motorInfo)
        motor = s.Motor(motorInfo[1],motorInfo[2],motorInfo[3],motorInfo[4],motorInfo[6],motorInfo[5],motorInfo[7])

        #Fetch ESC data
        formatString = """select * from ESCs where id = {ID}"""
        command = formatString.format(ID = escID)
        results = dbcur.execute(command)
        escInfo = np.asarray(results.fetchone()).flatten()
        print(escInfo)
        esc = s.ESC(escInfo[1],escInfo[2],escInfo[6],escInfo[3], escInfo[5])

        #Fetch battery data
        formatString = """select * from Batteries where id = {ID}"""
        command = formatString.format(ID = battID)
        results = dbcur.execute(command)
        batteryInfo = np.asarray(results.fetchone()).flatten()
        print(batteryInfo)
        batt = s.Battery(batteryInfo[1],batteryInfo[2],numCells,batteryInfo[4],batteryInfo[7],batteryInfo[6],batteryInfo[5],batteryInfo[3])

        if batt.R == 0 and esc.R == 0 and motor.R == 0:
            continue

        currUnit = unit.PropulsionUnit(prop,motor,batt,esc,altitude)
        currFlightTime = currUnit.CalcBattLife(reqCruiseSpeed,reqThrust)
    return currFlightTime, currUnit


combinations = 10000
maxProcesses = 8

# Will attempt to maximize flight time based on these parameters
# Randomly selects combinations of components
reqCruiseSpeed = 10
reqThrust = 0.5
altitude = 2000

with mp.Pool(processes=maxProcesses,initializer=setGlobalCursor,initargs=()) as pool:
    args = [(reqCruiseSpeed,reqThrust,altitude,i) for i in range(combinations)]
    data = pool.map(getCombination,args)
sql.connect(dbFile).close()

flightTimes,units = map(list,zip(*data))

bestFlightTime = max(flightTimes)
bestUnit = units[flightTimes.index(bestFlightTime)]


print("Maximum flight time found:",bestFlightTime,"min")
print("Prop:",bestUnit.prop.name)
print("Motor:",bestUnit.motor.name,"(Kv =",bestUnit.motor.Kv,")")
print("Battery:",bestUnit.batt.name,"(Capacity =",bestUnit.batt.cellCap,", Voltage =",bestUnit.batt.V0,")")
print("ESC:",bestUnit.esc.name)
print("Throttle setting for max flight:",bestUnit.CalcCruiseThrottle(reqCruiseSpeed,reqThrust))
print("Current draw:",bestUnit.Im,"A")
bestUnit.PlotThrustCurves(30,11,51)

