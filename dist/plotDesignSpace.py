import propulsionUnitClass as unit
import matplotlib.pyplot as plt
import sqlite3 as sql
import supportClasses as s
import numpy as np
from random import randint
import multiprocessing as mp
import math
import sys
import warnings

dbFile = "Database/components.db"

def printUnitInfo(unit):
    print("----Propulsion Unit----")
    print("Prop:",unit.prop.name)
    print("Motor:",unit.motor.name)
    print("      Kv:",unit.motor.Kv)
    print("      I0:",unit.motor.I0)
    print("      R:",unit.motor.R)
    print("      weight:",unit.motor.weight)
    print("ESC:",unit.esc.name)
    print("      weight:",unit.esc.weight)
    print("Battery:",unit.batt.name)
    print("      capacity:",unit.batt.cellCap)
    print("      cells:",unit.batt.n)
    print("      V:",unit.batt.V0)
    print("      weight:",unit.batt.weight)

def on_pick(event):
    artist = event.artist
    xmouse,ymouse = event.mouseevent.xdata, event.mouseevent.ydata
    x,y = artist.get_xdata(), artist.get_ydata()
    ind = int(event.ind[0])
    selUnit = units[ind]

    axClicked = event.mouseevent.inaxes
    fig = plt.figure(plt.get_fignums()[0])
    fig.suptitle("SELCTED Prop: "+str(selUnit.prop.name)+"  Motor: "+str(selUnit.motor.name)+"  Battery: "+str(selUnit.batt.name)+"  ESC: "+str(selUnit.esc.name))
    ax = fig.axes
    ax[0].plot(selUnit.prop.diameter,t_flight[ind],'o')
    ax[1].plot(selUnit.prop.pitch,t_flight[ind],'o')
    ax[2].plot(selUnit.motor.Kv,t_flight[ind],'o')
    ax[3].plot(selUnit.batt.V0,t_flight[ind],'o')
    ax[4].plot(selUnit.batt.cellCap,t_flight[ind],'o')
    ax[5].plot(selUnit.GetWeight()+W_frame,t_flight[ind],'o')
    printUnitInfo(selUnit)
    print("Flight Time:",t_flight[ind],"min")
    selUnit.PlotThrustCurves(30,11,51)

def setGlobalCursor():
    global dbcur
    dbcur = sql.connect(dbFile).cursor()

def getCombination(args):

    v_req = args[0]
    T = args[1]
    h = args[2]
    optimizeForRatio = args[3]

    if optimizeForRatio:
        R_tw_req = T
    else:
        T_req = T

    # Get numbers of components from database
    dbcur.execute("select count(*) from Props")
    N_props = int(dbcur.fetchall()[0][0])
    dbcur.execute("select count(*) from Motors")
    N_motors = int(dbcur.fetchall()[0][0])
    dbcur.execute("select count(*) from Batteries")
    N_batt = int(dbcur.fetchall()[0][0])
    dbcur.execute("select count(*) from ESCs")
    N_escs = int(dbcur.fetchall()[0][0])
    
    t_flight_curr = None
    while t_flight_curr is None or math.isnan(t_flight_curr):

        propID = randint(1,N_props)
        motorID = randint(1,N_motors)
        battID = randint(1,N_batt)
        numCells = randint(2,5)
        escID = randint(1,N_escs)

        #Fetch prop data
        formatString = """select * from Props where id = {ID}"""
        command = formatString.format(ID = propID)
        results = dbcur.execute(command)
        propInfo = np.asarray(results.fetchone()).flatten()
        prop = s.Propeller(propInfo[1],propInfo[2],propInfo[3],propInfo[4],propInfo[5:])

        #Fetch motor data
        formatString = """select * from Motors where id = {ID}"""
        command = formatString.format(ID = motorID)
        results = dbcur.execute(command)
        motorInfo = np.asarray(results.fetchone()).flatten()
        motor = s.Motor(motorInfo[1],motorInfo[2],motorInfo[3],motorInfo[4],motorInfo[6],motorInfo[5],motorInfo[7])

        #Fetch ESC data
        formatString = """select * from ESCs where id = {ID}"""
        command = formatString.format(ID = escID)
        results = dbcur.execute(command)
        escInfo = np.asarray(results.fetchone()).flatten()
        esc = s.ESC(escInfo[1],escInfo[2],escInfo[6],escInfo[3], escInfo[5])

        #Fetch battery data
        formatString = """select * from Batteries where id = {ID}"""
        command = formatString.format(ID = battID)
        results = dbcur.execute(command)
        batteryInfo = np.asarray(results.fetchone()).flatten()
        batt = s.Battery(batteryInfo[1],batteryInfo[2],numCells,batteryInfo[4],batteryInfo[7],batteryInfo[6],batteryInfo[5],batteryInfo[3])

        if batt.R == 0 and esc.R == 0 and motor.R == 0:
            continue

        currUnit = unit.PropulsionUnit(prop,motor,batt,esc,h)
        if optimizeForRatio:
            T_req = (currUnit.GetWeight()+args[4])*R_tw_req
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            t_flight_curr = currUnit.CalcBattLife(v_req,T_req)
    return t_flight_curr, currUnit

