import vehicleClasses as vc

frameWeight = 2
desTtW = 1
cruiseSpeed = 10
altitude = 2000
maxIterations = 20000
plane = vc.Airplane(frameWeight)
plane.RSOptimizeThrustToWeight(desTtW,cruiseSpeed,altitude,maxIterations)
