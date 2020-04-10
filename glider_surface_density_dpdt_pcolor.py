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




#dpdt on isopycnals with surface density

#adjust figure size
plt.rcParams["figure.figsize"] = (40,15)


pgrid=np.arange(np.round(presgd.max()),0,-0.5) # <- pressure grid
sgrid=np.arange(np.round(densgd.min()),np.round(densgd.max()),0.2) # <- density grid
dpdtgrid2d=np.zeros((len(pgrid),1))
dpdtgrids2d=np.zeros((len(sgrid),1))
datavg1d_d=np.zeros(1)

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
        temp1=smooth(dpdtmp1,9)    #use smooth function
        datavg_d1=np.expand_dims(np.mean(dtmp1),axis=0) 
        datavg1d_d1=np.append(datavg1d_d1,datavg_d1,axis=0) 
        dpdtgrid1=np.expand_dims(np.interp(pgrid,np.flip(ptmp1),np.flip(temp1),np.nan,np.nan),axis=1) # <- interp grid arrays must be increasing
        dpdtgrid2d1=np.append(dpdtgrid2d1,dpdtgrid1,axis=1)   
        dpdtgrids1 = np.expand_dims(np.interp(sgrid,np.flip(stmp1),np.flip(temp1),np.nan,np.nan),axis=1)
        dpdtgrids2d1 = np.append(dpdtgrids2d1,dpdtgrids1,axis=1)
    
        
dpdtgrids2d_anom = 0.*dpdtgrids2d1
for ii in range(1,len(sgrid)):
    dpdtgrids2d_anom[ii,:] = dpdtgrids2d1[ii,:]-np.nanmean(dpdtgrids2d1[ii,:])
    

#set up DATE2 time series
date_up=np.squeeze(dategd[up1])

DATE2=[]
for row in datavg1d_d1[1:-1]:
    DATE2.append(datetime.datetime.fromtimestamp(row))   #convert unix timestamp into local datetime
    

#pcolor graph for timeseries-surface density graph (colored by dpdt)
pgraph=plt.pcolor(DATE2,sgrid,dpdtgrids2d_anom[:,1:-1],vmin=-0.1,vmax=0.1,cmap=cmo.balance) 
plt.ylim(sgrid.min(),sgrid.max())  
cbar=plt.colorbar(pgraph)
ax=pgraph.axes
cbar.ax.set_ylabel('dpdt (dbar/s)',size=30)
cbar.ax.tick_params(labelsize=30)    #adjust label size


#label the graph
plt.title('dpdt on isopycnals'+ " "+dm2+"-"+dn2,size=30)
plt.xlabel('Date',size=30)
plt.ylabel('Surface Density (g/cm^3)',size=30)
plt.xticks(size = 25)
plt.yticks(size = 30)

#save figure
plt.savefig(f_namefig2, bbox_inches='tight')
plt.show()



