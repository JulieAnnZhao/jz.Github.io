#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 15:10:01 2020

@author: yanzhao
"""
import datetime #as dt  
import numpy as np
from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/
import matplotlib.pyplot as plt
import os
import matplotlib.dates as md

nc_f = '/Users/yanzhao/Downloads/otn200_20160405_60_delayed_78fb_eab6_050a.nc'
nc_fid = Dataset(nc_f, 'r')

date = nc_fid.variables['time'][:] #x axis
lats = nc_fid.variables['latitude'][:] 
lons = nc_fid.variables['longitude'][:] 
temp = nc_fid.variables['temperature'][:]
sali = nc_fid.variables['salinity'][:]
dens = nc_fid.variables['density'][:]
depth = nc_fid.variables['depth'][:]  #y axis


# Make plot
#1. date-pres-temp plotting
goods=np.argwhere(temp.filled()>-5)
tempgd=temp[goods]
dategd=date[goods]
presgd=pres[goods]

DATE=[]
for row in dategd:
    DATE.append(datetime.datetime.fromtimestamp(row))  #convert unix timestamp into local datetime

scatter = plt.scatter(DATE,presgd,c=tempgd)
ax1 = scatter.axes
ax1.invert_yaxis()   #flip pressure
plt.ylim((-0.5,max(presgd)+5))
ax1.set_ylim(ax1.get_ylim()[::-1]) 
ax1.set_xlim([datetime.date(2016, 4, 1), datetime.date(2016, 5, 5)]) #fix the date range
cbar = plt.colorbar(orientation='horizontal', extend='both')  #specify mappable object
#plt.clim(2,12)
xfmt = md.DateFormatter('%Hh\n%dd\n%b')  #formatter, set the display format of time
ax1.xaxis.set_major_formatter(xfmt)   #set formatter of major ticker
cbar.ax.set_xlabel('Temperature ($^\circ$C)')
plt.title('Glider transect')  #label the plotting
plt.ylabel('Pressure (dbar)')
plt.xlabel('Temperature')

#2. date-salinity-temp plotting
saligd=sali[goods]


scatter=plt.scatter(DATE,presgd,c=saligd)
ax1 = scatter.axes
ax1.invert_yaxis()   
plt.ylim((-5,max(presgd)+5))
ax1.set_xlim([datetime.date(2016, 4, 1), datetime.date(2016, 5, 5)])
ax1.set_ylim(ax1.get_ylim()[::-1]) 
cbar = plt.colorbar(orientation='horizontal', extend='both')  #specify mappable object
#cbar = plt.colorbar.ColorbarBase(ax1, cmap=cm,norm=plt.colors.Normalize(vmin=20, vmax=35))
#cbar.set_clim(20, 35)
# bounds=[20,25,30,35,40]
plt.clim(28,36)  #adjust colorbar range
xfmt = md.DateFormatter('%Hh\n%dd\n%b')  #formatter, set the display format of time
ax1.xaxis.set_major_formatter(xfmt)   #set formatter of major ticker
cbar.ax.set_xlabel('Salinity (psu)')
plt.title('Glider transect')  #label the plotting
plt.ylabel('Pressure (dbar)')
plt.xlabel('Salinity')


#3. date-density-temp plotting
densgd=dens[goods]

scatter = plt.scatter(DATE,presgd,c=densgd)
ax1 = scatter.axes
ax1.invert_yaxis()   
plt.ylim((-0.5,max(presgd)+5))
ax1.set_ylim(ax1.get_ylim()[::-1]) 
ax1.set_xlim([datetime.date(2016, 4, 1), datetime.date(2016, 5, 5)])
cbar = plt.colorbar(orientation='horizontal', extend='both')  #specify mappable object
plt.clim(1024,1029)   #adjust colorbar range
xfmt = md.DateFormatter('%Hh\n%dd\n%b')  #formatter, set the display format of time
ax1.xaxis.set_major_formatter(xfmt)   #set formatter of major ticker
cbar.ax.set_xlabel('Density (kg m$^{-3}$)')
plt.title('Glider transect')  #label the plotting
plt.ylabel('Pressure (dbar)')
plt.xlabel('Density')

#new figure for latitude and longitude
latsgd=lats[goods]
lonsgd=lons[goods]
scatter=plt.scatter(lonsgd,latsgd,c=tempgd)
ax1 = scatter.axes
ax1.invert_yaxis()   
cbar = plt.colorbar(orientation='horizontal', extend='both')  #specify mappable object
plt.clim(-0.66,6)
xfmt = md.DateFormatter('%Hh\n%dd\n%b')          
cbar.ax.set_xlabel('Temperature ($^\circ$C)')
plt.title('longitude-latitute plotting')  #label the plotting
plt.ylabel('Latitute (degrees_north)')
plt.xlabel('Longitude (degrees_east)')

x=dategd.min()
xind=np.argwhere(dategd==x)
latsmin=latsgd[xind]
lonsmin=lonsgd[xind]
colorsx=["red"]
plt.scatter(lonsmin,latsmin,color=colorsx) #plot start point in red dot

y=dategd.max()
yind=np.argwhere(dategd==y)
latsmax=latsgd[yind]
lonsmax=lonsgd[yind]
colorsy=["black"]
plt.scatter(lonsmax,latsmax,color=colorsy,marker='+')  #plot end point in black +

#get surface data plotting
np1=np.diff(latsgd,axis=0)
np2=np.diff(lonsgd,axis=0)
ind=np.argwhere(presgd<1) #function to get data index from specific range 

scatter=plt.scatter(lonsgd[ind],latsgd[ind],c=tempgd[ind]) 
ax1 = scatter.axes
ax1.invert_yaxis()   
cbar = plt.colorbar(orientation='horizontal', extend='both')  #specify mappable object
xfmt = md.DateFormatter('%Hh\n%dd\n%b')          
cbar.ax.set_xlabel('Temperature ($^\circ$C)')
plt.title('longitude-latitute plotting')  #label the plotting
plt.ylabel('Latitute (degrees_north)')
plt.xlabel('Longitude (degrees_east)')













