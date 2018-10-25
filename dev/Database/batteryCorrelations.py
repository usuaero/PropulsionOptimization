#Used to plot and determine any correlations between battery parameters
import sqlite3 as sql
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

database = sql.connect("components.db")
cursor = database.cursor()
cursor.execute("SELECT * FROM Batteries")
batteryTable = cursor.fetchall()

batteryArray = np.array(batteryTable)

#Correlate weights with capacity

weightAvailable = np.where((batteryArray[:,6] != "NULL") & (batteryArray[:,5] != "NULL") & (batteryArray[:,6] != 0) & (batteryArray[:,5] != 0) & (batteryArray[:,6] != None) & (batteryArray[:,5] != None))
weight = batteryArray[weightAvailable,6].astype(float)
capacity = batteryArray[weightAvailable,5].astype(float)

#Split weights according to which trend they follow
dividingSlope = 0.05
upper = np.where(weight > dividingSlope*capacity)
lower = np.where(weight < dividingSlope*capacity)
Cu = capacity[upper]
Cl = capacity[lower]
Wu = weight[upper]
Wl = weight[lower]
upperReg = stats.linregress(Cu, Wu)
lowerReg = stats.linregress(Cl, Wl)

cTheo = np.linspace(0, max(Cl))
wUTheo = upperReg[0]*cTheo + upperReg[1]
wLTheo = lowerReg[0]*cTheo + lowerReg[1]

plt.subplot(1, 2, 1)
plt.plot(Cu, Wu, "go")
plt.plot(Cl, Wl, "bo")
plt.plot(cTheo, wUTheo, "r-")
plt.plot(cTheo, wLTheo, "r-")
plt.text(2000, 1000, "w = " + "{:.4}".format(upperReg[0]) + "*C + " + "{:.4}".format(upperReg[1]) + " {" + "{:.4}".format(upperReg[2]**2) + "}")
plt.text(5000, 0, "w = " + "{:.4}".format(lowerReg[0]) + "*C + " + "{:.4}".format(lowerReg[1]) + " {" + "{:.4}".format(lowerReg[2]**2) + "}")
plt.title("Battery Weight vs Capacity Rating")
plt.xlabel("Capacity (mAh)")
plt.ylabel("Weight (g)")

#Correlate internal resistance with capacity

resAvailable = np.where((batteryArray[:,7] != "NULL") & (batteryArray[:,5] != "NULL") & (batteryArray[:,7] != 0) & (batteryArray[:,5] != 0) & (batteryArray[:,7] != None) & (batteryArray[:,5] != None))
capacity = batteryArray[resAvailable,5].astype(float)
resistance = batteryArray[resAvailable,7].astype(float)
logCap = np.log(capacity).flatten()
logRes = np.log(resistance).flatten()

resReg = stats.linregress(logCap, logRes)
cTheo = np.linspace(min(logCap), max(logCap))
resTheo = cTheo*resReg[0] + resReg[1]

plt.subplot(1, 2, 2)
plt.plot(logCap, logRes, "bo")
plt.plot(cTheo, resTheo, "r-")
plt.text(min(cTheo), -2, "R = " + "exp({:.4}".format(resReg[0]) + "*ln(C) + " + "{:.4}".format(resReg[1]) + ") {" + "{:.4}".format(upperReg[2]**2) + "}")
plt.title("Battery Resistance vs Capacity Rating")
plt.xlabel("ln of Capacity (mAh)")
plt.ylabel("ln of Resistance (ohms)")

plt.show()