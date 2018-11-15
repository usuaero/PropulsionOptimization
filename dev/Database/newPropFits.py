#An attempt to fit prop coefficients to more well-behaved functions.
#From observation it looks like C_t can be given by:
#
#       C_tmax/(1+e^(k*d)) + (C-A*J_sel-B*N_sel)/(1+e^(-k*d))
# where d = (F*J_sel-N_sel+E)/sqrt(1+F^2)
#       C_tmax is the max value for the coefficient of thrust (a plateau in experimental data)
#       C-A*J_sel-B*N_sel defines the plane of thrust coefficients below stall (relatively flat)
#       r = <0,E>+s<1,F> defines the line marking halfway in the transition from C_tmax and the lower values
#       k is a parameter describing the transition curvature

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
from os import path
import polyFit as fit
import re
import scipy.optimize as opt
import multiprocessing as mp

def isNum(x):
    try:
        float(x)
        if np.isnan(float(x)):
            return False
        return True
    except ValueError:
        return False
    except TypeError:
        return False

def CalcCt(JN,C_tmax,A,B,C,k):
    E = (C-C_tmax)/B
    F = -A/B
    d = (F*JN[0]-JN[1]+E)/np.sqrt(1+F**2)
    return C_tmax/(1+np.exp(k*d)) + (C-A*JN[0]-B*JN[1])/(1+np.exp(-k*d))