#----------------------BEGINNING OF COMPUTATION------------------------------------

v_req = None
T_req = None
R_tw_req = None
h = None
W_frame = None
N_units = 10000 #default value
N_proc_max = 8 #default value
args = sys.argv
for i,arg in enumerate(args):
    if "units" in arg:
        N_units = int(args[i+1])
    if "mp" in arg:
        N_proc_max = int(args[i+1])
    if "speed" in arg:
        v_req = float(args[i+1])
    if "thrust" in arg:
        T_req = float(args[i+1])
        optimizeForRatio = False
    if "thrustToWeight" in arg:
        R_tw_req = float(args[i+1])
        optimizeForRatio = True
    if "alt" in arg:
        h = float(args[i+1])
    if "weight" in arg:
        W_frame = float(args[i+1])

if v_req is None or (T_req is None and R_tw_req is None) or h is None:
    raise ValueError('One or more required parameters were not specified')
if optimizeForRatio and W_frame is None:
    raise ValueError('Airframe weight not specified for thrust-to-weight analysis')

if optimizeForRatio:
    print("Optimizing for a thrust-to-weight ratio of",R_tw_req,"at a speed of",v_req,"ft/s and an altitude of",h,"ft")
    thrustParam = R_tw_req
else:
    print("Optimizing for a thrust of",T_req,"lbf at a speed of",v_req,"ft/s and an altitude of",h)
    thrustParam = T_req


# Distribute work
with mp.Pool(processes=N_proc_max,initializer=setGlobalCursor,initargs=()) as pool:
    args = [(v_req,thrustParam,h,optimizeForRatio,W_frame) for i in range(N_units)]
    data = pool.map(getCombination,args)
sql.connect(dbFile).close()

t_flight,units = map(list,zip(*data))

# Determine optimum
t_max = max(t_flight)
bestUnit = units[t_flight.index(t_max)]

print("Maximum flight time found:",t_max,"min")
print("Prop:",bestUnit.prop.name)
print("Motor:",bestUnit.motor.name,"(Kv =",bestUnit.motor.Kv,")")
print("Battery:",bestUnit.batt.name,"(Capacity =",bestUnit.batt.cellCap,", Voltage =",bestUnit.batt.V0,")")
print("ESC:",bestUnit.esc.name)
print("Throttle setting for max flight:",bestUnit.CalcCruiseThrottle(v_req,T_req))
print("Current draw:",bestUnit.Im,"A")

# Plot design space
plt.ion()
fig,((ax1,ax2,ax3),(ax4,ax5,ax6)) = plt.subplots(nrows=2,ncols=3)
fig.suptitle("OPTIMUM Prop: "+str(bestUnit.prop.name)+"  Motor: "+str(bestUnit.motor.name)+"  Battery: "+str(bestUnit.batt.name)+"  ESC: "+str(bestUnit.esc.name))
ax1.plot([units[i].prop.diameter for i in range(N_units)],t_flight,'b*',picker=3)
ax1.plot(bestUnit.prop.diameter,t_max,'r*')
ax1.set_xlabel("Prop Diameter [in]")
ax1.set_ylabel("Flight Time [min]")

ax2.plot([units[i].prop.pitch for i in range(N_units)],t_flight,'b*',picker=3)
ax2.plot(bestUnit.prop.pitch,t_max,'r*')
ax2.set_xlabel("Prop Pitch [in]")
ax2.set_ylabel("Flight Time [min]")

ax3.plot([units[i].motor.Kv for i in range(N_units)],t_flight,'b*',picker=3)
ax3.plot(bestUnit.motor.Kv,t_max,'r*')
ax3.set_xlabel("Motor Kv [rpm/V]")
ax3.set_ylabel("Flight Time [min]")

ax4.plot([units[i].batt.V0 for i in range(N_units)],t_flight,'b*',picker=3)
ax4.plot(bestUnit.batt.V0,t_max,'r*')
ax4.set_xlabel("Battery Voltage [V]")
ax4.set_ylabel("Flight Time [min]")

ax5.plot([units[i].batt.cellCap for i in range(N_units)],t_flight,'b*',picker=3)
ax5.plot(bestUnit.batt.cellCap,t_max,'r*')
ax5.set_xlabel("Cell Capacity [mAh]")
ax5.set_ylabel("Flight Time [min]")

ax6.plot([units[i].GetWeight()+W_frame for i in range(N_units)],t_flight,'b*',picker=3)
ax6.plot(bestUnit.GetWeight()+W_frame,t_max,'r*')
ax6.set_xlabel("Total Unit Weight [lb]")
ax6.set_ylabel("Flight Time [min]")

fig.canvas.mpl_connect('pick_event',on_pick)
plt.show(block=True)
plt.ioff()
