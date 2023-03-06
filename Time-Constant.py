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
from pandas.tseries.offsets import DateOffset

inpath = "C:/Users/qraus/Documents/Uni/9_22-23WiSe/Measurement Electronics/Temperature_Logger/data/"

def create_time_axis(df):
    print("----- Creating time axis -----")
    df["time"] = tsticks["time"]+DateOffset(years=23,months=2,days=1,hours=15,minutes=48)

    for i in range(len(df["time"].values)):
        df["time"][i] = df["time"][i]+DateOffset(seconds=df["millis"].values[i]/1000)
        
    df.to_csv(inpath+"test.LOG",sep=',',index=False)
    return df

#%%

callibration = pd.read_csv(inpath +"c_tsensor_calibration_time_constant_new.log", 
                      sep=',', comment='#', header=None,
                      names=['time', 'temperature'])
callibration["time"] = pd.to_datetime(callibration["time"], utc=True).dt.tz_localize(None)

#%%
t1 = 0
t2 = 500

t_const = 0.1 #°C below which diff we consinder Temp as const
av_const = 30 #s averaging period


c = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
files = glob.glob(inpath +"TSENSOR*.log")

plt.figure(figsize = (10,8))

for i, file in enumerate(files[:]):
    name = file.split("/")[-1].split("_")[-1].split(".")[0]
    print(name)
    tsticks = pd.read_csv(file, 
                          sep=',', comment='#', header=None,
                          names=['time', 'millis', 'ID', 'temperature'])
    
    # convert date into datetime-format
    tsticks["time"] = pd.to_datetime(tsticks["time"], utc=True).dt.tz_localize(None)
    
    # Creating time axis for the ones without a functioning RTC
    if name in ["LG", "KM"]:
        tsticks = create_time_axis(tsticks)
    
    # fill in blank values with NaNs
    tsticks = tsticks.replace(r'^\s*$', np.nan, regex=True)

    # get "shock" time
    diff  = tsticks["temperature"].values[1:] - tsticks["temperature"].values[:-1]    
    diff_200000 = abs(tsticks['millis']-200000)
    millis_200000 = np.where(diff_200000 == min(diff_200000))[0][0]
    millis_start = np.where(abs(diff[millis_200000:350]) >= 0.1)[0][0]
    start_index = millis_200000+millis_start
    start_time = tsticks['millis'][start_index]
    
    Offset = tsticks["time"][start_index] - callibration["time"][2]
    
    print("shock ",tsticks["time"][start_index])
    print("Offset",tsticks["time"][start_index] - callibration["time"][2])
    print("old   ",tsticks["time"][0])
    print("new   ",tsticks["time"][0]-Offset)
    
    tsticks["time"] = tsticks["time"] -Offset
    print("shock ",tsticks["time"][start_index])
        
    sum_diff = np.zeros(len(diff))
    n= 100
    for k in range(len(diff)-n):
        sum_diff[k+n-1] = np.nanmean(diff[k:k+n-1])
    
    millis_end = np.where(abs(sum_diff[millis_200000+millis_start+50:]) <= 0.1)[0][0]
    end_time = tsticks['millis'][millis_200000+millis_start+millis_end+50]
    #print(end_time)
    stop = millis_200000+millis_start+millis_end+50
    Temp_end = np.nanmean(tsticks['temperature'][stop:stop+30])
    #print(Temp_end)
    start = millis_200000+millis_start
    Temp_start = np.nanmean(tsticks['temperature'][start-30:start])
    #print(Temp_start)
    
    
    
    # time const
    Temp_tau = Temp_end +1/np.e *(Temp_start-Temp_end)
    #print(Temp_tau)
    
    #Temp_tau = 0.632 * np.nanmean(tsticks['temperature'][stop:stop+30])
    diff_temp = abs(tsticks['temperature'].values[:330]-Temp_tau)
    time_tau = tsticks['millis'][np.where(diff_temp == np.nanmin(diff_temp))[0][0]]
    #print(time_tau)
    print("")
        
    # plot  
    plt.hlines(np.nanmean(tsticks['temperature'][start-30:start]),0,550000,zorder=0,linestyle="--",color=c[i])
    plt.hlines(np.nanmean(tsticks['temperature'][stop:stop+30]),0,550000,zorder=0,linestyle="--",color=c[i])
    
    plt.scatter(start_time,tsticks["temperature"].values[millis_200000+millis_start],marker="x",c=c[i],zorder=1)
    plt.scatter(end_time,tsticks["temperature"].values[millis_200000+millis_start+millis_end+50],marker="o",c=c[i],zorder=2)
    plt.scatter(time_tau,Temp_tau,marker="o",c=c[i],zorder=4)
    
    plt.plot(tsticks["millis"].values[t1:t2-1],sum_diff[t1:t2-1] ,c=c[i])
    plt.plot(tsticks["millis"].values[t1:t2],tsticks["temperature"].values[t1:t2], label=file.split("/")[-1].split("_")[-1].split(".")[0],alpha=0.5,c=c[i],zorder=3)

    #plt.plot(tsticks["time"].values[t1:t2],tsticks["temperature"].values[t1:t2], label=file.split("/")[-1].split("_")[-1].split(".")[0],alpha=0.5,c=c[i],zorder=3)
    #tsticks.to_csv(inpath+"time_"+file.split("/")[-1][5:],sep=',',index=False,header = None)

plt.title("Time Constant",weight= "bold")    
plt.ylabel("Temperature [°C]")
plt.xlabel("time [ms]")
plt.xlim(160000,450000)
plt.ylim(0,25)
plt.legend(loc=5)
plt.grid()

