from httplib2 import Credentials
import numpy as np
import rasterio
import rasterio.warp
import ee
import requests
from retry import retry
import shutil
import multiprocessing
import math
import os
from .config import eejson, s_account


# see  https://developers.google.com/earth-engine/guides/service_account
credentials = ee.ServiceAccountCredentials(s_account, eejson)
ee.Initialize(credentials=credentials,
              opt_url='https://earthengine-highvolume.googleapis.com')
RGB = ['B4', 'B3', 'B2']
PERCENTILE_SCALE = 50
NEWRGB = ['B4_median', 'B3_median', 'B2_median']
TRUE_RGB = ['TCI_R', 'TCI_G', 'TCI_B']


class EEH:
    def __init__(self, directory = './output', size = 512):
        self.dimensions = [size, size]
        self.path = directory
        self.alos_path = f'{directory}/alos'
        self.meters = 100
        self.min = 0
        self.max = 300
        self.sat_min = 0
        self.sat_max = 300
        self.crs = 'EPSG:4326'

    def init_directory(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if not os.path.exists(self.alos_path):
            os.makedirs(self.alos_path)

    @retry(tries=10, delay=1, backoff=2)
    def getALOSDEM(self, lat, lon):
        u_poi = ee.Geometry.Point(lon, lat)
        lyon = u_poi.buffer(self.meters)  # meters
        alos = ee.ImageCollection('JAXA/ALOS/AW3D30/V3_2').select('DSM')#.filterBounds(lyon)

        proj = alos.first().select(0).projection()

        alos = alos.mosaic().setDefaultProjection(proj)
        url = alos.getThumbUrl({'min': self.min,
                                    'max': self.max,
                                    'region': lyon,
                                    'dimensions': self.dimensions,
                                    'format': 'png',
                                    'crs': self.crs,
                                    'bestEffort': True,
                                    })

        r = requests.get(url, stream=True)
        
        if r.status_code != 200:
            print("Failed to get image...")
            raise r.raise_for_status()
        filename = f'{self.alos_path}/{lat}_{lon}_dem.png'
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(r.raw, out_file)
        print(f"Done: {filename}")

    def work_save_map_image(self, latlon_list):
        pool = multiprocessing.Pool()
        pool.starmap(self.getALOSDEM, latlon_list)
        pool.close()
        pool.join()


    def workALOS(self,  csv):
        import pandas as pd
        df = pd.read_csv(csv,  encoding='cp949' , header = 0, engine = 'python')
        latlon = df.loc[:, ['lat', 'lon']]
        self.work_save_map_image(latlon.values.tolist())


if __name__ == '__main__':
    eee = EEH()
    eee.init_directory()
    eee.workALOS('D:\\1_SW2\\data\\for_cnn\\lon_lat_list.csv')