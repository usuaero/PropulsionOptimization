#Used to organize motors into the database
#There are three sources of motor parameters: DriveCalc, MotoCalc, csv from Josh
import sqlite3 as sql
import numpy as np
import os
from os import path
import csv

def isNum(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

#Kv should be in rpms/V
#current should be in amps
#resistance should be in ohms
#weight should be in ounces

connection = sql.connect("components.db")
motoCalcFile = open("C:/Program Files (x86)/MotoCalc 8/Initial/MOTOR8.DBF")
cursor = connection.cursor()
cursor.execute("drop table Motors")# The database is refreshed every time

cursor.execute("""CREATE TABLE Motors (id INTEGER PRIMARY KEY, 
                                      name VARCHAR(40), 
                                      kv FLOAT, 
                                      gear_ratio FLOAT, 
                                      resistance FLOAT, 
                                      no_load_current FLOAT,
                                      weight FLOAT);""")

print("Reading MotoCalc Database")
firstLine = True
for line in motoCalcFile:
    
    if firstLine:
        firstLine = False
        continue
    
    entries = line
    
print(entries)
totalLength = len(entries)
entryLength = len(" Neu F3A-1 1513/2Y                          1300.00   1.50000   0.01500  18.00000TF")
numMotors = len(entries)//entryLength
print(numMotors)

motors = [entries[i:i+entryLength] for i in range(0, totalLength, entryLength)]
motors.pop()

for motor in motors:
    print(motor)
    name = motor[0:40].replace("  ", "")
    if isNum(motor[41:51]):
        Kv = float(motor[41:51])
    else:
        Kv = None
    if isNum(motor[51:62]):
        I0 = float(motor[51:62])
    else:
        I0 = None
    if isNum(motor[63:73]):
        R = float(motor[63:73])
    else:
        R = None
    if isNum(motor[73:81]):
        weight = float(motor[73:81])
    else:
        weight = None
    
    print([name, Kv, I0, R, weight])

    formatStr = """INSERT INTO Motors (name, kv, resistance, no_load_current, weight) VALUES ("{motorName}", "{motorKv}", "{motorResistance}", "{motorNoLoadCurrent}", "{motorWeight}");"""
    command = formatStr.format(motorName = name, motorKv = Kv, motorResistance = R, motorNoLoadCurrent = I0, motorWeight = weight)
    cursor.execute(command)

print("Reading Database after MotoCalc")
cursor.execute("SELECT * FROM Motors")
result = cursor.fetchall()
for r in result:
    print(r)

print("Reading DriveCalc database")

inDatabaseFile = os.getcwd() + "/Motors/DCbase.dcd"
inConnection = sql.connect(inDatabaseFile)
inCursor = inConnection.cursor()

inCursor.execute("SELECT * FROM motors")
motors = inCursor.fetchall()

for motor in motors:

    formatStr = """INSERT INTO Motors (name, kv, resistance, weight, gear_ratio) VALUES ("{motorName}", "{motorKv}", "{motorResistance}", "{motorWeight}", "{motorGearRatio}");"""
    command = formatStr.format(motorName = str(motor[2]).replace("\"", " "), motorKv = str(motor[16]), motorResistance = str(motor[17]), motorWeight = str(motor[13]*0.035274), motorGearRatio = str(motor[14]))
    cursor.execute(command)
    
print("Reading Database after DriveCalc")
cursor.execute("SELECT * FROM Motors")
result = cursor.fetchall()
for r in result:
    print(r)
    
print(cursor.description)
inCursor.close()

print("Reading motors from csv")
motorCsv = open(os.getcwd()+"/Motors/motor.csv")
motorCsvReader = csv.reader(motorCsv,delimiter=',')
firstLine = True
for row in motorCsvReader:
    if firstLine:
        firstLine = False
        continue
    print(row)
    name = " ".join(row[0:1])
    kv = row[2]
    resistance = row[3]
    I0 = row[4]

    formatStr = """INSERT INTO Motors (name, kv, resistance, no_load_current) VALUES ("{motorName}", "{motorKv}", "{motorResistance}", "{motorI0}");"""
    command = formatStr.format(motorName = name, motorKv = kv, motorResistance = resistance, motorI0 = I0)
    cursor.execute(command)

print("Reading Database after CSV")
cursor.execute("SELECT * FROM Motors")
result = cursor.fetchall()
for r in result:
    print(r)

connection.commit()
cursor.close()
