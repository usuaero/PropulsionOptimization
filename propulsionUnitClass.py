import numpy as np
import matplotlib.pyplot as plt
import sqlite3 as sql
import supportClasses as s
from skaero.atmosphere import coesa


#Converts rads per second to rpms
def toRPM(rads):
    return rads*30/np.pi

#A class that defines an entire electric propulsion unit
class PropulsionUnit:

    #Initialize the class from components in the component database 
    def __init__(self, prop, motor, battery, numCells, esc, altitude):
        
        #Open database and read records from database
        db = sql.connect("Database/components.db")
        dbcur = db.cursor()

        #Fetch prop data
        formatString = """select * from Props where Name = "{propName}" """
        command = formatString.format(propName = prop)
        dbcur.execute(command)
        propRecord = dbcur.fetchall()
        propInfo = np.asarray(propRecord[0])
        print(propInfo)
        self.prop = s.Propeller(propInfo[1],propInfo[2],propInfo[3],propInfo[4:])


        #Fetch motor data
        formatString = """select * from Motors where Name = "{motorName}" """
        command = formatString.format(motorName = motor)
        dbcur.execute(command)
        motorRecord = dbcur.fetchall()
        motorInfo = np.asarray(motorRecord[0])
        print(motorInfo)
        self.motor = s.Motor(motorInfo[1],motorInfo[2],motorInfo[3],motorInfo[5],motorInfo[4],motorInfo[6])

        #Fetch battery data
        formatString = """select * from Batteries where Name = "{batteryName}" """
        command = formatString.format(batteryName = battery)
        dbcur.execute(command)
        batteryRecord = dbcur.fetchall()
        batteryInfo = np.asarray(batteryRecord[0])
        print(batteryInfo)
        self.batt = s.Battery(batteryInfo[1], numCells, batteryInfo[3], batteryInfo[6], batteryInfo[5], batteryInfo[4])

        #Fetch ESC data
        formatString = """select * from ESCs where Name = "{escName}" """
        command = formatString.format(escName = esc)
        dbcur.execute(command)
        escRecord = dbcur.fetchall()
        escInfo = np.asarray(escRecord[0])
        print(escInfo)
        self.esc = s.ESC(escInfo[1], escInfo[5], escInfo[2], escInfo[4])
        
        #Initialize exterior parameters to be set later
        self.prop.vInf = 0
        self.prop.angVel = 0
        _,_,_,self.airDensity = coesa.table(altitude)
        db.close()
        

        
    #Computes motor torque given throttle setting and revolutions (rpm)
    def CalcTorque(self, throttle, revs):
        etaS = 1 - 0.078*(1 - throttle)
        Im = (etaS*throttle*self.batt.V0 - (self.motor.Gr/self.motor.Kv)*revs)/(etaS*throttle*self.batt.R + self.esc.R + self.motor.R)
        return 7.0432*self.motor.Gr/self.motor.Kv * (Im - self.motor.I0)
    
    #Computes thrust produced at a given cruise speed and throttle setting
    def CalcCruiseThrust(self, cruiseSpeed, throttle):
        self.prop.vInf = cruiseSpeed
        
        #Determine the shaft angular velocity at which the motor torque and propeller torque are matched
        #Uses a secant method
        errorBound = 0.000001
        approxError = 1 + errorBound
        w0 = 300 #An initial guess of the prop's angular velocity
        self.prop.angVel = w0
        self.prop.CalcProperties()
        self.prop.CalcTorqueCoef()
        f0 = self.CalcTorque(throttle, toRPM(w0)) - self.prop.Cl*self.airDensity*(w0/(2*np.pi))**2*self.prop.diameter**5
        w1 = w0 * 1.1
        
        while approxError >= errorBound:
            
            self.prop.angVel = w1
            self.prop.CalcProperties()
            self.prop.CalcTorqueCoef()
            motorTorque = self.CalcTorque(throttle, toRPM(w1))
            propTorque = self.prop.Cl*self.airDensity*(w1/(2*np.pi))**2*self.prop.diameter**5
            f1 = motorTorque - propTorque
            
            w2 = w1 - (f1*(w0 - w1))/(f0 - f1)
            
            approxError = abs((w2 - w1)/w2)
            
            w0 = w1
            f0 = f1
            w1 = w2
        
        self.prop.angVel = w2
        self.prop.CalcProperties()
        self.prop.CalcThrustCoef()
            
        return self.prop.Ct*self.airDensity*(w0/(2*np.pi))**2*self.prop.diameter**4
    
    #Computes required throttle setting for a given thrust and cruise speed
    def CalcCruiseThrottle(self, cruiseSpeed, reqThrust):
        
        #Determine the throttle setting that will produce the required thrust
        #Uses a secant method
        errorBound = 0.000001
        approxError = 1 + errorBound
        t0 = 0.5
        T0 = self.CalcCruiseThrust(cruiseSpeed, t0) - reqThrust
        t1 = t0*1.1
        
        while approxError >= errorBound and t1 > 0 and t1 < 1:
            
            T1 = self.CalcCruiseThrust(cruiseSpeed, t1) - reqThrust
            T1 = self.CalcCruiseThrust(cruiseSpeed, t1) - reqThrust
            
            t2 = t1 - (T1*(t0 - t1))/(T0 - T1)
            
            approxError = abs((t2 - t1)/t2)
    
            t0 = t1
            T0 = T1
            t1 = t2
        
        if t2 > 1 or t2 < 0:
            return None
        
        return t2
        
    #Plots thrust curves for propulsion unit up to a specified airspeed
    def PlotThrustCurves(self, maxAirspeed):
        
        vel = np.linspace(0, maxAirspeed, 10)
        thr = np.linspace(0, 1, 10)
        thrust = np.zeros((10, 10))
        
        for i in range(10):
            for j in range(10):
                
                #print("Freestream Velocity: ", vel[i])
                #print("Throttle Setting: ", thr[j])
                thrust[i][j] = self.CalcCruiseThrust(vel[i], thr[j])
                
            plt.plot(thr, thrust[i])
        plt.title("Thrust Curves at Various Cruise Speeds for: " + str(self.prop.name) + ", " + str(self.motor.name) + ", and " + str(self.batt.name))
        plt.ylabel("Thrust [N]")
        plt.xlabel("Throttle Setting")
        plt.legend(list(vel))
