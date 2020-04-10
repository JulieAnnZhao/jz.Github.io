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


#date-pressure scatter plot color with upcast dpdt
plt.rcParams["figure.figsize"] = (35,10)

#DATE1 array
date_up=np.squeeze(dategd[up1])
#get DATE array for time axis in subplot plottings
import datetime
DATE_up=[]
for row in date_up:
    DATE_up.append(datetime.datetime.fromtimestamp(row))  #convert unix timestamp into local datetime

#scatter plot
scatter2=plt.scatter(DATE_up,np.squeeze(presgd[up1]),c=np.squeeze(dp1[up1]),cmap=cmo.ice,vmin=-0.25,vmax=0.)  #use dpdt as color bar
cbar=plt.colorbar(scatter2)
ax=scatter2.axes
ax.invert_yaxis()
cbar.ax.tick_params(labelsize=30)
cbar.ax.set_ylabel('dpdt (dbar/s)',size = 30)
ax.set_xlim([datetime.date(start.year, start.month, start.day), datetime.date(end.year, end.month, end.day)])

#label the profile in figure 3 with red dots
mk=np.argwhere((profnum1>1127.5)&(profnum1<1130.5))
nk=np.argwhere((profnum1>1123.5)&(profnum1<1125.5))   
#start point for two different profiles
plt.scatter(DATE_up[mk.min()],presgd[mk.min()],color='red',s=100)   #red dot for 3a
plt.scatter(DATE_up[nk.min()],presgd[nk.min()],color='yellow',s=100)  #yellow dot for 3b

plt.title('Upcast dpdt Pressure plotting'+ " "+dm2+"-"+dn2,size=30)   #add start and end date into title
plt.ylabel('Pressure (dbar)',size=30)
plt.grid(True)
plt.xlabel('Date',size=30)



plt.xticks(size = 25)
plt.yticks(size = 30)

#save figure
plt.savefig(f_namefig, bbox_inches='tight')
plt.show()



