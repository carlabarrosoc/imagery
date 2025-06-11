import satpy
import sys
from satpy import find_files_and_readers, Scene
from pyproj import Proj
from pyresample.geometry import AreaDefinition
from pyresample import get_area_def
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime,timedelta
import area
from area import get_parameters
import warnings
from glob import glob

warnings.simplefilter('ignore')
# enable access to custom composites/enhancements 
os.environ['SATPY_CONFIG_PATH']='../'


def define_AOI(min_lon,max_lon,min_lat,max_lat,resolution):
    #using lambert conus conform projection which is appropriate for mid-latitudes, consider changing laea to merc for equatorial regions
    proj, lat_0, lon_0,xsize, ysize, area_extent=get_parameters("custom","merc",min_lon,max_lon,min_lat,max_lat,resolution)
    projection= '+proj=%s +lat_0=%s +lon_0=%s +ellps=%s'%(proj, lat_0, lon_0, 'WGS84')
    AOI = get_area_def("custom", '', proj, projection,xsize, ysize, area_extent)
    print("custom", '', proj, projection,xsize, ysize, area_extent)
    return AOI

if __name__ == '__main__':

    file_location=sys.argv[1]
    ch=sys.argv[2]
    time=sys.argv[3]
    #end=sys.argv[3]
    #step=sys.argv[4] #minutes
    coords=sys.argv[4] # fourtuple (min_lon,max_lon,min_lat,max_lat)
    resolution = sys.argv[5]
    min_lon=max_lon=min_lat=max_lat = 0
    predefined_region=False
    
    if (coords != "0"):
        if(len(coords.split(",")) ==4):
            coord=coords.split(",")
            min_lon = float(coord[0])
            max_lon = float(coord[1])
            min_lat= float(coord[2])
            max_lat = float(coord[3])
        else:
            predefined_region=True
            print("predefined satpy region: ",coords)
    
    print("processing timestep: ",time)
    start_time=datetime.strptime(time,"%Y-%m-%dT%H:%M:%SZ")
    end_time=datetime.strptime(time,"%Y-%m-%dT%H:%M:%SZ")+timedelta(minutes=10) # 10-minute resolution of the data
    
    files = find_files_and_readers(base_dir=file_location, reader='fci_l1c_nc',filter_parameters={'start_time': start_time , 'end_time': end_time})
    scn = Scene(filenames=files)

    scn.load([ch], upper_right_corner='NE')

    
    if (coords != "0" and not predefined_region):
       
        AOI = define_AOI(min_lon,max_lon,min_lat,max_lat,resolution)
        scn_resample=scn.resample(AOI) # nearest neighbor interpolator
        scn_resample.save_dataset(ch, filename='tifs/fci_%s_%s_%s.tif' % (ch,'AOI',datetime.strftime(start_time,"%Y%m%dT%H%M%SZ")))
      #  scn_resample.save_dataset(ch, filename='%s/fci_%s_%s.png' % (ch,ch,datetime.strftime(start_time,"%Y%m%dT%H%M%SZ"))) #,
        #overlay={'coast_dir':'/home/jovyan/coastlines/data/Weather/etc/gshhg-shp-2.3.7','color':'black','resolution':'l', 'width': 1.5})
      #  overlay={'coast_dir':'/data/Weather/etc/gshhg-shp-2.3.7/GSHHS_shp','color':'black','resolution':'i', 'width': 1.5,'coastline_filename': 'GSHHS_i_L1',})

        imagefile1=glob("tifs/fci_%s_AOI_%s.tif"%(ch,datetime.strftime(start_time,"%Y%m%dT%H%M%SZ")))
        img1 = plt.imread(imagefile1[0])

        #creating the plot
        crs2=ccrs.PlateCarree()
        plt.figure(figsize=(20, 20))

        crs2 = scn_resample[ch].attrs["area"].to_cartopy_crs()
        ax2 = plt.axes(projection=crs2)

        # Now we can add some coastlines...
      #  ax2.gridlines(draw_labels=True, linestyle='--')
        ax2.coastlines(resolution="10m", color="white")
       # ax2.set_global()
       # states_provinces = cfeature.NaturalEarthFeature(
       #     category="cultural",
       #     name="admin_0_countries",
       #     scale="50m",
       #     facecolor="none")
       # ax2.add_feature(states_provinces, edgecolor="white")    
        #add title
      #  plt.title(ch+ "_AOI_"+ scn_resample[ch].attrs["start_time"].strftime("%Y-%m-%d %H:%M"), fontsize=20, pad=20.0)
        
        # in the end, we can plot our image data...
        ax2.imshow(img1, transform=crs2, extent=crs2.bounds, origin="upper")
      #  plt.savefig("%s/%s.png"%(ch,scn_resample[ch].attrs["start_time"].strftime("%Y-%m-%dT%H.%M.%SZ")))    
        plt.gca().set_axis_off()
        plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
        hspace = 0, wspace = 0)
        plt.margins(0,0)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        os.makedirs(ch, exist_ok=True)
        plt.savefig("%s/%s.png"%(ch,scn_resample[ch].attrs["start_time"].strftime("%Y-%m-%dT%H.%M.%SZ")) , bbox_inches = 'tight',
        pad_inches = 0, dpi=300)    
    else:
        if (predefined_region):
            scn_resample=scn.resample(coords)
            scn_resample.save_dataset(ch, filename='tifs/fci_%s_%s_%s.tif' % (ch,coords,datetime.strftime(start_time,"%Y%m%dT%H%M%SZ")))#,
 #           overlay={'coast_dir':'/home/jovyan/coastlines/data/Weather/etc/gshhg-shp-2.3.7','color':'black','resolution':'l', 'width': 1.5})

            imagefile1=glob("tifs/fci_%s_%s_%s.tif"%(ch,coords,datetime.strftime(start_time,"%Y%m%dT%H%M%SZ")))
            print("tifs/fci_%s_%s_%s.tif"%(ch,coords,datetime.strftime(start_time,"%Y%m%dT%H%M%SZ")))
            img1 = plt.imread(imagefile1[0])
            #creating the plot
            crs2=ccrs.PlateCarree()
            plt.figure(figsize=(20, 20))
            crs2 = scn_resample[ch].attrs["area"].to_cartopy_crs()
            ax2 = plt.axes(projection=crs2)
            # Now we can add some coastlines...
            #ax2.gridlines(draw_labels=True, linestyle='--')
            ax2.coastlines(resolution="10m", color="white")
            ax2.imshow(img1, transform=crs2, extent=crs2.bounds, origin="upper")
            plt.gca().set_axis_off()
            plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
            hspace = 0, wspace = 0)
            plt.margins(0,0)
            plt.gca().xaxis.set_major_locator(plt.NullLocator())
            plt.gca().yaxis.set_major_locator(plt.NullLocator())
            os.makedirs(ch, exist_ok=True)
            plt.savefig("%s/%s.png"%(ch,scn_resample[ch].attrs["start_time"].strftime("%Y-%m-%dT%H.%M.%SZ")), bbox_inches = 'tight',
            pad_inches = 0)    
        
        else:
            scn_resample=scn.resample()
            scn_resample.save_dataset(ch, filename='tifs/fci_%s_FD_%s.tif' % (ch,datetime.strftime(start_time,"%Y%m%dT%H%M%SZ")))#,
       #     overlay={'coast_dir':'/home/jovyan/coastlines/data/Weather/etc/gshhg-shp-2.3.7','color':'black','resolution':'l', 'width': 1.5})

            imagefile1=glob("tifs/fci_%s_FD_%s.tif"%(ch,datetime.strftime(start_time,"%Y%m%dT%H%M%SZ")))
            print("tifs/fci_%s_FD_%s.tif"%(ch,datetime.strftime(start_time,"%Y%m%dT%H%M%SZ")))
            img1 = plt.imread(imagefile1[0])
            #creating the plot
            crs2=ccrs.PlateCarree()
            plt.figure(figsize=(20, 20))
            crs2 = scn_resample[ch].attrs["area"].to_cartopy_crs()
            ax2 = plt.axes(projection=crs2)
            # Now we can add some coastlines...
            #ax2.gridlines(draw_labels=True, linestyle='--')
            ax2.coastlines(resolution="10m", color="white")
            ax2.imshow(img1, transform=crs2, extent=crs2.bounds, origin="upper")
            plt.gca().set_axis_off()
            plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
            hspace = 0, wspace = 0)
            plt.margins(0,0)
            plt.gca().xaxis.set_major_locator(plt.NullLocator())
            plt.gca().yaxis.set_major_locator(plt.NullLocator())
            fig = plt.gcf()
            fig.patch.set_alpha(0.0)
            os.makedirs(ch, exist_ok=True)
            fig.savefig("%s/%s.png"%(ch,scn_resample[ch].attrs["start_time"].strftime("%Y-%m-%dT%H.%M.%SZ")), bbox_inches = 'tight',
            pad_inches = 0)     
    
