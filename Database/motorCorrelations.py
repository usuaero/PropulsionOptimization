#Used to plot and determine any correlations between motor parameters
import sqlite3 as sql
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

database = sql.connect("components.db")
cursor = database.cursor()
cursor.execute("SELECT * FROM Motors")
motorTable = cursor.fetchall()

motorArray = np.array(motorTable)

#Correlate weight with Kv rating

weightAvailable = np.where((motorArray[:,6] != "NULL") & (motorArray[:,2] != "NULL") & (motorArray[:,6] != 0) & (motorArray[:,2] != 0) & (motorArray[:,6] != None) & (motorArray[:,2] != None) & (motorArray[:,6] != "None") & (motorArray[:,2] != "None"))
Kv = motorArray[weightAvailable,2].astype(float).flatten()
weight = motorArray[weightAvailable,6].astype(float).flatten()
logKv = np.log(Kv)
logWeight = np.log(weight)

weightReg = stats.linregress(logKv, logWeight)
KvTheo = np.linspace(min(logKv), max(logKv))
weightTheo = KvTheo*weightReg[0] + weightReg[1]

#plt.subplot(2, 2, 1)
plt.plot(logKv, logWeight, "bo")
plt.plot(KvTheo, weightTheo, "r-")
#plt.title("Motor Weight vs kV Rating")
plt.xlabel("ln of Kv")
plt.ylabel("ln of Weight (g)")
plt.text(6, 7, "W = " + "exp({:.4}".format(weightReg[0]) + "*ln(Kv) + " + "{:.4}".format(weightReg[1]) + ") {" + "{:.4}".format(weightReg[2]**2) + "}")
plt.show()

#Correlate armature resistance with Kv rating

resAvailable = np.where((motorArray[:,4] != "NULL") & (motorArray[:,2] != "NULL") & (motorArray[:,4] != 0) & (motorArray[:,2] != 0) & (motorArray[:,4] != None) & (motorArray[:,2] != None) & (motorArray[:,4] != "None") & (motorArray[:,2] != "None"))
resClean = np.where((motorArray[resAvailable,4].astype(float) <= 2 ))
Kv = motorArray[resAvailable][resClean,2].astype(float).flatten()
resist = motorArray[resAvailable][resClean,4].astype(float).flatten()
logKv = np.log(Kv)
logR = np.log(resist)

#plt.subplot(2, 2, 2)
plt.plot(logKv, logR, "bo")
#plt.title("Motor Resistance vs kV Rating")
plt.xlabel("ln of Kv")
plt.ylabel("ln of Resistance (ohms)")
plt.show()

#Correlate no load current with Kv rating

curAvailable = np.where((motorArray[:,5] != "NULL") & (motorArray[:,2] != "NULL") & (motorArray[:,5] != 0) & (motorArray[:,2] != 0) & (motorArray[:,5] != None) & (motorArray[:,2] != None) & (motorArray[:,5] != "None") & (motorArray[:,2] != "None"))
curClean = np.where((motorArray[curAvailable,5].astype(float) <= 10 ))
Kv = motorArray[curAvailable][curClean,2].astype(float).flatten()
I0 = motorArray[curAvailable][curClean,5].astype(float).flatten()
logKv = np.log(Kv)
logI0 = np.log(I0)

currReg = stats.linregress(logKv, logI0)
KvTheo = np.linspace(min(logKv), max(logKv))
currTheo = KvTheo*currReg[0] + currReg[1]

#plt.subplot(2, 2, 3)
plt.plot(logKv, logI0, "bo")
plt.plot(KvTheo, currTheo, "r-")
plt.text(5.5, 2, "W = " + "exp({:.4}".format(currReg[0]) + "*ln(Kv) + " + "{:.4}".format(currReg[1]) + ") {" + "{:.4}".format(currReg[2]**2) + "}")
#plt.title("Motor No Load Current vs kV Rating")
plt.xlabel("ln of Kv")
plt.ylabel("ln of No Load Current (amps)")
plt.show()

#Correlate no load current with armature resistance

curResAvailable = np.where((motorArray[:,5] != "NULL") & (motorArray[:,4] != "NULL") & (motorArray[:,5] != 0) & (motorArray[:,4] != 0) & (motorArray[:,5] != None) & (motorArray[:,4] != None) & (motorArray[:,5] != "None") & (motorArray[:,4] != "None"))
curResClean = np.where((motorArray[curResAvailable,5].astype(float) <= 10 ) & (motorArray[curResAvailable,4].astype(float) <= 2 ))
resist = motorArray[curResAvailable][curResClean,4].astype(float).flatten()
I0 = motorArray[curResAvailable][curResClean,5].astype(float).flatten()

logR = np.log(resist)
logI0 = np.log(I0)

reg = stats.linregress(logR, logI0)

RTheo = np.linspace(min(logR), max(logR))
I0Theo = RTheo*reg[0] + reg[1]

#plt.subplot(2, 2, 4)
plt.plot(logR, logI0, "bo")
plt.plot(RTheo, I0Theo, "r-")
plt.text(-6, 2, "I0 = " + "exp({:.4}".format(reg[0]) + "*ln(R) + " + "{:.4}".format(reg[1]) + ") {" + "{:.4}".format(reg[2]**2) + "}")
#plt.title("Motor No Load Current vs Resistance")
plt.xlabel("ln of Resistance (ohms)")
plt.ylabel("ln of No Load Current (amps)")

plt.show()