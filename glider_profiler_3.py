#load in glider dataset file
import datetime
import numpy as np
from netCDF4 import Dataset  
import matplotlib.pyplot as plt
import os
import matplotlib.dates as md
import numpy.ma as ma
import gsw as gsw
import cmocean
import cmocean.cm as cmo
import statistics
from statistics import mean 
import time

#define smooth function
def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth
    
    
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
f_namefig=f_name2[0]+'_profiler.png'


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

m2=datetime.datetime.fromtimestamp(x)   #convert start and end date timestamp into datetime format
n2=datetime.datetime.fromtimestamp(y) 
dm2=m2.strftime("%x")        #convert datetime format into string format
dn2=n2.strftime("%x") 




#use the smooth function
Psmooth = smooth(presgd[:,0],5)
dp1=0*Psmooth
# divide by "dt" to get something like speed
dp1[1:-1]=np.divide(Psmooth[1:-1]-Psmooth[0:-2],np.squeeze(dategd[1:-1]-dategd[0:-2])) 

#get all indices for upcast profilers
up1 = np.argwhere(dp1<0)

#get profnum1 array for all upcast profilers
profnum1 = [1]

t1 = time.time()
id=1
for kk in range(1,len(up1)):
    if up1[kk]-up1[kk-1]<2:
        profnum1.append(id)
    else:
        id = id+1
        profnum1.append(id)
        
 
t2 = time.time()
print('Elapsed  time: %f' %(t2-t1))

profnum1 = np.asarray(profnum1)



#define movMin function
def movMin(datas,k):
    result = np.empty_like(datas)
    start_pt = 0
    end_pt = int(np.ceil(k/2))

    for i in range(len(datas)):
        if i < int(np.ceil(k/2)):
            start_pt = 0
        if i > len(datas) - int(np.ceil(k/2)):
            end_pt = len(datas)
        result[i] = np.max(datas[start_pt:end_pt])
        start_pt += 1
        end_pt +=1
    return result
    
    
   
   
   #draw subplots
fig, axs = plt.subplots(2, 2,figsize=(25,15))
fig.subplots_adjust(left=0.5, bottom=0.5, right=1.5, top=1.5, wspace=0.5, hspace=0.5) #left<right, bottom>top


#1. date-pressure scatter plot color with upcast dpdt

#DATE1 array
date_up=np.squeeze(dategd[up1])
#get DATE array for time axis in subplot plottings
import datetime
DATE_up=[]
for row in date_up:
    DATE_up.append(datetime.datetime.fromtimestamp(row))  #convert unix timestamp into local datetime

#scatter plot
scatter2=axs[0,0].scatter(DATE_up,np.squeeze(presgd[up1]),c=np.squeeze(dp1[up1]),cmap=cmo.ice,vmin=-0.25,vmax=0.) 
cbar=fig.colorbar(scatter2,ax=axs[0,0])
cbar.set_label('dpdt (dbar/s)')


#flip pressure (y axis)
ax=axs[0, 0].axes
ax.invert_yaxis()
ax.set_xlim([datetime.date(start.year, start.month, start.day), datetime.date(end.year, end.month, end.day)])

axs[0, 0].set_title('Upcast dpdt Pressure plotting'+ " "+dm2+"-"+dn2)   #add start and end date into title
axs[0, 0].set_ylabel('Pressure (dbar)')
axs[0, 0].grid(True)
axs[0, 0].set_xlabel('Date')

plt.tight_layout(pad=1, w_pad=1, h_pad=2.0)


#2. upcast dpdt-pressure graph 
pgrid=np.arange(np.round(presgd.max()),0,-0.5)  #pressure grid
sgrid=np.arange(np.round(densgd.min()),np.round(densgd.max()),0.2) #density grid
tgrid=np.arange(np.round(tempgd.min()),np.round(tempgd.max()),0.2) # <- temperature grid
saligrid=np.arange(np.round(saligd.min()),np.round(saligd.max()),0.2) # <- salinity grid

dpdtgrid2d=np.zeros((len(pgrid),1))   #set 2-dimensional dpdt grid with all zeros 
dpdtgrids2d=np.zeros((len(sgrid),1))  #set 2-dimensional surface density with all zeros
datavg1d_d=np.zeros(1)                #set date average with zero

