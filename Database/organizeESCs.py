#used to organize ESCs from various sources into the component database
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

cursor.execute("drop table ESCs")
cursor.execute("""create table ESCs (id INTEGER PRIMARY KEY, 
                                      Name VARCHAR(40), 
                                      Imax FLOAT, 
                                      Ipeak FLOAT, 
                                      Weight FLOAT,
                                      Ri FLOAT,
                                      NiMHmin INT,
                                      NiMHmax INT,
                                      LiPomin INT,
                                      LiPomax INT);""")

print("Reading MotoCalc Database")
escFilePath = os.getcwd() + "/ESCs/ESC8.DBF"
escFile = DBF(escFilePath)

for record in escFile:
    print(record)
    if record["MAXCURRENT"] == 0 or record["MAXCURRENT"] == None:
        continue

    formatStr = """INSERT INTO ESCs (Name, Weight, Imax, Ri) VALUES ("{name}", "{weight}",  "{iMax}", "{Ri}");"""
    command = formatStr.format(name = record["ESCNAME"], weight = record["WEIGHT"], iMax = record["MAXCURRENT"], Ri = record["RESISTANCE"])
    cursor.execute(command)

print("Reading Database after MotoCalc")
cursor.execute("SELECT * FROM ESCs")
result = cursor.fetchall()
for r in result:
    print(r)

print("Reading DriveCalc database")

inDatabaseFile = os.getcwd() + "/ESCs/DCbase.dcd"
inConnection = sql.connect(inDatabaseFile)
inCursor = inConnection.cursor()

inCursor.execute("SELECT * FROM ESC")
escs = inCursor.fetchall()

for esc in escs:

    if esc[4] == 0 or esc[4] == None:
        continue
    formatStr = """INSERT INTO ESCs (Name, Imax, Ipeak, Weight, Ri, NiMHmin, NiMHmax, LiPomin, LiPomax) VALUES ("{name}", "{iMax}", "{iPeak}", "{weight}", "{res}", "{nmhMin}", "{nmhMax}", "{liMin}", "{liMax}");"""
    command = formatStr.format(name = str(esc[2]), iMax = str(esc[4]), iPeak = str(esc[5]), weight = str(esc[7]), res  = str(esc[6]), nmhMin = str(esc[8]), nmhMax = str(esc[9]), liMin = str(esc[10]), liMax = str(esc[11]))
    cursor.execute(command)
    
print("Reading Database after DriveCalc")
cursor.execute("SELECT * FROM ESCs")
result = cursor.fetchall()
for r in result:
    print(r)

inCursor.close()
connection.commit()
connection.close()
