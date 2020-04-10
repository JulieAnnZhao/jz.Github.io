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
f_namefig1=f_name2[0]+'_profiler_1.png'
f_namefig2=f_name2[0]+'_profiler_2.png'
f_namefig3=f_name2[0]+'_profiler_3.png'
f_namefig4=f_name2[0]+'_profiler_4.png'
f_namefig5=f_name2[0]+'_profiler_5.png'
f_namefig6=f_name2[0]+'_profiler_6.png'

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



##upcast dpdt vs. pressure for single isopycnal

#adjust figure size
plt.rcParams["figure.figsize"] = (30,15)

pgrid=np.arange(np.round(presgd.max()),0,-0.5) # <- pressure grid
sgrid=np.arange(np.round(densgd.min()),np.round(densgd.max()),0.2) # <- density grid
dpdtgrid2d=np.zeros((len(pgrid),1))
dpdtgrids2d=np.zeros((len(sgrid),1))
datavg1d_d=np.zeros(1)

for pnum in range(1128,1130):   #2000,2034
#for pnum in range(1124,1127): 
    idx=np.argwhere(profnum1==pnum)  #extract date
    dtmp= np.squeeze(dategd[up1[idx]])
    ptmp = np.squeeze(presgd[up1[idx]])
    stmp = np.squeeze(densgd[up1[idx]])
    dpdtmp = np.squeeze(dp1[up1[idx]])
    
    if abs(ptmp.max()-ptmp.min())>50: 
        temp=smooth(dpdtmp,9)   #use smooth function instead of movMin
        
        datavg_d=np.expand_dims(np.mean(dtmp),axis=0)
        datavg1d_d=np.append(datavg1d_d,datavg_d,axis=0) 
        
        dpdtgrid=np.expand_dims(np.interp(pgrid,np.flip(ptmp),np.flip(temp),np.nan,np.nan),axis=1) # <- interp grid arrays must be increasing
        dpdtgrid2d=np.append(dpdtgrid2d,dpdtgrid,axis=1)   #
        
        dpdtgrids = np.expand_dims(np.interp(sgrid,np.flip(stmp),np.flip(temp),np.nan,np.nan),axis=1)
        dpdtgrids2d = np.append(dpdtgrids2d,dpdtgrids,axis=1)
        
        scatter6=plt.scatter(temp,ptmp,c='black')  #scatter plot after using smooth function
        plt.scatter(dpdtmp,ptmp,c='r')   #scatter plot without using smooth function
        plt.plot(dpdtgrid,pgrid,c='b')  #interpolate dots on regular grid
        plt.plot(temp,ptmp)    #linear interpolation
        
#label the graph
plt.title('Upcast dpdt Pressure plotting'+ " "+dm2+"-"+dn2,size=30)   #add start and end date into title
plt.ylabel('Upcast Pressure (dbar)',size=30)
plt.xlabel('upcast dpdt (dbar/s)',size=30)
ax1 = scatter6.axes    #invert axis
ax1.invert_yaxis()

plt.xticks(size = 25)
plt.yticks(size = 30)


#save figure
plt.savefig(f_namefig4, bbox_inches='tight')
plt.show()
