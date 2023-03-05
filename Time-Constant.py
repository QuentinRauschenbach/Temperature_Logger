# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 09:48:21 2023

@author: Quentin Rauschenbach
"""

#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import unisacsi.Ocean as Oc
import matplotlib

import datetime

inpath = "C:/Users/qraus/Documents/Uni/9_22-23WiSe/Measurement Electronics/Temperature_Logger/data/"

def add_colorbar(mappable,label):
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    import matplotlib.pyplot as plt
    last_axes = plt.gca()
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="1.5%", pad=0.1)
    cbar = fig.colorbar(mappable, cax=cax,label=label)
    plt.sca(last_axes)
    return cbar

#%%
t1 = 210
t2 = 300

files = glob.glob(inpath +"TSENSOR*.log")
plt.figure(figsize = (8,6))
for file in files[:]:
    print(file)
    tsticks = pd.read_csv(file, 
                          sep=',', comment='#', header=None,
                          names=['time', 'millis', 'ID', 'temperature'])
    
    # convert date into datetime-format
    tsticks["time"] = pd.to_datetime(tsticks["time"], utc=True).dt.tz_localize(None)
    
    # fill in blank values with NaNs
    tsticks = tsticks.replace(r'^\s*$', np.nan, regex=True)
    #tsticks["hex-ID"] = tsticks["hex-ID"].astype("string")
    
    
    plt.plot(tsticks["millis"].values[t1:t2],tsticks["temperature"].values[t1:t2], label=file.split("/")[-1].split("_")[-1].split(".")[0])
plt.title("Time Constant",weight= "bold")    
plt.ylabel("Temperature [°C]")
plt.xlabel("time [ms]")
plt.legend(loc=1)
plt.grid()

