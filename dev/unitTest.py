import propulsionUnitClass as unit
import sqlite3 as sql
import numpy as np
import supportClasses as s

props = ["apce_4.1x4.1","apc_10x8","apcepn_20.5x13.5","da4052_5x1.58"]
motors = ["dys BX1306-3100","Actro 12-4","Astro Cobalt 90 11T#23 #690","Uberall NB 1608/160"]
batteries = ["Turnigy 1000mAH 25C LiPo","Hacker TopFuel EcoX 2400mAh","SLS-APL 5000 45C","XCell 5500 (25C)"]
numCells = 3
escs = ["Kontronic SUN 3000","Ace Smart Throttle","Astro 211","Stefan's 4-FET ESC with BEC and Brake"]
altitude = 2000
thrusts = [0.05,0.3,0.2,1]
speeds = [5,15,20,15]

#Open database and read records from database
db = sql.connect("Database/components.db")
dbcur = db.cursor()

for prop, motor, battery, esc, thrust, cruiseSpeed in zip(props,motors,batteries,escs,thrusts,speeds):

    #Fetch prop data
    formatString = """select * from Props where Name = "{propName}" """
    command = formatString.format(propName = prop)
    dbcur.execute(command)
    propRecord = dbcur.fetchall()
    propInfo = np.asarray(propRecord[0])
    propC = s.Propeller(propInfo[1],propInfo[2],propInfo[3],propInfo[4:])
    propC.PlotCoefs()

    #Fetch motor data
    formatString = """select * from Motors where Name = "{motorName}" """
    command = formatString.format(motorName = motor)
    dbcur.execute(command)
    motorRecord = dbcur.fetchall()
    motorInfo = np.asarray(motorRecord[0])
    print(motorInfo)
    motorC = s.Motor(motorInfo[1],motorInfo[2],motorInfo[3],motorInfo[5],motorInfo[4],motorInfo[6])

    #Fetch battery data
    formatString = """select * from Batteries where Name = "{batteryName}" """
    command = formatString.format(batteryName = battery)
    dbcur.execute(command)
    batteryRecord = dbcur.fetchall()
    batteryInfo = np.asarray(batteryRecord[0])
    print(batteryInfo)
    battC = s.Battery(batteryInfo[1], numCells, batteryInfo[3], batteryInfo[6], batteryInfo[5], batteryInfo[4],batteryInfo[2])

    #Fetch ESC data
    formatString = """select * from ESCs where Name = "{escName}" """
    command = formatString.format(escName = esc)
    dbcur.execute(command)
    escRecord = dbcur.fetchall()
    escInfo = np.asarray(escRecord[0])
    print(escInfo)
    escC = s.ESC(escInfo[1], escInfo[5], escInfo[2], escInfo[4])

    test = unit.PropulsionUnit(propC, motorC, battC, escC, altitude)
    print("Initialization complete. Plotting thrust curves.")
    maxAirspeed = 30
    numVelocities = 11
    numThrottles = 101
    test.PlotThrustCurves(maxAirspeed, numVelocities, numThrottles)
    print("Flight time (thrust=",thrust,", cruiseSpeed=",cruiseSpeed,")",test.CalcBattLife(thrust,cruiseSpeed),"min")

db.close()
