import propulsionUnitClass as unit

prop = "apc_9x3"
motor = "EMAX GF2210/20 1534KV"
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

