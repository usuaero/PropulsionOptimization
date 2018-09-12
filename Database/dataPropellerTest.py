#used to test the DataPropeller class
import propellerClass as prop
import propulsionUnitClass as prpl
import numpy as np
import matplotlib.pyplot as plt


testFolders = ["grcp_9x4", "apc_9x4", "mit_5x4"]

for testFolder in testFolders:
    testProp = prop.DataPropeller(testFolder)
    
    for i in range(testProp.rpmCount):
        plt.plot(testProp.coefArray[i,:,0], testProp.coefArray[i,:,2])
        
    plt.xlabel("Prop Advance Ratio")
    plt.ylabel("Thrust Coef")
    plt.title(testFolder)
    plt.legend(list(testProp.rpms))
    plt.show()
