Propulsion Unit Optimization Software

Created by Cory Goates (undergraduate, Utah State University)
Under supervision of Dr Doug Hunsaker (professor, Utah State University; director, USU AeroLab)
As part of the Engineering Undergraduate Research Program (EURP)

README (last revision: 10/25/18)

--------------------------------------------------------------------
INTRODUCTION
--------------------------------------------------------------------

The purpose of this software is to assist small UAS designers in selecting efficient and effective propulsion units (consisting of a propeller, motor, battery, and ESC) for UASs. This software includes a database of over 600 props, over 5000 motors, over 500 batteries, and over 500 ESCs, all commercially available. This software is meant to be a guide in selecting components. The results given are reasonably accurate, but approximations have to be made, especially in the modelling of propeller characteristics. The user is thus cautioned against trusting too much in the exact results of these analyses.

--------------------------------------------------------------------
PREREQUISITES
--------------------------------------------------------------------

It is assumed that the user already has Python 3 running on their machine. The software makes use of the following Python packages:

numpy
sqlite3
multiprocessing
matplotlib
scikit-aero

Please ensure these packages are installed and functional before using this software.

--------------------------------------------------------------------
SCRIPTS
--------------------------------------------------------------------

All relevant software for the user is contained in the /dist directory. The /dev directory is used for development and does not need to be accessed. An SQL database, compiled from various other databases, in contained in the /dist/Database directory. All scripts pull information from this databas. A description of all scripts in this software package is given below:

ploy_fit.py

Contains functions for performing linear fits.

supportClasses.py

Contains classes used by other scripts.

plotDesignSpace.py

The purpose of this script is to give the user a good idea of the design space they are working in, given a certain set of parameters. Based on these parameters, the script will determine a specified number of total propulsion units which meet these parameters. It will determine the maximum flight time achieved by each unit and plot these flight times versus the following characteristics:
-Propeller diameter
-Propeller pitch
-Motor Kv
-Battery voltage
-Battery capacity
-Total aircraft weight
The unit which gives the highest flight time will be highlighted in red in each of these plots. The user can then select any other plotted point in these plots and the corresponding data points will be highlighted in the other plots. The user will also be presented with a full description of that unit's specifications (in the command line) and the thrust and speed curves for that unit (in a separate window).

This script operates in two modes: required thrust and required thrust-to-weight ratio. For both, the user must specify the number of units to consider, the number of subprocesses to be used (this script does the bulk of its computation in parallel), the cruise speed, and the altitude. To analyze simply for a required thrust, this is the only other parameter the user must specify. To analyze for thrust-to-weight ratio, the user must also specify the required thrust-to-weight ratio and the empty weight of the airframe. Examples of both types of command are given below:

$python plotDesignSpace.py units 1000 mp 8 speed 10 thrust 1 alt 2000
$python plotDesignSpace.py units 10000 mp 8 speed 15 thrustToWeight 0.4 alt 1000 weight 2

PLEASE NOTE:
Speed is specified in ft/s, thrust and weight in lbf, altitude in ft.

--------------------------------------------------------------------
KNOWN ISSUES
--------------------------------------------------------------------
