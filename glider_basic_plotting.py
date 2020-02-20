#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 15:10:01 2020

@author: yanzhao
"""
import datetime
import numpy as np
from netCDF4 import Dataset  
import matplotlib.pyplot as plt
import os
import matplotlib.dates as md
import numpy.ma as ma
import gsw as gsw
from matplotlib import cm

#load in contour map dataset file
f_root='/Users/yanzhao/Downloads/'
f_name='etopo1_bedrock.nc'    
nc_f=f_root+f_name
nc_fid = Dataset(nc_f, 'r')   

#load in contour dataset variables
lat = nc_fid.variables['lat'][:]            
lon = nc_fid.variables['lon'][:] 
band= nc_fid.variables['Band1'][:]

##########################################
#4. otn200_20110726_4_delayed_78fb_eab6_050a.nc
##########################################



#load in glider dataset file
f_root1='/Users/yanzhao/Downloads/'
f_name1='otn200_20110726_4_delayed_78fb_eab6_050a.nc'  
nc_f1=f_root1+f_name1
nc_fid1 = Dataset(nc_f1, 'r')    

#remove .nc with .png for fig
f_name2=f_name1.split('.')
f_namefig=f_name2[0]+'.png'


#accessing glider dataset variables
date = nc_fid1.variables['time'][:] 
lats = nc_fid1.variables['latitude'][:]            
lons = nc_fid1.variables['longitude'][:] 
temp = nc_fid1.variables['temperature'][:]
sali = nc_fid1.variables['salinity'][:]
dens = nc_fid1.variables['density'][:] 
depth = nc_fid1.variables['depth'][:]  
pres = nc_fid1.variables['pressure'][:]
dens = nc_fid1.variables['density'][:]
#only use the data that have temperature>-5 
goods=np.argwhere((temp.filled()>-5)&(sali.filled()>0))
latsgd=lats[goods]
lonsgd=lons[goods]
tempgd=temp[goods]
dategd=date[goods]
presgd=pres[goods]
depthgd=depth[goods]
saligd=sali[goods]
presgd=pres[goods]
densgd=dens[goods]
#get the start and end date 
x=dategd.min()
y=dategd.max()
from datetime import datetime
start = datetime.fromtimestamp(x)
end = datetime.fromtimestamp(y)

#get DATE array for time axis in subplot plottings
import datetime
DATE=[]
for row in dategd:
    DATE.append(datetime.datetime.fromtimestamp(row))  #convert unix timestamp into local datetime



#draw subplots
fig, axs = plt.subplots(2, 2,figsize=(12,8))
fig.subplots_adjust(left=0.5, bottom=0.5, right=1.5, top=1.5, wspace=0.5, hspace=0.5) #left<right, bottom>top

#1. axs[0,0] plot: contour map with latitude and longitude info on it

#draw contour lines with specific levels in grey, label level lines properly
scatter=axs[0,0].contour(lon, lat, band, levels=[-4000,-3000,-2000,-1000,-500,-200,-100,0],linewidths=1,colors=('grey'),zorder=0) 
axs[0,0].clabel(scatter, fontsize=10, inline=1,fmt='%1.0f')

#draw contour line with levels=0 in black, label properly
scatter=axs[0,0].contour(lon, lat, band, levels=[0],linewidths=2,colors=('black'),zorder=0)
axs[0,0].clabel(scatter, fontsize=10, inline=1,fmt='%1.0f')  

#add lonsgd,latsgd map to contour map

#get surface data plotting
np1=np.diff(latsgd,axis=0)
np2=np.diff(lonsgd,axis=0)
surf=np.argwhere(presgd>0) #get data index from specific range 

#draw scatter plot
scatter=axs[0,0].scatter(lonsgd[surf],latsgd[surf],c=tempgd[surf],zorder=5)  
ax1 = scatter.axes
cbar=fig.colorbar(scatter,ax=axs[0,0])    #set colorbar 
cbar.set_label('Temperature ($^\circ$C)')

#add xlim
axs[0,0].set_xlim(-67.5,-58)

#plot start point in red dot
xind=np.argwhere(dategd==x)
latsmin=latsgd[xind[0,0]]
lonsmin=lonsgd[xind[0,0]]
colorsx=["red"]
axs[0,0].scatter(lonsmin,latsmin,color=colorsx,zorder=5) 

#plot end point in black plus sign
yind=np.argwhere(dategd==y)
latsmax=latsgd[yind[0,0]]
lonsmax=lonsgd[yind[0,0]]
colorsy=["black"]
axs[0,0].scatter(lonsmax,latsmax,color=colorsy,marker='+',zorder=5)  

#label date in axs[0,0] subplot title
m2=datetime.datetime.fromtimestamp(x)   #convert start and end date timestamp into datetime format
n2=datetime.datetime.fromtimestamp(y) 
dm2=m2.strftime("%x")        #convert datetime format into string format
dn2=n2.strftime("%x")    
axs[0,0].set_title('Longitude-Latitute Plotting at Surface Temp'+ " "+dm2+"-"+dn2)  #add start and end date into title
axs[0,0].set_ylabel('Latitute (degrees_north)')
axs[0,0].set_xlabel('Longitude (degrees_east)')


#2. axs[0,1] plot: date-pres plotting with temperature colorbar
scatter2=axs[0, 1].scatter(DATE,presgd,c=tempgd)  #draw scatter plot
ax1 = axs[0, 1].axes
#flip pressure (y axis)
ax1.invert_yaxis()   

#draw internal wave lines
sa=gsw.SA_from_SP(saligd,presgd,-64,44)
ct=gsw.CT_from_t(sa,tempgd,presgd)
sig=gsw.sigma0(sa,ct)
ind=np.argwhere((sig.filled()>25.99)&(sig.filled()<26.01))
ind1=np.delete(ind,1,1)
dateind1=dategd[ind1]       
presind1=presgd[ind1]

#get the new DATE1 based on DATE
import datetime
DATE1=[]
for row in dateind1:
    DATE1.append(datetime.datetime.fromtimestamp(row))  #convert unix timestamp into local datetime

axs[0,1].scatter(DATE1,presind1,c='black',s=1)

#fix pressure (y axis) range based on real condition
plt.ylim((-0.5,max(presgd)+5))   

#fix the date (x axis) range based on real glider target start and end date
ax1.set_xlim([datetime.date(start.year, start.month, start.day), datetime.date(end.year, end.month, end.day)]) 

#set and label colorbar
cbar=fig.colorbar(scatter2,ax=axs[0,1])
cbar.set_label('Temperature ($^\circ$C)')

#set formatter of major ticker for the display format in date-month
xfmt = md.DateFormatter('%dd\n%b')  
ax1.xaxis.set_major_formatter(xfmt)

#add title and set xlabel, ylabel
axs[0, 1].set_title('Pressure plotting'+ " "+dm2+"-"+dn2)   #add start and end date into title
axs[0,1].set_ylabel('Pressure (dbar)')
axs[0,1].set_xlabel('Date')
#3. axs[1,0]: date-pres plotting with salinity colorbar

#draw the scatter plot of date-presgd
scatter3=axs[1,0].scatter(DATE,presgd,c=saligd,vmin=28,vmax=36)  #rearrange the colorbar into appropriate range
ax3 = axs[1,0].axes

#flip pressure (y axis)
ax3.invert_yaxis()    

#fix presgd(y axis) range based on real condition
plt.ylim((-5,max(presgd)+5))

#fix the date (x axis) range based on real glider target start and end date
ax3.set_xlim([datetime.date(start.year, start.month, start.day), datetime.date(end.year, end.month, end.day)]) #fix the date range

#set and label colorbar
cbar=fig.colorbar(scatter3,ax=axs[1,0])
cbar.set_label('Salinity (psu)')

#set formatter of major ticker for the display format in date-month
xfmt = md.DateFormatter('%dd\n%b')  
ax3.xaxis.set_major_formatter(xfmt)  

#add plot title, xlabel and ylabel
axs[1,0].set_title('Salinity Plotting'+ " "+dm2+"-"+dn2)  
axs[1,0].set_ylabel('Pressure (dbar)')
axs[1,0].set_xlabel('Date')

#4. axs[1,1]: Salinity-temperature plot

#build up 2D arrays for temperature and salinity grid
tgrid=np.linspace(0,20,100)
sgrid=np.linspace(30,37,101)

#draw sigma contour lines
sg,tg=np.meshgrid(sgrid,tgrid)
sig=gsw.sigma0(sg,tg)
scatter4=axs[1,1].contour(sgrid,tgrid,sig,zorder=0,colors=('grey'))
axs[1,1].clabel(scatter4, fontsize=10, inline=1,fmt='%1.0f')   

#draw absolute salinity and conservative temperature scatter plot on top of sigma contour lines
sa=gsw.SA_from_SP(saligd,presgd,-64,44)
ct=gsw.CT_from_t(sa,tempgd,presgd)
scatter4=axs[1, 1].scatter(sa,ct,c=presgd,zorder=5)  

#add and label colorbar
cbar=fig.colorbar(scatter4,ax=axs[1,1])
cbar.set_label('Pressure (dbar)')

#fix the range of x and y axis
ax4 = scatter4.axes
ax4.set_xlim(30,37)
ax4.set_ylim(saligd.min(),20)

#add title, xlabel and ylabel
plt.xlabel('Absolute Salinity (g/kg)')    
plt.ylabel('Conservative Temperature ($^\circ$C)')
axs[1, 1].set_title('AS-CT Plotting'+ " "+dm2+"-"+dn2)

#save figure
plt.savefig(f_namefig, bbox_inches='tight')
plt.show()






#######################################
# dpdt graph
#######################################

#split x into two parts, >0 and <0
dpdt=0*presgd
dpdt[2:(len(presgd)-2)]=(presgd[3:(len(presgd)-1)]-presgd[1:(len(presgd)-3)])/(dategd[3:(len(dategd)-1)]-dategd[1:(len(dategd)-3)])
x=dpdt[2:(len(presgd)-2)]
xind1=np.argwhere(x>0)
xind2=np.argwhere(x<0)
dpdt1=x[xind1]
dens1=densgd[xind1]
dpdt2=x[xind2]
dens2=densgd[xind2]
plt.scatter(dens1,dpdt1)  #dpdt>0, downcast
plt.scatter(dens2,dpdt2)  #dpdt<0, upcast






