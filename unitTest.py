import propulsionUnitClass as unit

prop = "ance_8.5x6"
motor = "Kontronik Pyro 700-34"
battery = "Turnigy 5000mAh 40C"
numCells = 3
esc = "Kontronic SUN 3000"
altitude = 2000

test = unit.PropulsionUnit(prop, motor, battery, numCells, esc, altitude)
print("Initialization complete. Plotting thrust curves.")
test.PlotThrustCurves(100)

