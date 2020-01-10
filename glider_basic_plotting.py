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

# add date object for plotting
DATE = []
for row in date:
    DATE.append(datetime.datetime.fromtimestamp(row))

# Make plot
fig, ax1 = plt.subplots(1) # a one graph contains all variables is needed
plt.scatter(date,depth, c=temp)#s=15,c=temp,marker='o', edgecolor='none') #plt.scatter(x, y, s=area, c=colors, alpha)
plt.ylim((-0.5,max(depth)+5))
ax1.set_ylim(ax1.get_ylim()[::-1]) 
cbar = plt.colorbar(orientation='horizontal', extend='both')  #specify mappable object
xfmt = md.DateFormatter('%Hh\n%dd\n%b')  #formatter, set the display format of time
ax1.xaxis.set_major_formatter(xfmt)   #set formatter of major ticker
cbar.ax.set_xlabel('Temperature ($^\circ$C)')
plt.title('Glider transect')  #label the plotting
plt.ylabel('Depth (m)')
plt.xlabel('Temperature')
plt.show()

# Save figure (without 'white' borders)
#plt.savefig('glider_basic.png', bbox_inches='tight')
















