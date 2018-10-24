import sqlite3 as sql
import itertools
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import pickle
from mpl_toolkits.mplot3d import Axes3D
import os
from os import path

def polyfit2d(x, y, z, order=3):
    ncols = (order + 1)**2
    G = np.zeros((x.size, ncols))
    ij = itertools.product(range(order+1), range(order+1))
    for k, (i,j) in enumerate(ij):
        G[:,k] = x**i * y**j
    m, _, _, _ = np.linalg.lstsq(G, z)
    return m

def polyval2d(x, y, m):
    order = int(np.sqrt(len(m))) - 1
    ij = itertools.product(range(order+1), range(order+1))
    z = np.zeros_like(x)
    for a, (i,j) in zip(m, ij):
        z += a * x**i * y**j
    return z

#First, determine prop coefs as a function of pitch and diameter
db = sql.connect("Database/components.db")
dbcur = db.cursor()
dbcur.execute("select * from Props")
rawProps = dbcur.fetchall()
props = np.asarray(rawProps)
numProps = max(np.shape(props))

numThrustCoefs = (props[1,4].astype(int)+1)*(props[1,5].astype(int)+1)

for coef in range(numThrustCoefs):
    fig = plt.figure(figsize=plt.figaspect(1.))
    ax = fig.add_subplot(1,1,1,projection='3d')
    diameter = np.zeros(numProps)
    pitch = np.zeros(numProps)
    coefficient = np.zeros(numProps)

    for i, prop in enumerate(props):
        ax.scatter(prop[2].astype(float),prop[3].astype(float),prop[8+coef].astype(float),c=[[1,0,0]],depthshade = True)
        diameter[i] = prop[2].astype(float)
        pitch[i] = prop[3].astype(float)
        coefficient[i] = prop[8+coef].astype(float)
    
    m = polyfit2d(diameter,pitch,coefficient)
    dd, pp = np.meshgrid(np.linspace(diameter.min(),diameter.max(),30),np.linspace(pitch.min(),pitch.max(),30))
    predCoef = polyval2d(dd, pp, m)
#    ax.plot_wireframe(dd,pp,predCoef)

    ax.set_xlabel("Diameter [in]")
    ax.set_ylabel("Pitch [in]")    
    plt.show()

db.close()
