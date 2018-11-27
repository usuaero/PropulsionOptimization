import sqlite3 as sql
import numpy as np
import supportClasses as s

props = ["gwsdd_5x4.3","grcp_11x6"]
motors = ["137x50 11Y450 Kisscatz 9N6P jw","Neu 1521/1D"]
batteries = ["SLS-X-Treme 5000-35C (3P)","Saehan 2100-20C"]
numCells = 3
escs = ["Aveox F5LV","Castle Phoenix 25"]
altitude = 1000
thrusts = [0.5,0.5,0.5]
speeds = [0,10,10]

#Open database and read records from database
db = sql.connect("Database/components.db")
dbcur = db.cursor()

for prop, motor, battery, esc, thrust, cruiseSpeed in zip(props,motors,batteries,escs,thrusts,speeds):

    #Fetch prop data
    propC = s.Propeller(dbcur,name=prop)
    propC.printInfo()
    propC.PlotCoefs()

    #Fetch motor data
    motorC = s.Motor(dbcur,name=motor)
    motorC.printInfo()

    #Fetch battery data
    battC = s.Battery(dbcur)
    battC.printInfo()

    #Fetch ESC data
    escC = s.ESC(dbcur,name=esc)
    escC.printInfo()

    test = s.PropulsionUnit(propC, motorC, battC, escC, altitude)
    print("Initialization complete. Plotting thrust curves.")
    maxAirspeed = 30
    numVelocities = 11
    numThrottles = 11
    test.PlotThrustCurves(maxAirspeed, numVelocities, numThrottles)
    print("Flight time (thrust=",thrust,", cruiseSpeed=",cruiseSpeed,")",test.CalcBattLife(thrust,cruiseSpeed),"min")

db.close()