def FitCoefs(args):
    propFolder = args[0]
    databasePath = args[1]

    if ".py" in str(propFolder):
        return None
    if ".xls" in str(propFolder):
        return None
    
    print("\n---", propFolder, "---")
  
    propFolderPath = propDatabasePath + "/" + propFolder
    dataType = None
    
    for filename in os.listdir(path.join(propFolderPath)):
        if "PER" in filename:
            if dataType is None: #Some props have both sets of data, of which Selig is superior
                dataType = "apc"
                dataFileName = filename
        if ("geom" in filename) or ("static" in filename):
            dataType = "selig"
            break
                
    if dataType == "apc": #Data files from APC (manufacturer)
        with open(propFolderPath+"/"+dataFileName) as dataFile:
            dataFile = open(propFolderPath + "/" + dataFileName)
            firstLine = dataFile.readline().split()
            diaPitch = firstLine[0].split("x")
            diameter = float(diaPitch[0])
            pitch = float(re.search(r'\d+', diaPitch[1]).group())
            
            manufacturer = "APC"
                    
            #Now read through the file to read in measurements
            dataFile.seek(0)
            firstLine = dataFile.readline().split() #Get rid of the first line
            JN = []
            C_t = []
            
            for line in dataFile:
                
                line = line.replace("-", " ")
                entries = line.split()
                if len(entries) != 0:
                    if entries[0] == "PROP":
                        rpm = float(entries[3])
                    elif entries[0][0].isdigit():
                        if isNum(entries[1]) and isNum(entries[3]):
                            JN.append([float(entries[1]),rpm])
                            C_t.append(float(entries[3]))

        JNexp = np.asarray(JN).T
        print(JNexp.shape)
        C_texp = np.asarray(C_t)
        print(C_texp.shape)

    #----------------------------------END OF APC-----------------------------------------
        
    elif dataType == "selig": #Data files from U of I U-C
        diaPitch = propFolder.split("_")[1].split("x")
        diameter = float(diaPitch[0])
        met = False
        if diameter>50:
            diameter = diameter/25.4;
            met = True
        if "deg" in diaPitch[1]:
            pitch = 2*np.pi*0.525*diameter*np.tan(np.radians(float(re.search(r'\d+', diaPitch[1]).group())))
        else:
            pitch = float(diaPitch[1])
            if met:
                pitch = pitch/25.4;

        manufacturer = "UNKNOWN"
        manufacturers = [["an","AERONAUT"],
                         ["apc","APC"],
                         ["da","UIUC"],
                         ["ef","E-FLITE"],
                         ["gr","GRAUPNER"],
                         ["gws","GWS"],
                         ["kav","KAVON"],
                         ["kp","KP"],
                         ["kyosho","KYOSHO"],
                         ["ma","MASTER AIRSCREW"],
                         ["mi","MICRO INVENT"],
                         ["nr","UIUC"],
                         ["pl","PLANTRACO"],
                         ["ru","REV UP"],
                         ["union","UNION"],
                         ["vp","VAPOR"],
                         ["zin","ZINGALI"]]
        for manu in manufacturers:
            if manu[0] in propFolder:
                manufacturer = manu[1]
                break                 
        
        if manufacturer is "UIUC":
            return None #These props were 3D printed by UIUC and are not commercially available

        #Loop thorugh files to read in measurements
        JN = []
        C_t = []
        
        for dataFileName in os.listdir(path.join(propFolderPath)):
            if not ("static" in dataFileName or "geom" in dataFileName or "PER" in dataFileName or "spec2" in dataFileName):
                dataFileNameParts = dataFileName.split("_")#Pull apart the filename to extract the rpm value
                rpm = dataFileNameParts[-1].replace(".txt", "")
                with open(propFolderPath+"/"+dataFileName) as dataFile:
                    firstLine = dataFile.readline() #Throw away first line
                    
                    for line in dataFile:
                        entries = line.split()
                        JN.append([float(entries[0]),float(rpm)])
                        C_t.append(float(entries[1]))
                        
            elif "static" in dataFileName: #Static tests
                with open(propFolderPath+"/"+dataFileName) as dataFile:
                    dataFile = open(propFolderPath + "/" + dataFileName)
                    firstLine = dataFile.readline() #Throw away first line
                    
                    for line in dataFile:
                        entries = line.split()
                        JN.append([0.0,float(entries[0])])
                        C_t.append(float(entries[1]))
                        
        JNexp = np.asarray(JN).T
        print(JNexp.shape)
        C_texp = np.asarray(C_t)
        print(C_texp.shape)
                
    #-----------------------END OF SELIG/UIUC---------------------------------------------

    #Initial guesses for curve fitting
    C_tmax = max(C_texp)
    
    #Estimate variation in C_t due to N and J to seed the curve fit
    coefs,_ = fit.poly_fit(2,JNexp[0],C_texp)
    A = -coefs[1]
    coefs,_ = fit.poly_fit(2,JNexp[1],C_texp)
    B = -coefs[1]
    C = C_texp[np.argmin(JNexp[0]*JNexp[1])]
    k = 5
    guess = (C_tmax,A,B,C,k)
    print(guess)
    
    params, pcov = opt.curve_fit(CalcCt,JNexp,C_texp,guess,bounds=([0,0,-np.inf,-np.inf,0],[np.inf,np.inf,np.inf,np.inf,np.inf]),method='dogbox')
    
    print(params)
    C_tmax = params[0]
    A = params[1]
    B = params[2]
    C = params[3]        
    k = params[4]
    
    Jspace = np.linspace(0,max(JNexp[0])*1.5,25)
    Nspace = np.linspace(0,max(JNexp[1])*1.5,25)
    Jgrid,Ngrid = np.meshgrid(Jspace,Nspace)
    JN = np.stack([Jgrid.flatten(),Ngrid.flatten()])
    
    C_t = CalcCt(JN,C_tmax,A,B,C,k)
    
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    ax.scatter(JN[0],JN[1],C_t)
    ax.scatter(JNexp[0],JNexp[1],C_texp)
    ax.set_xlabel("J")
    ax.set_ylabel("N")
    ax.set_zlabel("C_t")
    ax.set_title(arg[0])
    ax.legend(["Predicted","Experimental"])
    plt.show()
    return params
        

#Specify which group of props to analyze
propDatabasePath = os.getcwd() + "/Props"
wholeDatabase = os.listdir(path.join(propDatabasePath))
apcTestProps = ["apc_16x10", "apce_4x3.3", "apcr-rh_9x4.5","apcsf_8x4.7","apcpn_21x10.5","apc-3blade_13.4x13.5","apc_8x3.75"]
seligTestProps = ["kyosho_10x6", "ance_8.5x6", "grcp_9x4", "kavfk_11x7.75", "mit_5x4", "rusp_11x4"]
mixedProps = apcTestProps + seligTestProps
problemProps = ["apcc_7.4x7.5"]
propSet = mixedProps

N_proc_max = 8

plt.close('all')
args = [(propFolder,propDatabasePath) for propFolder in propSet]

for arg in args:
    params = FitCoefs(arg)
