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
t1 = 0
t2 = 500

t_const = 0.1 #°C below which diff we consinder Temp as const
av_const = 30 #s averaging period

c = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
files = glob.glob(inpath +"TSENSOR*.log")
#T_start = np.zeros(len(files))
#T_end   = np.zeros(len(files))
plt.figure(figsize = (10,6))
i = 0
for file in files[:]:
    print(file.split("/")[-1])
    tsticks = pd.read_csv(file, 
                          sep=',', comment='#', header=None,
                          names=['time', 'millis', 'ID', 'temperature'])
    
    # convert date into datetime-format
    tsticks["time"] = pd.to_datetime(tsticks["time"], utc=True).dt.tz_localize(None)
    # fill in blank values with NaNs
    tsticks = tsticks.replace(r'^\s*$', np.nan, regex=True)
    #tsticks["hex-ID"] = tsticks["hex-ID"].astype("string")
    #print(tsticks["temperature"].values[t2])
    
    diff = tsticks["temperature"].values[1:] - tsticks["temperature"].values[:-1]
    start = np.where(abs(diff[190:350])>=t_const)[0][0]+190
    
    diff_200000 = abs(tsticks['millis']-200000)
    millis_200000 = np.where(diff_200000 == min(diff_200000))[0][0]
    millis_start = np.where(abs(diff[millis_200000:350]) >= 0.1)[0][0]
    start_time = tsticks['millis'][millis_200000+millis_start]
    
    # millis_end = np.where(abs(diff[millis_200000+millis_start:]) <= 0.03)[0][0]
    # end_time = tsticks['millis'][millis_200000+millis_start+millis_end]
    # print(end_time)
    
    sum_diff = np.zeros(len(diff))
    n= 100
    for k in range(len(diff)-n):
        sum_diff[k+n-1] = np.nanmean(diff[k:k+n-1])
    
    millis_end = np.where(abs(sum_diff[millis_200000+millis_start+50:]) <= 0.1)[0][0]
    end_time = tsticks['millis'][millis_200000+millis_start+millis_end+50]
    #print(end_time)
    stop = millis_200000+millis_start+millis_end+50
    Temp_end = np.nanmean(tsticks['temperature'][stop:stop+30])
    print(Temp_end)
    start = millis_200000+millis_start
    Temp_start = np.nanmean(tsticks['temperature'][start-30:start])
    print(Temp_start)
    
    
    
    # time const
    #0.632
    
    Temp_tau = Temp_end +1/np.e *(Temp_start-Temp_end)
    print(Temp_tau)
    
    #Temp_tau = 0.632 * np.nanmean(tsticks['temperature'][stop:stop+30])
    diff_temp = abs(tsticks['temperature'].values[:330]-Temp_tau)
    time_tau = tsticks['millis'][np.where(diff_temp == np.nanmin(diff_temp))[0][0]]
    print(time_tau)
    
    print("")
        
    # plot  
    
    plt.scatter(time_tau,Temp_tau,marker="o",c=c[i],zorder=4)

    
    plt.hlines(np.nanmean(tsticks['temperature'][start-30:start]),0,550000,zorder=1000,linestyle="--",color=c[i])
    
    plt.hlines(np.nanmean(tsticks['temperature'][stop:stop+30]),0,550000,zorder=1000,linestyle="--",color=c[i])
    plt.scatter(start_time,tsticks["temperature"].values[millis_200000+millis_start],marker="x",c=c[i],zorder=1)
    plt.scatter(end_time,tsticks["temperature"].values[millis_200000+millis_start+millis_end+50],marker="o",c=c[i],zorder=2)
    plt.plot(tsticks["millis"].values[t1:t2-1],sum_diff[t1:t2-1] ,c=c[i])
    
    plt.plot(tsticks["millis"].values[t1:t2],tsticks["temperature"].values[t1:t2], label=file.split("/")[-1].split("_")[-1].split(".")[0],alpha=0.5,c=c[i],zorder=3)
    i+=1

plt.title("Time Constant",weight= "bold")    
plt.ylabel("Temperature [°C]")
plt.xlabel("time [ms]")
plt.xlim(160000,450000)
plt.ylim(0,25)
plt.legend()
plt.grid()

