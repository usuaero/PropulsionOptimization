import numpy as np
import copy
from scipy import integrate
import scipy.interpolate as interp
import os
from os import path
import matplotlib.pyplot as plt
import polyFit as fit

import supportClasses as s


#A class that defines a propeller specifically to be analyzed using blade element theory
class Propeller:

    #Initialization of the class from a dict of properties
    def __init__(self, specs):
        
        #Members to be defined by PropulsionUnit
        self.vInf = 0.0 #Freestream velocity
        self.angVel = 0.0 #Prop angular velocity
        
        #Defined by the specs dict for both types
        self.name = specs["name"]
        self.rootAirfoil = s.Airfoil(specs["rootAirfoil"]) #Cross-sectional airfoil of the blade at the hub
        self.tipAirfoil = s.Airfoil(specs["tipAirfoil"]) #Cross-sectional airfoil of the blade at the tip
        self.k = specs["numBlades"] #Number of propeller blades
        self.n = specs["grid"] #Indicates how many step should be used in numerical integration steps
        
        if specs["type"] == "Hunsaker": #Reads in json according to Hunsaker's format
            
            #These members are defined by the specs dict
            self.diameter = specs["diameter"]*0.0254 #Propeller diameter
            self.pitch = specs["pitch"] #Propeller pitch length (chord-line pitch)
            self.hubZeta = 2*specs["hubRadius"]/self.diameter #Dimensionless radius of the prop hub
            self.name = specs["name"] #Name of the propeller
            self.rotation = specs["rotation"] #Direction the prop should spin
            self.rootChord = specs["rootChord"] #Chord length at the hub blade
            self.tipChord = specs["tipChord"] #Chord length at the tip of the blade
            
            #Derived members
            self.Kc = self.pitch / self.diameter
            self.zeta = np.linspace(self.hubZeta, 0.9999, self.n)
            self.c = self.rootChord + (self.tipChord - self.rootChord)*self.zeta
            self.cHatB = self.k*self.c/self.diameter
            self.K = np.pi*self.zeta*(self.Kc - np.pi*self.zeta*np.tan(self.alphaL0))/(np.pi*self.zeta + self.Kc*np.tan(self.alphaL0))
            self.beta = np.arctan(self.K/(np.pi*self.zeta))
            
            #Linear interpolation of airfoil lift and drag parameters
            self.alphaL0 = self.rootAirfoil.alphaL0 + (self.tipAirfoil.alphaL0 - self.rootAirfoil.alphaL0)*self.zeta
            self.CLalpha = self.rootAirfoil.CLalpha + (self.tipAirfoil.CLalpha - self.rootAirfoil.CLalpha)*self.zeta
            self.CLmax = self.rootAirfoil.CLmax + (self.tipAirfoil.CLmax - self.rootAirfoil.CLmax)*self.zeta
            self.CD0 = self.rootAirfoil.CD0 + (self.tipAirfoil.CD0 - self.rootAirfoil.CD0)*self.zeta
            self.CD0L = self.rootAirfoil.CD0L + (self.tipAirfoil.CD0L - self.rootAirfoil.CD0L)*self.zeta
            self.CD0L2 = self.rootAirfoil.CD0L2 + (self.tipAirfoil.CD0L2 - self.rootAirfoil.CD0L2)*self.zeta
            
        elif specs["type"] == "Selig": #Allows for geometry to be defined by Selig's test results
            
            #Read in the geometry file
            relativePath = specs["geomFile"]
            scriptDir = os.path.dirname(__file__)
            absPath = os.path.join(scriptDir, relativePath)
            geomFile = open(absPath, "r")
            rawData = geomFile.readlines()
            numPoints = len(rawData)-1
            
            #Initialize property vectors
            rawZeta = np.zeros(numPoints)
            rawC = np.zeros(numPoints)
            rawBeta = np.zeros(numPoints)
            
            #Populate property vectors
            for i in range(1, numPoints+1):
                dataRow = rawData[i].split()
                rawZeta[i-1] = float(dataRow[0])
                rawC[i-1] = float(dataRow[1])
                rawBeta[i-1] = float(dataRow[2])
            
            #Interpolate geometry vectors to create desired grid size
            self.zeta = np.linspace(rawZeta[0], 0.9999, self.n)
            self.c = np.interp(self.zeta, rawZeta, rawC)*0.0254
            self.beta = np.radians(np.interp(self.zeta, rawZeta, rawBeta))
            self.diameter = specs["diameter"]*0.0254
            self.cHatB = self.k*self.c/self.diameter
            
            #Linear interpolation of airfoil lift and drag parameters
            self.alphaL0 = self.rootAirfoil.alphaL0 + (self.tipAirfoil.alphaL0 - self.rootAirfoil.alphaL0)*self.zeta
            self.CLalpha = self.rootAirfoil.CLalpha + (self.tipAirfoil.CLalpha - self.rootAirfoil.CLalpha)*self.zeta
            self.CLmax = self.rootAirfoil.CLmax + (self.tipAirfoil.CLmax - self.rootAirfoil.CLmax)*self.zeta
            self.CD0 = self.rootAirfoil.CD0 + (self.tipAirfoil.CD0 - self.rootAirfoil.CD0)*self.zeta
            self.CD0L = self.rootAirfoil.CD0L + (self.tipAirfoil.CD0L - self.rootAirfoil.CD0L)*self.zeta
            self.CD0L2 = self.rootAirfoil.CD0L2 + (self.tipAirfoil.CD0L2 - self.rootAirfoil.CD0L2)*self.zeta
           
            #Alter beta to be based on areodynamic pitch rather than geometric pitch
            self.beta = self.beta + self.alphaL0 
            
    #Calculates the section lift
    def CalcCL(self, alpha, pos=None):
        
        if pos == None:
            pos = np.where(self.zeta==self.zeta)
            
        CL = self.CLalpha[pos]*(alpha)
        
        stalled = np.where(alpha > 0.25) or np.where(CL < -0.25)
        CL[stalled] = np.pi*np.cos(alpha[stalled])/(2*np.cos(0.25))*np.sign(CL[stalled])
        
        return CL
    
    #Calculate the section drag
    def CalcCD(self, alpha, pos=None):
        
        if pos == None:
            pos = np.where(self.zeta==self.zeta)
            
        CD = self.CD0L2*alpha[pos]**2 + self.CD0L*alpha[pos] + self.CD0[pos]
        
        stalled1 = np.where(alpha > 0.25) or np.where(alpha < -0.25)
        CD[stalled1] = (16.6944*alpha[stalled1]**2 - 1.0234)*np.sign(CD[stalled1])
        
        stalled2 = np.where(alpha > 0.3) or np.where(alpha < -0.3)
        CD[stalled2] = np.pi*np.cos(alpha[stalled2])/(2*np.cos(0.25))*np.sign(CD[stalled2])
        
        return CD
       
    #Populates arrays of propeller properties
    def CalcProperties(self):
        
        #Determine advance ratio
        self.J = 2*np.pi*self.vInf/(self.angVel*self.diameter)
        
        #Arrays of other parameters
        self.epsInf = np.arctan(self.J/(np.pi*self.zeta))
        self.epsInd = self.CalcIndAngle()
        self.alphaB = self.beta - self.epsInf - self.epsInd
        self.CL = self.CalcCL(self.alphaB)
        self.CD = self.CalcCD(self.alphaB)
                                                              
    #Uses the modified secant method to determine the induced angle at each value of zeta
    def CalcIndAngle(self):

        #Parameters for the modified secant method
        errorBound = 0.0000001
        iterations = 0
        maxIterations = 100

        #The initial guesses for epsilon at every point
        e0 = (self.beta - self.epsInf)/2
        e1 = e0 * 1.1
        
        #Initialize other necessary arrays
        f0 = np.zeros(self.n)
        f1 = np.zeros(self.n)
        e2 = np.zeros(self.n)
        alpha0 = self.beta - self.epsInf - e0
        alpha1 = np.zeros(self.n)
        A = np.arccos(np.exp(-self.k*(1-self.zeta)/(2*np.sin(self.beta[-1]))))
        f0 = self.cHatB/(8*self.zeta)*self.CalcCL(alpha0) - A*np.tan(e0)*np.sin(self.epsInf + e0)
        
        pos = np.where(e1==e1)

        #Iterate until each point converges
        while pos[0].size > 0 and iterations > maxIterations:
            
            iterations += 1
            alpha1[pos] = self.beta[pos] - self.epsInf[pos] - e1[pos]

            #Create a new estimate for the induced angle
            f1[pos] = self.cHatB[pos]/(8*self.zeta[pos])*self.CalcCL(alpha1[pos], pos) - A[pos]*np.tan(e1[pos])*np.sin(self.epsInf[pos] + e1[pos])

            e2[pos] = e1[pos] - f1[pos]*(e1[pos] - e0[pos])/(f1[pos] - f0[pos])
            
            
            #Check for an acceptable value for the induced angle
            e2[e2 >= np.pi/2] = 0.03
            e2[e2 <= -np.pi/2] = -0.03
            e2 = abs(e2)*np.sign(self.beta - self.epsInf)

            #Determine which points have not yet converged
            pos = np.where(abs((e2 - e1)/e2) > errorBound)
            print(pos)
            print(e2[pos])

            #Set values for the next iteration
            e0 = copy.deepcopy(e1)
            e1 = copy.deepcopy(e2)
            f0 = copy.deepcopy(f1)
        
        return e2

    #Uses numerical integration to find the thrust coefficient
    def CalcThrustCoef(self):

        dCt = self.zeta**2*self.cHatB*np.cos(self.epsInd)**2/np.cos(self.epsInf)**2*(self.CL*np.cos(self.epsInf + self.epsInd) - self.CD*np.sin(self.epsInf + self.epsInd))
        
        self.Ct = np.pi**2/4*integrate.simps(dCt, self.zeta)
        
    #Uses numerical integration to find the torque coefficient
    def CalcTorqueCoef(self):
        
        dCl = self.zeta**3*self.cHatB*np.cos(self.epsInd)**2/np.cos(self.epsInf)**2*(self.CD*np.cos(self.epsInf + self.epsInd) + self.CL*np.sin(self.epsInf + self.epsInd))
        
        self.Cl = np.pi**2/8*integrate.simps(dCl, self.zeta)

    #Determines the power coefficient
    def CalcPowerCoef(self):
        self.Cp = 2*np.pi*self.Cl

    #Determines the propulsive efficiency
    def CalcPropulsiveEfficiency(self):
        self.eta = self.Ct * self.J / self.Cp
        
    #Combine the above functions
    def CalcCoefficients(self):
        self.CalcThrustCoef()
        self.CalcTorqueCoef()
        self.CalcPowerCoef()
        self.CalcPropulsiveEfficiency()
        
