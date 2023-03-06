# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 17:07:43 2023

@author: Quentin Rauschenbach
"""

#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import matplotlib

import datetime

inpath = "C:/Users/qraus/Documents/Uni/9_22-23WiSe/Measurement Electronics/Temperature_Logger/data/adjusted/"


#%%

files = glob.glob(inpath +"*")
variable = "temperature"
print(files)

df1 = pd.read_csv(files[-1], sep=',', comment='#',names=["time","millis","ID","temperature"])
df_spot1 = df1[["time",variable]]
df_spot1 = df_spot1.rename(columns={variable: "Labor"})
df_spot1["time"] = pd.to_datetime(df1["time"], utc=True).dt.tz_localize(None)
df1 = df_spot1.copy()

for count, file in enumerate(files[:-1]):
    name = file.split("/")[-1].split("_")[-1].split(".")[0]
    print(name)
    df2 = pd.read_csv(file, sep=',', comment='#',names=["time","millis","ID","temperature"])
    df2 = df2[["time",variable]]
    print(df2.time.values[0])
    df2 = df2.rename(columns={variable: name})
    df2["time"] = pd.to_datetime(df2["time"], utc=True).dt.tz_localize(None)
    df_spot1 = pd.merge_ordered(df_spot1, df2)#, fill_method="ffill", left_by="group")
    
df_spot1["time"] = pd.to_datetime(df_spot1["time"], utc=True).dt.tz_localize(None)
df_spot1.set_index(['time'], inplace = True)

df_spot1 = df_spot1.interpolate(method = "time")
df_spot1 = df_spot1.reindex(df1.time)

sensor_list = df_spot1.columns.values.tolist()[:]

#%%

plt.figure(figsize = (7.5,6))

for sensor in sensor_list[1:]:
    plt.plot(df_spot1.index.values,df_spot1[sensor].values,label = sensor, alpha = 0.5,linestyle = "--")
plt.plot(df_spot1.index.values,df_spot1[sensor_list[0]].values,label = sensor_list[0])
plt.legend()

#%%
plt.figure(figsize = (7.5,6))
for sensor in sensor_list[1:]:
    plt.plot(df_spot1[sensor_list[0]].values,df_spot1[sensor].values,label = sensor, alpha = 0.5,linestyle = "--")
    
plt.plot(df_spot1[sensor_list[0]].values,df_spot1[sensor_list[0]].values,label = sensor_list[0])   
plt.xlabel("Labor") 
plt.legend()
    