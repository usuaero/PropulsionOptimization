#Used to plot and determine any correlations between ESC parameters
import sqlite3 as sql
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

database = sql.connect("components.db")
cursor = database.cursor()
cursor.execute("SELECT * FROM ESC")
escTable = cursor.fetchall()

escArray = np.array(escTable)

#Correlate weights with resistance

weightAvailable = np.where((escArray[:,6] != "NULL") & (escArray[:,7] != "NULL") & (escArray[:,6] != None) & (escArray[:,7] != None))
resist = escArray[weightAvailable,6].astype(float).flatten()
weight = escArray[weightAvailable,7].astype(float).flatten()

weightClean = np.where((resist > 0.02) & (weight != 0.0))

logR = np.log(resist[weightClean])
logWeight = np.log(weight[weightClean])

weightReg = stats.linregress(logR, logWeight)
rTheo = np.linspace(min(logR), max(logR))
wTheo = rTheo*weightReg[0] + weightReg[1]

plt.plot(logR, logWeight, "bo")
plt.plot(rTheo, wTheo, "r-")
plt.text(0, 5, "W = " + "exp({:.4}".format(weightReg[0]) + "*ln(R) + " + "{:.4}".format(weightReg[1]) + ") {" + "{:.4}".format(weightReg[2]**2) + "}")
plt.title("ESC Weight vs Resistance")
plt.xlabel("ln of Resistance (ohms)")
plt.ylabel("ln of Weight (g)")
plt.show()