#get all date,pressure, density values at specific upcast indices using for loop
for pnum in range(1,profnum1.max()):   
    idx=np.argwhere(profnum1==pnum)   #extract date
    dtmp= np.squeeze(dategd[up1[idx]])
    ptmp = np.squeeze(presgd[up1[idx]])
    stmp = np.squeeze(densgd[up1[idx]])
    dpdtmp = np.squeeze(dp1[up1[idx]])
    if abs(ptmp.max()-ptmp.min())>50:
        temp=movMin(dpdtmp,9)
        datavg_d=np.expand_dims(np.mean(dtmp),axis=0) 
        datavg1d_d=np.append(datavg1d_d,datavg_d,axis=0) 
        dpdtgrid=np.expand_dims(np.interp(pgrid,np.flip(ptmp),np.flip(temp),np.nan,np.nan),axis=1) # interp grid arrays must be increasing
        dpdtgrid2d=np.append(dpdtgrid2d,dpdtgrid,axis=1)   
        dpdtgrids = np.expand_dims(np.interp(sgrid,np.flip(stmp),np.flip(temp),np.nan,np.nan),axis=1)
        dpdtgrids2d = np.append(dpdtgrids2d,dpdtgrids,axis=1)
        axs[0,1].scatter(temp,ptmp,c='r')
        axs[0,1].plot(dpdtgrid,pgrid,c='b')
        axs[0,1].plot(temp,ptmp)
#label the graph
axs[0,1].set_title('Upcast dpdt Pressure plotting'+ " "+dm2+"-"+dn2)   #add start and end date into title
axs[0,1].set_ylabel('Upcast Pressure (dbar)')
axs[0,1].set_xlabel('upcast dpdt (dbar/s)')


#3. dpdt on isopycnals
plt.rcParams["figure.figsize"] = (15,8)

dpdtgrid2d1=np.zeros((len(pgrid),1))
dpdtgrids2d1=np.zeros((len(sgrid),1))

datavg1d_d1=np.zeros(1)
for pnum1 in range(1,profnum1.max()):   
    idx1=np.argwhere(profnum1==pnum1)  #extract date
    dtmp1= np.squeeze(dategd[up1[idx1]])
    ptmp1= np.squeeze(presgd[up1[idx1]])
    stmp1 = np.squeeze(densgd[up1[idx1]])
    dpdtmp1 = np.squeeze(dp1[up1[idx1]])
    if abs(ptmp1.max()-ptmp1.min())>50: 
        temp1=movMin(dpdtmp1,9)
        datavg_d1=np.expand_dims(np.mean(dtmp1),axis=0) #,axis=0
        datavg1d_d1=np.append(datavg1d_d1,datavg_d1,axis=0) #,axis=0       #dpdtmp1
        dpdtgrid1=np.expand_dims(np.interp(pgrid,np.flip(ptmp1),np.flip(temp1),np.nan,np.nan),axis=1) # <- interp grid arrays must be increasing
        dpdtgrid2d1=np.append(dpdtgrid2d1,dpdtgrid1,axis=1)   #
        dpdtgrids1 = np.expand_dims(np.interp(sgrid,np.flip(stmp1),np.flip(temp1),np.nan,np.nan),axis=1)
        dpdtgrids2d1 = np.append(dpdtgrids2d1,dpdtgrids1,axis=1)

dpdtgrids2d_anom = 0.*dpdtgrids2d1
for ii in range(1,len(sgrid)):
    dpdtgrids2d_anom[ii,:] = dpdtgrids2d1[ii,:]-np.nanmean(dpdtgrids2d1[ii,:])
    

#DATE2 array
date_up=np.squeeze(dategd[up1])

DATE2=[]
for row in datavg1d_d1[1:-1]:
    DATE2.append(datetime.datetime.fromtimestamp(row))   #convert unix timestamp into local datetime
    

pc=axs[1,0].pcolor(DATE2,sgrid,dpdtgrids2d_anom[:,1:-1],vmin=-0.1,vmax=0.1) 
cbar=fig.colorbar(pc,ax=axs[1,0])
cbar.set_label('dpdt (dbar/s)')



#label the graph
axs[1,0].set_title('dpdt on isopycnals'+ " "+dm2+"-"+dn2)
axs[1,0].set_xlabel('Date')
axs[1,0].set_ylabel('Surface Density (g/cm^3)')

#4. dpdt value of specific isopycnal compared with mean dpdt
axs[1,1].plot(DATE2,dpdtgrids2d_anom[25,1:-1])

dpdts = np.nanmean(dpdtgrids2d_anom,axis=0)
axs[1,1].plot(DATE2,dpdts[1:-1]) 

#label the graph
axs[1,1].set_title('dpdt at specific isopycnal & mean dpdt'+ " "+dm2+"-"+dn2)
axs[1,1].set_xlabel('Date')
axs[1,1].set_ylabel('dpdt (dbar/s)')
