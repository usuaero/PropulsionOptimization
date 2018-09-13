import propulsionUnitClass as unit

prop = "kyosho_10x6"
motor = "Kontronik Pyro 700-34"
battery = "Turnigy 5000mAh 40C"
numCells = 3
esc = "Kontronic SUN 3000"
altitude = 2000

test = unit.PropulsionUnit(prop, motor, battery, numCells, esc, altitude, True)
print("Initialization complete. Plotting thrust curves.")
maxAirspeed = 100
numVelocities = 11
numThrottles = 100
test.PlotThrustCurves(maxAirspeed, numVelocities, numThrottles)

