#used to organize batteries from various sources into the component database
import os
import sqlite3 as sql
from dbfread import DBF

def isNum(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

databaseFile = os.getcwd() + "/components.db"
connection = sql.connect(databaseFile)
cursor = connection.cursor()

cursor.execute("drop table Batteries")
cursor.execute("""create table Batteries (id INTEGER PRIMARY KEY, 
                                      Name VARCHAR(40), 
                                      Imax FLOAT, 
                                      Capacity FLOAT, 
                                      Weight FLOAT,
                                      Ri FLOAT,
                                      Volt FLOAT,
                                      Chem VARCHAR);""")

print("Reading MotoCalc Database")
battFilePath = os.getcwd() + "/Batteries/CELL8.DBF"
battFile = DBF(battFilePath)

for record in battFile:
    print(record)

    formatStr = """INSERT INTO Batteries (Name, Imax, Capacity, Weight, Ri, Volt, Chem) VALUES ("{battName}", {battImax}, {battCap}, {battWeight}, {battRi}, {battVolt}, "{battChem}");"""

    #Check if the c rating is given and use that to define max current
    if isNum(record["CRATING"]):
        iMax = record["CAPACITY"]/1000*record["CRATING"]
    else:
        iMax = "NULL"

    if isNum(record["VOLTAGE"]):
        volt = record["VOLTAGE"]
    else:
        volt = "NULL"

    if isNum(record["CELLTYPE"]):
        chem = record["CELLTYPE"]
    else:
        chem = "NULL"

    command = formatStr.format(battName = record["CELLNAME"], battImax = iMax, battCap = record["CAPACITY"], battWeight = record["WEIGHT"], battRi = record["INTERTANCE"], battVolt = volt, battChem = chem)
    print(command)
    cursor.execute(command)

print("Reading Database after MotoCalc")
cursor.execute("SELECT * FROM Batteries")
result = cursor.fetchall()
for r in result:
    print(r)

print("Reading DriveCalc database")

inDatabaseFile = os.getcwd() + "/Batteries/DCbase.dcd"
inConnection = sql.connect(inDatabaseFile)
inCursor = inConnection.cursor()

inCursor.execute("SELECT * FROM Batteries")
batteries = inCursor.fetchall()

for battery in batteries:

    formatStr = """INSERT INTO Batteries (Name, Imax, Capacity, Weight, Ri, Volt) VALUES ("{battName}", "{battImax}", "{battCap}", "{battWeight}", "{battRi}", "{battVolt}");"""
    if isNum(battery[7]): #Must check because python will not multiply a None by a float for the unit conversion
        weight = battery[7]*0.35274
    else:
        weight = battery[7]
    command = formatStr.format(battName = str(battery[2]), battImax = str(battery[4]), battCap = str(battery[6]), battWeight = str(weight), battRi = str(battery[8]), battVolt = str(battery[9]))
    cursor.execute(command)
    
print("Reading Database after DriveCalc")
cursor.execute("SELECT * FROM Batteries")
result = cursor.fetchall()
for r in result:
    print(r)

# Code for cleaning database
cursor.execute("update Batteries set Chem = 'LiPo' where Volt = 3.7")

print("Reading Database after Cleaning")
cursor.execute("SELECT * FROM Batteries")
result = cursor.fetchall()
for r in result:
    print(r)

    
inCursor.close()
connection.commit()
connection.close()
