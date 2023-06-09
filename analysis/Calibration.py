# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 17:07:43 2023

@author: Quentin Rauschenbach

UHH WiSe 2022/2023
Practical Measurement Electronics and Interfaces in Ocean Sciences

Find Calibration parameters for all sensors by performing 2. degree polynomial fit.
"""

#%% Load Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import matplotlib

import datetime

inpath = "C:/Users/qraus/Documents/Uni/9_22-23WiSe/Measurement Electronics/Temperature_Logger/data/adjusted/"
plotpath = "C:/Users/qraus/Documents/Uni/9_22-23WiSe/Measurement Electronics/Temperature_Logger/pictures/"
c = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

#%% Create dataframe reduced to ref sensor

files = glob.glob(inpath +"*")
variable = "temperature"
print(files)

df1 = pd.read_csv(files[-1], sep=',', comment='#',names=["time","millis","ID","temperature"])
df = df1[["time",variable]]
df = df.rename(columns={variable: "Labor"})
df["time"] = pd.to_datetime(df1["time"], utc=True).dt.tz_localize(None)
df1 = df.copy()

for count, file in enumerate(files[:-1]):
    name = file.split("/")[-1].split("_")[-1].split(".")[0]
    print(name)
    df2 = pd.read_csv(file, sep=',', comment='#',names=["time","millis","ID","temperature"])
    df2 = df2[["time",variable]]
    df2 = df2.rename(columns={variable: name})
    df2["time"] = pd.to_datetime(df2["time"], utc=True).dt.tz_localize(None)
    df = pd.merge_ordered(df, df2)#, fill_method="ffill", left_by="group")
    
df["time"] = pd.to_datetime(df["time"], utc=True).dt.tz_localize(None)
df.set_index(['time'], inplace = True)

df = df.interpolate(method = "time")
df = df.reindex(df1.time)

sensor_list = df.columns.values.tolist()[:]

#%% find calibration & quick plot
plt.figure(figsize = (7.5,6))
fity = np.zeros((len(sensor_list[1:]),len(df[sensor_list[0]])))
fit_parameter = {}

for i, sensor in enumerate(sensor_list[1:]):
    fit_parameter[sensor] = np.polyfit(df[sensor_list[0]].values, df[sensor].values-df[sensor_list[0]].values, 2)
    fity[i] = fit_parameter[sensor][2]+fit_parameter[sensor][1]*df[sensor_list[0]]+fit_parameter[sensor][0]*df[sensor_list[0]]**2
    plt.plot(df[sensor_list[0]],fity[i])
    #plt.plot(df[sensor_list[0]].values,df[sensor].values,label = sensor, alpha = 0.5,linestyle = "--")
    plt.plot(df[sensor_list[0]].values,df[sensor].values-df[sensor_list[0]].values,label = sensor, alpha = 1,linestyle = "--",c=c[i])
#plt.plot(df[sensor_list[0]].values,df[sensor_list[0]].values,label = sensor_list[0])   
plt.xlabel("Sensor - Labor") 
plt.xlabel("Labor") 
plt.suptitle("Temperature Calibration")
plt.legend()

#%% plot

fig, axs = plt.subplots(1, 1, tight_layout = True ,figsize = (6,5))
plt.suptitle("Temperature Calibration", fontsize=16, fontweight= "bold")


axs.set_xlabel('Temperature Reference Sensor [°C]')
#axs.set_title('Difference Between DS18B20 Sensors and Reference Sensor')
axs.set_title(r'$\Delta$T of DS18B20 Sensors - Greisinger')
axs.set_ylabel('Temperature Difference [°C]')
axs.plot(np.nan,np.nan,label = "fit", color = "black")
axs.plot(np.nan,np.nan,label = "data", color = "black",linestyle = "--")

fity = np.zeros((len(sensor_list[1:]),len(df[sensor_list[0]])))
fit_parameter = {}

for i, sensor in enumerate(sensor_list[1:]):
    fit_parameter[sensor] = np.polyfit(df[sensor_list[0]].values, df[sensor].values-df[sensor_list[0]].values, 2)
    fity[i] = fit_parameter[sensor][2]+fit_parameter[sensor][1]*df[sensor_list[0]]+fit_parameter[sensor][0]*df[sensor_list[0]]**2
    
    axs.plot(df[sensor_list[0]],fity[i],label = sensor)
    axs.plot(df[sensor_list[0]].values,df[sensor].values-df[sensor_list[0]].values,linestyle = "--",c=c[i])

axs.legend(bbox_to_anchor=(1, 0.8))
#plt.savefig(plotpath + "Calibration.png", dpi = 300, bbox_inches='tight')
plt.savefig(plotpath + "Calibration.pdf", bbox_inches='tight')
plt.show()
