# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 09:48:21 2023

@author: Quentin Rauschenbach

UHH WiSe 2022/2023
Practical Measurement Electronics and Interfaces in Ocean Sciences

Calibrate time axis and calculate time constants.


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


def calibrate(temp, fit_parameter, calibration=True, debug = []):
    if "temp" in debug:
        print("Temp[0] BEFORE calibration:",temp.values[0:2])  
    if calibration:
        temp = temp - (fit_parameter[0]*temp**2 + fit_parameter[1]*temp+fit_parameter[2])
        if "temp" in debug:
            print("Temp[0] AFTER  calibration:",temp.values[0:2])
            
    return temp

def adjust_time_axis(time_axis, shock_index, reference_shock_time, debug = []):
    offset = time_axis[shock_index] - reference_shock_time
    if "time" in debug:
        print("shock old:",time_axis[shock_index])
        print("Offset   :",offset)
    time_axis = time_axis - offset
    if "time" in debug:
        print("shock new:",time_axis[shock_index])

#%%
debug = [""]
calibration = True

start_index = 160 # start index of "shock" experiment
end_index   = 500 # end index "shock" experiment

t_const = 0.1 # °C below which diff we consinder Temp as const
av_const = 30 # number of values to average

plotpath = "C:/Users/qraus/Documents/Uni/9_22-23WiSe/Measurement Electronics/Temperature_Logger/pictures/"
inpath = "C:/Users/qraus/Documents/Uni/9_22-23WiSe/Measurement Electronics/Temperature_Logger/data/"

# by hand from Calibration.py
fit_parameter = {'DF': [ 0.00171593, -0.04987637,  0.88662819], 'DKB': [ 0.00119211, -0.02983068,  0.14389312], 'KiS': [ 0.00036888, -0.01093385,  0.09981709], 'KM': [ 0.00219469, -0.06951533,  0.46263249], 'KS': [ 1.47361701e-03, -6.23715667e-02,  1.58281494e+00], 'LG': [ 0.00158846, -0.05031084,  0.58245583], 'QR': [ 0.00140693, -0.04060876,  0.44311093], 'SimonS': [ 0.00075733, -0.02163417,  0.08605323]}

#%% Load calibration file

calibration_file = pd.read_csv(inpath +"c_tsensor_calibration_time_constant_new.log", 
                      sep=',', comment='#', header=None, names=['time', 'temperature'])
calibration_file["time"] = pd.to_datetime(calibration_file["time"], utc=True).dt.tz_localize(None)

#%%
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
files  = glob.glob(inpath +"TSENSOR*.log")
#files = glob.glob(inpath +"adjusted/time*.log")

plt.figure(figsize = (10,4))

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
    shock_index = start_index + np.where(diff[start_index:end_index] >= t_const)[0][0]          # find index of "shock"
    shock_time  = tsensors['millis'][shock_index]
    Temp_start  = np.nanmean(tsensors['temperature'][shock_index-av_const:shock_index])        
    
    # correct time offset to reference sensor
    adjust_time_axis(tsensors["time"], shock_index, calibration_file["time"][2], debug)
    
    # get final temp
    av_diff = np.zeros(len(diff))
    N = 100 # average over N values
    for k in range(len(diff)-N):
        av_diff[k + N] = np.nanmean(diff[k : k + N])
    # where Temperature is stable over N values for the first time after shock
    stable_index = shock_index + 50 + np.where(abs(av_diff[shock_index+50:]) <= t_const)[0][0]
    end_time     = tsensors['millis'][stable_index]
    Temp_end     = np.nanmean(tsensors['temperature'][stable_index:stable_index+av_const])
    
    # time const
    Temp_tau = Temp_end +1/np.e *(Temp_start-Temp_end)
    diff_temp = abs(tsensors['temperature'].values[:end_index]-Temp_tau)
    time_tau = tsensors['millis'][np.where(diff_temp == np.nanmin(diff_temp))[0][0]]
    print(Temp_end)
    print(Temp_start)
    print("Time constant: ",time_tau)
    print("")
        
    # plot  
    #plt.hlines(Temp_start,0,600000,zorder=0,linestyle="--",color=colors[i])
    #plt.hlines(Temp_end,0,600000,zorder=0,linestyle="--",color=colors[i])
    
    plt.scatter(shock_time/1000,tsensors["temperature"].values[shock_index],marker="x",c=colors[i],zorder=1, s=100)
    plt.scatter(end_time/1000,Temp_end,marker="x",c=colors[i],zorder=2,s=100)
    plt.scatter(time_tau/1000,tsensors["temperature"].values[np.where(diff_temp == np.nanmin(diff_temp))[0][0]],marker="o",c=colors[i],zorder=4)
    
    plt.plot(tsensors["millis"].values[start_index:end_index]/1000,tsensors["temperature"].values[start_index:end_index], label=file.split("/")[-1].split("_")[-1].split(".")[0],alpha=1,c=colors[i],zorder=3)
    #plt.plot(tsensors["time"].values[start_index:end_index],tsensors["temperature"].values[start_index:end_index], label=file.split("/")[-1].split("_")[-1].split(".")[0],alpha=0.5,c=colors[i],zorder=3)
    

    # save temperature and time calibrated data in new folder
    # tsensors.to_csv(inpath+"time_"+file.split("/")[-1][5:],sep=',',index=False,header = None)

plt.scatter(np.nan,np.nan,marker="o",c="black", label = r"T$_\tau$")
plt.scatter(np.nan,np.nan,marker="x",c="black", label = "start/end")
plt.title("Time Constant",weight= "bold")    
plt.ylabel("Temperature [°C]")
plt.xlabel("time [s]")
plt.xlim(238,380)
plt.ylim(0,25)
plt.legend(loc=5)
plt.grid()

#plt.savefig(plotpath + "time-const.png", dpi = 300, bbox_inches='tight')
plt.savefig(plotpath + "time-const.pdf", bbox_inches='tight')

