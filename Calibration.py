# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 17:46:09 2023

@author: Quentin Rauschenbach
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import unisacsi.Ocean as Oc
import matplotlib

import datetime
from pandas.tseries.offsets import DateOffset
inpath = "C:/Users/qraus/Documents/Uni/9_22-23WiSe/Measurement Electronics/Temperature_Logger/data/adjusted/"
#%%

files = glob.glob(inpath +"*")
#T_start = np.zeros(len(files))
#T_end   = np.zeros(len(files))
plt.figure(figsize = (10,8))
i = 0
for file in files[:]:
    name = file.split("/")[-1].split("_")[-1].split(".")[0]
    print(name)
    
    df = pd.read_csv(file, sep=',', comment='#',names=["time","millis","ID","temperature"])
    
    df["time"] = pd.to_datetime(df["time"], utc=True).dt.tz_localize(None)
    if name != "calibration":
        plt.plot(df["time"].values[800:],df["temperature"].values[800:],label=name,alpha = 0.5,linestyle = "--")
        print(df["temperature"].values[10])
    else:
        plt.plot(df["time"].values[:],df["temperature"].values[:],label=name)

    plt.legend()