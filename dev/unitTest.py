import sqlite3 as sql
import numpy as np
import supportClasses as s

props = ["apc_9x6.5","gwsdd_5x4.3","grcp_11x6"]
motors = ["Aveox 27/13/2","137x50 11Y450 Kisscatz 9N6P jw","Neu 1521/1D"]
batteries = ["Kokam 2100SHD","SLS-X-Treme 5000-35C (3P)","Saehan 2100-20C"]
numCells = 3
escs = ["Welgard ESC 18 (default)","Aveox F5LV","Castle Phoenix 25"]
altitude = 1000
thrusts = [0.5,0.5,0.5]
speeds = [0,10,10]

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
    propC = s.Propeller(propInfo[1],propInfo[2],propInfo[3],propInfo[4],propInfo[5:])
    propC.PlotCoefs()

    #Fetch motor data
    formatString = """select * from Motors where Name = "{motorName}" """
    command = formatString.format(motorName = motor)
    dbcur.execute(command)
    motorRecord = dbcur.fetchall()
    motorInfo = np.asarray(motorRecord[0])
    print(motorInfo)
    motorC = s.Motor(motorInfo[1],motorInfo[2],motorInfo[3],motorInfo[4],motorInfo[6],motorInfo[5],motorInfo[7])

    #Fetch battery data
    formatString = """select * from Batteries where Name = "{batteryName}" """
    command = formatString.format(batteryName = battery)
    dbcur.execute(command)
    batteryRecord = dbcur.fetchall()
    batteryInfo = np.asarray(batteryRecord[0])
    print(batteryInfo)
    battC = s.Battery(batteryInfo[1],batteryInfo[2],numCells,batteryInfo[4],batteryInfo[7],batteryInfo[6],batteryInfo[5],batteryInfo[3])

    #Fetch ESC data
    formatString = """select * from ESCs where Name = "{escName}" """
    command = formatString.format(escName = esc)
    dbcur.execute(command)
    escRecord = dbcur.fetchall()
    escInfo = np.asarray(escRecord[0])
    print(escInfo)
    escC = s.ESC(escInfo[1],escInfo[2],escInfo[6],escInfo[3], escInfo[5])

    test = s.PropulsionUnit(propC, motorC, battC, escC, altitude)
    print("Initialization complete. Plotting thrust curves.")
    maxAirspeed = 30
    numVelocities = 11
    numThrottles = 11
    test.PlotThrustCurves(maxAirspeed, numVelocities, numThrottles)
    print("Flight time (thrust=",thrust,", cruiseSpeed=",cruiseSpeed,")",test.CalcBattLife(thrust,cruiseSpeed),"min")

db.close()
