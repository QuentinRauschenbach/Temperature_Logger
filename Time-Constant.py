# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 09:48:21 2023

@author: Quentin Rauschenbach
"""

#%% Libaries & Functions
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
from pandas.tseries.offsets import DateOffset

def create_time_axis(df):
    print("----- Creating time axis -----")
    df["time"] = df["time"]+DateOffset(years=23,months=2,days=1,hours=15,minutes=48)

    for i in range(len(df["time"].values)):
        df["time"][i] = df["time"][i]+DateOffset(seconds=df["millis"].values[i]/1000)
        
    df.to_csv(inpath+"test.LOG",sep=',',index=False)
    return df


def calibrate(temp,fit_parameter,calibration=True,debug = []):
    if "temp" in debug:
        print("Temp[0] BEFORE calibration:",temp.values[0:2])  
    if calibration:
        temp = temp - (fit_parameter[0]*temp**2 + fit_parameter[1]*temp+fit_parameter[2])
        if "temp" in debug:
            print("Temp[0] AFTER  calibration:",temp.values[0:2])
            
    return temp

#%%
debug = ["time"]
calibration = True

inpath = "C:/Users/qraus/Documents/Uni/9_22-23WiSe/Measurement Electronics/Temperature_Logger/data/"
fit_parameter = {'DF': [ 0.00171593, -0.04987637,  0.88662819], 'DKB': [ 0.00119211, -0.02983068,  0.14389312], 'KiS': [ 0.00036888, -0.01093385,  0.09981709], 'KM': [ 0.00219469, -0.06951533,  0.46263249], 'KS': [ 1.47361701e-03, -6.23715667e-02,  1.58281494e+00], 'LG': [ 0.00158846, -0.05031084,  0.58245583], 'QR': [ 0.00140693, -0.04060876,  0.44311093], 'SimonS': [ 0.00075733, -0.02163417,  0.08605323]}

#%% Load calibration file

calibration_file = pd.read_csv(inpath +"c_tsensor_calibration_time_constant_new.log", 
                      sep=',', comment='#', header=None, names=['time', 'temperature'])
calibration_file["time"] = pd.to_datetime(calibration_file["time"], utc=True).dt.tz_localize(None)

#%%
start_index = 160 # start index of "shock" experiment
end_index   = 500 # end index "shock" experiment

t_const = 0.1 #°C below which diff we consinder Temp as const
av_const = 30 #s averaging period


c = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
files = glob.glob(inpath +"TSENSOR*.log")

plt.figure(figsize = (16,8))

for i, file in enumerate(files[:]):
    sensor = file.split("/")[-1].split("_")[-1].split(".")[0]
    print(sensor)
    
    tsensors = pd.read_csv(file, sep=',', comment='#', header=None,
                          names=['time', 'millis', 'ID', 'temperature'])
    
    # temperature calibration
    tsensors['temperature'] = calibrate(tsensors['temperature'],fit_parameter[sensor],calibration,debug)
    
    # convert date into datetime-format
    tsensors["time"] = pd.to_datetime(tsensors["time"], utc=True).dt.tz_localize(None)
    
    # Creating time axis for the ones without a functioning RTC
    if sensor in ["LG", "KM"]:
        tsensors = create_time_axis(tsensors)
    
    # fill in blank values with NaNs
    tsensors = tsensors.replace(r'^\s*$', np.nan, regex=True)

    # get "shock" time
    diff        = abs(tsensors["temperature"].values[1:] - tsensors["temperature"].values[:-1]) # change in temperature  between timesteps   
    shock_index = start_index + np.where(diff[start_index:end_index] >= t_const)[0][0]       # find index of "shock"
    shock_time  = tsensors['millis'][shock_index]
    Temp_start  = np.nanmean(tsensors['temperature'][shock_index-30:shock_index])         # average over 30 values
    
    # adjust time axis
    offset = tsensors["time"][shock_index] - calibration_file["time"][2]
    if "time" in debug:
        print("shock old:",tsensors["time"][shock_index])
        print("Offset   :",offset)
    tsensors["time"] = tsensors["time"] - offset
    if "time" in debug:
        print("shock new:",tsensors["time"][shock_index])
    
    # get final temp
    av_diff = np.zeros(len(diff))
    N = 120 # average over N values
    for k in range(len(diff)-N):
        av_diff[k + N] = np.nanmean(diff[k : k + N])
    stable_index = shock_index + 50 + np.where(abs(av_diff[shock_index+50:]) <= t_const)[0][0]
    end_time     = tsensors['millis'][stable_index]
    Temp_end     = np.nanmean(tsensors['temperature'][stable_index:stable_index+30]) # average over 30 values
    
    
    # time const
    Temp_tau = Temp_end +1/np.e *(Temp_start-Temp_end)
    diff_temp = abs(tsensors['temperature'].values[:end_index]-Temp_tau)
    time_tau = tsensors['millis'][np.where(diff_temp == np.nanmin(diff_temp))[0][0]]
    print("Time constant: ",time_tau)
    print("")
        
    # plot  
    #plt.hlines(Temp_start,0,600000,zorder=0,linestyle="--",color=c[i])
    plt.hlines(Temp_end,0,600000,zorder=0,linestyle="--",color=c[i])
    
    plt.scatter(shock_time,tsensors["temperature"].values[shock_index],marker="x",c=c[i],zorder=1)
    plt.scatter(end_time,Temp_end,marker="o",c=c[i],zorder=2)
    plt.scatter(time_tau,Temp_tau,marker="o",c=c[i],zorder=4)
    
    plt.plot(tsensors["millis"].values[start_index:end_index],tsensors["temperature"].values[start_index:end_index], label=file.split("/")[-1].split("_")[-1].split(".")[0],alpha=0.5,c=c[i],zorder=3)
    #plt.plot(tsensors["time"].values[start_index:end_index],tsensors["temperature"].values[start_index:end_index], label=file.split("/")[-1].split("_")[-1].split(".")[0],alpha=0.5,c=c[i],zorder=3)
    
    #tsensors.to_csv(inpath+"time_"+file.split("/")[-1][5:],sep=',',index=False,header = None)

plt.title("Time Constant",weight= "bold")    
plt.ylabel("Temperature [°C]")
plt.xlabel("time [ms]")
plt.xlim(230000,300000)
plt.ylim(0,25)
plt.legend(loc=5)
plt.grid()

