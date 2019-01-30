Propulsion Unit Optimization Software

Created by Cory Goates (undergraduate, Utah State University)
Under supervision of Dr Doug Hunsaker (professor, Utah State University; director, USU AeroLab)
As part of the Engineering Undergraduate Research Program (EURP)

README (last revision: 10/31/18)

--------------------------------------------------------------------
INTRODUCTION
--------------------------------------------------------------------

The purpose of this software is to assist small UAS designers in selecting efficient and effective propulsion units (consisting of a propeller, motor, battery, and ESC) for UASs. This software includes a database of over 600 props, over 5000 motors, over 500 batteries, and over 500 ESCs, all commercially available. This software is meant to be a guide in selecting components. The results given are reasonably accurate, but approximations have to be made, especially in the modelling of propeller characteristics. The user is thus cautioned against trusting too much in the exact results of these analyses.

--------------------------------------------------------------------
PREREQUISITES
--------------------------------------------------------------------

It is assumed that the user already has Python 3 running on their machine. The software makes use of the following Python packages:

numpy
multiprocessing
matplotlib
scikit-aero

Please ensure these packages are installed and functional before using this software.

--------------------------------------------------------------------
SCRIPTS
--------------------------------------------------------------------

All relevant software for the user is contained in the /PropulsionOptimization directory. The /dev directory is used for development and does not need to be accessed. An SQL database, compiled from various other databases, is contained in the /Database directory. All scripts pull information from this database. A description of all scripts in this software package is given below:

---poly_fit.py---

Contains functions for performing linear fits.

---supportClasses.py---

Contains classes used by other scripts.

---plotDesignSpace.py---

The purpose of this script is to give the user a good idea of the design space they are working in, given a certain set of parameters. Based on these parameters, the script will determine a specified number of total propulsion units which meet these parameters. It will determine the maximum flight time achieved by each unit and plot these flight times versus the following characteristics:
-Propeller diameter
-Propeller pitch
-Motor Kv
-Battery voltage
-Battery capacity
-Total aircraft weight
-Throttle setting at max flight time
The unit which gives the highest flight time will be highlighted in red in each of these plots. The user can then select any other plotted point in these plots and the corresponding data points will be highlighted in the other plots. The user will also be presented with a full description of that unit's specifications (in the command line) and the thrust and speed curves for that unit (in a separate window).

The only argument is a .json file defining the search parameters, an example of which is
given below (explanatory comments given within // //):
----sampleSearch.json----
{
    "computation":{
        "units":1000, //Number of propulsion units to find in the design space.//
        "processes":8, //Maximum number of processes to be used in parallel computation.//
        "outlierStdDevs":5 //Number of standard deviations of the half-normal distribution within which designs are considered feasible.//
    },
    "condition":{
        "altitude":0, //Flight altitude.//
        "airspeed":10 //Flight cruise speed.//
    },
    "goal":{ //One and only one of these parameters must be specified. Set for cruise condition.//
        "thrust":0, //Thrust required from the propulsion unit.//
        "thrustToWeightRatio":0.3 //Thrust to weight ratio required (requires emptyWeight to be defined.//
    },
    "aircraft":{
        "emptyWeight":1, //Weight of the aircraft minus the propulsion system.//
        "components":{ //These parameters are optional, but only one for each component may be specified.//
            "propeller":{
                "name":"",
                "manufacturer":""
            },
            "motor":{
                "name":"",
                "manufacturer":""
            },
            "esc":{
                "name":"",
                "manufacturer":""
            },
            "battery":{
                "name":"",
                "manufacturer":""
            }
        }
    }
}

The component parameters in the .json file are all optional. Specifying a component name limits
the search to propulsion units including that specific component. Specifying a component manufacturer
limits the search to a single manufacturer for that component. Please note that some component
manufacturers have very few components in our current database, and specifying this may limit the
search more than desirable. Only one of these parameters may be specified for each component at most.

Once the search is complete (i.e. the specified number of designs has been considered), the propulsion
unit which has the longest flight time will be output to the terminal. A figure will also be displayed
containing 6 plots which describe (in part) the design space. Each point on a plot represents a possible
design; each design is reflected in each plot. The y axis of each plot is the flight time given by a
design, and the x axis of each plot is a defining parameter of the design (currently: prop diameter, prop
pitch, motor Kv constant, battery voltage, battery capacity, and total unit weight). The user may select
any design in any one of the plots to see a plot of its thrust at various airspeeds and throttle settings.
A corresponding plot of propeller speeds is also shown and all details of the design are printed to the
terminal. Selecting a design will also highlight that design in each of the 6 plots, so that general
patterns in the design space can be opserved.

The developer is of the opinion that outliers should be ignored. Testing has shown that these arise from
error in the component models and should not be trusted as feasible, high-performance designs. Realistic
designs will be found closer to the main cluster of designs.

PLEASE NOTE:
Speed is specified in ft/s, thrust and weight in lbf, altitude in ft.

--------------------------------------------------------------------
KNOWN ISSUES
--------------------------------------------------------------------

10/31/2018
Due to the nature of fitting experimental data to curves, some props show erroneous results at very high and very low RPM and very low and very high advance ratio. Work is being done to improve these fits to more accurately represent propeller performance.