#A class of propellers defined by database test files
class DataPropeller:
    
    #Initializes the prop from a database folder
    #Will check what type of data iss stored in the folder
    def __init__(self, propFolder):
        
        propDatabasePath = os.getcwd()
        propFolderPath = propDatabasePath + "/Props/" + propFolder
        
        self.dataType = ""
        self.staticArray = None
        
        for filename in os.listdir(path.join(propFolderPath)):
            if "PER" in filename:
                self.dataType = "apc"
                dataFileName = filename
                break
            if ("geom" in filename) or ("static" in filename):
                self.dataType = "selig"
                break
            
        if self.dataType == "apc": #Data files from APC (manufacturer)
            
            dataFile = open(propFolderPath + "/" + dataFileName)
            firstLine = dataFile.readline().split()
            diaPitch = firstLine[0].split("x")
            self.diameter = float(diaPitch[0])
            self.pitch = float(diaPitch[1])
            
            #Read through the file to get how many sets of measurements were taken
            self.rpmCount = 0
            self.advRatioCount = 0
            
            for line in dataFile:
                
                entries = line.split()
                if len(entries) != 0:
                    if entries[0] == "PROP":
                        self.rpmCount += 1
                        self.advRatioCount = 0
                    elif entries[0][0].isdigit():
                        self.advRatioCount += 1
                        
            
            #Now read through the file to read in measurements
            dataFile.seek(0)
            firstLine = dataFile.readline().split() #Get rid of the first line
            rpmIndex = -1
            advRatioIndex = -1
            self.rpms = np.zeros(self.rpmCount)
            self.coefArray = np.zeros((self.rpmCount,self.advRatioCount,4))
            
            for line in dataFile:
                
                line = line.replace("-", " ")
                entries = line.split()
                if len(entries) != 0:
                    if entries[0] == "PROP":
                        rpmIndex += 1
                        self.rpms[rpmIndex] = entries[3]
                        advRatioIndex = -1
                    elif entries[0][0].isdigit():
                        advRatioIndex += 1
                        self.coefArray[rpmIndex, advRatioIndex, 0] = entries[1] #Store advance ratio
                        self.coefArray[rpmIndex, advRatioIndex, 1] = entries[2] #Store efficiency
                        self.coefArray[rpmIndex, advRatioIndex, 2] = entries[3] #Store thrust coef
                        self.coefArray[rpmIndex, advRatioIndex, 3] = entries[4] #Store power coef
                         
            dataFile.close()
            
            
        elif self.dataType == "selig": #Data files from U of I Chicago
            
            diaPitch = propFolder.split("_")[1].split("x")
            self.diameter = float(diaPitch[0])
            self.pitch = float(diaPitch[1])
            
            #Loop through files to count sets of measurements
            self.rpms = []
            self.rpmCount = 0
            self.staticRpmCount = 0
            self.advRatioCount = 0
            for dataFileName in os.listdir(path.join(propFolderPath)):
                if not ("static" in dataFileName or "geom" in dataFileName):
                    self.rpmCount += 1
                    currAdvRatioCount = 0
                    dataFile = open(propFolderPath + "/" + dataFileName)
                    firstLine = dataFile.readline() #Throw away first line
                    
                    for line in dataFile:
                        currAdvRatioCount += 1
                        
                    if currAdvRatioCount > self.advRatioCount:
                        self.advRatioCount = currAdvRatioCount
                        
                    dataFile.close()
                elif "static" in dataFileName:
                    dataFile = open(propFolderPath + "/" + dataFileName)
                    firstLine = dataFile.readline() #Throw away first line
                    for line in dataFile:
                        self.staticRpmCount += 1
                    dataFile.close()
                    
            
            #Loop thorugh files to read in measurements
            self.rpms = np.zeros(self.rpmCount)
            self.coefArray = np.zeros((self.rpmCount, self.advRatioCount, 4))
            self.staticArray = None
            rpmIndex = -1
            advRatioIndex = -1
            
            for dataFileName in os.listdir(path.join(propFolderPath)):
                if not ("static" in dataFileName or "geom" in dataFileName):
                    rpmIndex += 1
                    advRatioIndex = -1
                    dataFileNameParts = dataFileName.split("_")#Pull apart the filename to extract the rpm value
                    self.rpms[rpmIndex] = dataFileNameParts[-1].replace(".txt", "")
                    dataFile = open(propFolderPath + "/" + dataFileName)
                    firstLine = dataFile.readline() #Throw away first line
                    
                    for line in dataFile:
                        advRatioIndex += 1
                        entries = line.split()
                        self.coefArray[rpmIndex, advRatioIndex, 0] = entries[0] #Store advance ratio
                        self.coefArray[rpmIndex, advRatioIndex, 1] = entries[3] #Store efficiency
                        self.coefArray[rpmIndex, advRatioIndex, 2] = entries[1] #Store thrust coef
                        self.coefArray[rpmIndex, advRatioIndex, 3] = entries[2] #Store power coef
                        
                    dataFile.close()
                elif "static" in dataFileName: #Static tests
                    self.staticArray = np.zeros((self.staticRpmCount, 3))
                    staticRpmIndex = -1
                    dataFile = open(propFolderPath + "/" + dataFileName)
                    firstLine = dataFile.readline() #Throw away first line
                    
                    for line in dataFile:
                        staticRpmIndex += 1
                        entries = line.split()
                        self.staticArray[staticRpmIndex,0] = entries[0]
                        self.staticArray[staticRpmIndex,1] = entries[1]
                        self.staticArray[staticRpmIndex,2] = entries[2]
                        
                    dataFile.close()
                
