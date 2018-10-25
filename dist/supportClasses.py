import numpy as np
import copy
from scipy import integrate
import scipy.interpolate as interp
import os
from os import path
import matplotlib.pyplot as plt
import polyFit as fit
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#Converts rads per second to rpms
def toRPM(rads):
    return rads*30/np.pi
    
#A class that defines a battery
class Battery:

    #Initialize members from properties
    def __init__(self, name, manu, numCells, capacity, voltage, resistance, weight, maxCurr):

        #Define members from inputs
        self.n = int(numCells)
        self.cellCap = float(capacity)
        self.cellV = float(voltage)
        self.cellR = float(resistance)
        self.name = name
        self.manufacturer = manu
        self.cellWeight = float(weight)
        self.iMax = float(maxCurr)

        #Members derived from inputs
        self.V0 = self.cellV * self.n
        self.R = self.cellR * self.n
        self.weight = self.cellWeight*self.n

#A class that defines an ESC (Electronic Speed Controller)
class ESC:

    #Initialization of the class from properties
    def __init__(self, name, manu, resistance, iMax, weight):

        self.R = float(resistance)
        self.name = name
        self.manufacturer = manu
        self.iMax = float(iMax)
        self.weight = float(weight)
        
#A class that defines an electric motor.
class Motor:

    #Initialization of the class from properties
    def __init__(self, name, manu, Kv, gearRatio, noLoadCurrent, resistance, weight):

        #Initialize members from constructor inputs
        self.Kv = float(Kv)
        self.Gr = float(gearRatio)
        self.I0 = float(noLoadCurrent)
        self.R = float(resistance)
        self.name = name
        self.manufacturer = manu
        self.weight = float(weight)

#A class of propellers defined by database test files
class Propeller:
    
    #Initializes the prop from properties
    def __init__(self, name, manu, dia, pitch, coefs):

        self.name = name
        self.manufacturer = manu
        self.diameter = float(dia)
        self.pitch = float(pitch)
        self.thrustFitOrder = int(coefs[0])
        self.fitOfThrustFitOrder = int(coefs[1])
        self.powerFitOrder = int(coefs[2])
        self.fitOfPowerFitOrder = int(coefs[3])

        numThrustCoefs = (self.thrustFitOrder+1)*(self.fitOfThrustFitOrder+1)
        self.thrustCoefs = coefs[4:numThrustCoefs+4].reshape((self.thrustFitOrder+1,self.fitOfThrustFitOrder+1)).astype(np.float)
        self.powerCoefs = coefs[numThrustCoefs+4:].reshape((self.powerFitOrder+1,self.fitOfPowerFitOrder+1)).astype(np.float)

        #These parameters will be set by later functions
        self.vInf = 0.0
        self.angVel = 0.0

        if(False):
            self.PlotCoefs()

    def CalcTorqueCoef(self):
        self.rpm = toRPM(self.angVel)
        self.rps = self.rpm/60
        self.J = self.vInf/(self.rps*self.diameter/12)
        a = fit.poly_func(self.powerCoefs.T, self.rpm)
        if(a[-1]>0):#Quadratic coefficient should always be non-positive
            a[-1] = 0
        self.Cl = fit.poly_func(a, self.J)/2*np.pi
        

    def CalcThrustCoef(self):
        self.rpm = toRPM(self.angVel)
        self.rps = self.rpm/60
        self.J = self.vInf/(self.rps*self.diameter/12)
        a = fit.poly_func(self.thrustCoefs.T, self.rpm)
        if(a[-1]>0):#Quadratic coefficient should always be non-positive
            a[-1] = 0
        self.Ct = fit.poly_func(a, self.J)

    def PlotCoefs(self):
        #Plot thrust and torque coefficients
        rpms = np.linspace(0,35000,10)
        Js = np.linspace(0,1.4,10)
        fig = plt.figure(figsize=plt.figaspect(1.))
        fig.suptitle(self.name)
        ax = fig.add_subplot(1,2,1, projection='3d')

        for rpm in rpms:
            a = fit.poly_func(self.thrustCoefs.T, rpm)
            if(a[-1]>0):#Quadratic coefficient should always be non-positive
                a[-1] = 0
            thrust = fit.poly_func(a, Js)
            rpmForPlot = np.full(len(thrust),rpm)
            ax.plot(Js,rpmForPlot,thrust, 'r-')

        ax.set_title("Predicted Thrust")
        ax.set_xlabel("Advance Ratio")
        ax.set_ylabel("RPM")
        ax.set_zlabel("Thrust Coefficient")

        ax = fig.add_subplot(1,2,2, projection='3d')

        for rpm in rpms:
            a = fit.poly_func(self.powerCoefs.T, rpm)
            if(a[-1]>0):#Quadratic coefficient should always be non-positive
                a[-1] = 0
            power = fit.poly_func(a, Js)
            rpmForPlot = np.full(len(power),rpm)
            ax.plot(Js,rpmForPlot,power, 'r-')

        ax.set_title("Predicted Power")
        ax.set_xlabel("Advance Ratio")
        ax.set_ylabel("RPM")
        ax.set_zlabel("Power Coefficient")
        plt.show()
