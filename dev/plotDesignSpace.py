import matplotlib.pyplot as plt
import sqlite3 as sql
import supportClasses as s
import numpy as np
from random import randint,seed
import multiprocessing as mp
import math
import sys
import warnings
from datetime import datetime

####################################################################
# plotDesignSpace.py
#
# Randomly searches possible combinations of components and determines viable flight times.
# Plots these flight times against component parameters. User can select specific points in
# the design space to view component parameteres and thrust curves.
#
# Arguments:
#
# units (optional): the number of possible combinations to consider (10000 if not specified)
# processes (optional): the maximum number of processes to be used (this program is run in 
#                       parallel) (8 if not specified)
# speed (required): desired airspeed in ft/s
# alt (required): expected flight altitude in ft
# thrust (required to search for a simple thrust value): desired thrust in lbf
# thrustToWeight (required to search for a thrust to weight ratio): desired thrust to weight ratio in lbf/lbf
# weight (required to search for a thrust to weight ratio): aircraft frame weight

dbFile = "Database/components.db"

#Defines what happens when the user picks a plotted point in the design space. Highlights that point and 
#plots that unit's thrust curves.
def on_pick(event):
    artist = event.artist
    xmouse,ymouse = event.mouseevent.xdata, event.mouseevent.ydata
    x,y = artist.get_xdata(), artist.get_ydata()
    ind = int(event.ind[0])
    selUnit = units[ind]

    axClicked = event.mouseevent.inaxes
    fig = plt.figure(plt.get_fignums()[0])
    fig.suptitle("SELECTED Prop: "+str(selUnit.prop.name)+"  Motor: "+str(selUnit.motor.name)+"  Battery: "+str(selUnit.batt.name)+"  ESC: "+str(selUnit.esc.name))
    ax = fig.axes
    ax[0].plot(selUnit.prop.diameter,t_flight[ind],'o')
    ax[1].plot(selUnit.prop.pitch,t_flight[ind],'o')
    ax[2].plot(selUnit.motor.Kv,t_flight[ind],'o')
    ax[3].plot(selUnit.batt.V0,t_flight[ind],'o')
    ax[4].plot(selUnit.batt.cellCap,t_flight[ind],'o')
    ax[5].plot(selUnit.GetWeight()+W_frame,t_flight[ind],'o')
    selUnit.printInfo()
    print("Flight Time:",t_flight[ind],"min")
    if optimizeForRatio:
        print("    at {:4.2f}% throttle".format(selUnit.CalcCruiseThrottle(v_req,(selUnit.GetWeight()+W_frame)*R_tw_req)*100))
    else:
        print("    at {:4.2f}% throttle".format(selUnit.CalcCruiseThrottle(v_req,T_req)*100))
    selUnit.PlotThrustCurves(v_req*2+10,11,51)
    selUnit.prop.PlotCoefs()

#Defines a global database cursor giving all processes a connection to the database.
def setGlobalCursor():
    global dbcur
    dbcur = sql.connect(dbFile).cursor()

#Selects a propultion unit and calculates its flight time.
def getCombination(args):

    v_req = args[0]
    T = args[1]
    h = args[2]
    optimizeForRatio = args[3]
    W_frame = args[4]
    manufacturers = args[5]

    if optimizeForRatio:
        R_tw_req = T
    else:
        T_req = T

    seed(datetime.now())
    
    t_flight_curr = None
    while t_flight_curr is None or math.isnan(t_flight_curr):

        #Fetch prop data
        prop = s.Propeller(dbcur,manufacturer=manufacturers[0])

        #Fetch motor data
        motor = s.Motor(dbcur,manufacturer=manufacturers[1])

        #Fetch ESC data
        esc = s.ESC(dbcur,manufacturer=manufacturers[2])

        #Fetch battery data
        batt = s.Battery(dbcur,manufacturer=manufacturers[3])

        if batt.R == 0 and esc.R == 0 and motor.R == 0:
            continue

        currUnit = s.PropulsionUnit(prop,motor,batt,esc,h)
        if optimizeForRatio:
            T_req = (currUnit.GetWeight()+W_frame)*R_tw_req
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
manufacturers = [None, None, None, None]
components = [None, None, None, None]
N_units = 10000 #default value
N_proc_max = 8 #default value
args = sys.argv
for i,arg in enumerate(args):
    if "units" in arg:
        N_units = int(args[i+1])
    elif "processes" in arg:
        N_proc_max = int(args[i+1])
    elif "speed" in arg:
        v_req = float(args[i+1])
    elif "thrust" in arg:
        T_req = float(args[i+1])
        W_frame = 0
        optimizeForRatio = False
    elif "thrustToWeight" in arg:
        R_tw_req = float(args[i+1])
        optimizeForRatio = True
    elif "alt" in arg:
        h = float(args[i+1])
    elif "weight" in arg:
        W_frame = float(args[i+1])
    elif "propManufacturer" in arg:
        manufacturers[0] = args[i+1]
    elif "motorManufacturer" in arg:
        manufacturers[1] = args[i+1]
    elif "escManufacturer" in arg:
        manufacturers[2] = args[i+1]
    elif "battManufacturer" in arg:
        manufacturers[3] = args[i+1]

if v_req is None or (T_req is None and R_tw_req is None) or h is None:
    raise ValueError('One or more required parameters were not specified.')
if optimizeForRatio and W_frame is None:
    raise ValueError('Airframe weight not specified for thrust-to-weight analysis.')

if optimizeForRatio:
    print("Searching the design space for a thrust-to-weight ratio of",R_tw_req,"at a speed of",v_req,"ft/s and an altitude of",h,"ft")
    thrustParam = R_tw_req
else:
    print("Searching the design space for a thrust of",T_req,"lbf at a speed of",v_req,"ft/s and an altitude of",h)
    thrustParam = T_req


# Distribute work
with mp.Pool(processes=N_proc_max,initializer=setGlobalCursor,initargs=()) as pool:
    args = [(v_req,thrustParam,h,optimizeForRatio,W_frame,manufacturers) for i in range(N_units)]
    data = pool.map(getCombination,args)
sql.connect(dbFile).close()

t_flight,units = map(list,zip(*data))

# Determine optimum
t_max = max(t_flight)
bestUnit = units[t_flight.index(t_max)]

print("Maximum flight time found:",t_max,"min")
bestUnit.printInfo()
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
