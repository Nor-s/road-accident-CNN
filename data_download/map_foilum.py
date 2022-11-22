# 2022 Nor-s

import folium
from selenium import webdriver
import os
import pandas as pd
import time
import cv2
from config import vworld_key
from selenium.webdriver import FirefoxOptions
import cv2

import numpy as np
# Esri.WorldImagery
# CartoDB.PositronNoLabels  https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png
# CartoDB.VoyagerNoLabels
# create a map object with a desired initial map center and initial map zoom
# https://stackoverflow.com/questions/62621475/python-folium-custom-tile-setting

def make_dirs(dirs):
    if not os.path.exists(dirs):
        os.makedirs(dirs)

def center_crop(img, set_size):
    
    h, w, c= img.shape

    if set_size > min(h, w):
        return img

    crop_width = set_size
    crop_height = set_size

    mid_x, mid_y = w//2, h//2
    offset_x, offset_y = crop_width//2, crop_height//2
       
    crop_img = img[mid_y - offset_y:mid_y + offset_y, mid_x - offset_x:mid_x + offset_x]
    return crop_img        

class FoliumCrawl():
    def __init__(self):
        self.zoom_start = 17
        self.save_path = f'./data/foilum-image_kr'
        self.html_path = f'{self.save_path}/html'
        self.png_path = f'{self.save_path}/png'
        self.tiles = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png'
        self.attr= 'CartoDB.Voyager'
        self.max_zoom=18
        self.size_wh = [600, 600]
        self.reszie_wh = 180
        self.sleep_time = 4
        self.opts = FirefoxOptions()
        self.opts.add_argument(f'--width={self.size_wh[0]}')
        self.opts.add_argument(f'--height={self.size_wh[1]}')
        
     
    def make_dir(self):
        make_dirs(self.save_path)
        make_dirs(self.html_path)
        make_dirs(self.png_path)
        
    def screenshot(self, lat, lon, idx = -1):
        m = folium.Map(location=[lat, lon],
                    zoom_start=self.zoom_start, 
                    # tiles= self.tiles, 
                    # attr= self.attr,
                    # tiles = f"http://api.vworld.kr/req/wmts/1.0.0/{vworld_key}/Satellite/{{z}}/{{y}}/{{x}}.jpeg",
                    # attr = "Vworld"
                    tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attr = 'Esri'
                    )
        filename = f'{lat}_{lon}'

        if filename != -1:
            filename = int(idx);

        img = m._to_png()
        img = np.fromstring(img, dtype = np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        img = center_crop(img, self.reszie_wh)
        cv2.imwrite(f'{self.png_path}/{filename}.png', img)
        # mapFname =  f'{self.html_path}/output_{filename}.html'
        # mapObj.save(mapFname)

        # mapUrl = 'file://{0}/{1}'.format(os.getcwd(), mapFname)
        # driver = webdriver.Firefox(options=self.opts)
        # driver.set_window_size(self.size_wh[0], self.size_wh[1])
        # driver.get(mapUrl)
        # time.sleep(self.sleep_time)
        # driver.save_screenshot(f'{self.png_path}/{filename}.png')
        # driver.quit()
        
    def work(self, csv):
        from multiprocessing import Pool, cpu_count
        print('cpu_count: ', cpu_count())
        us = pd.read_csv(csv,  encoding='cp949' , header = 0, engine = 'python')
        latlon = us.loc[:, ['lat', 'lon', 'index']]
        pool = Pool(cpu_count()*2)
        pool.starmap(self.screenshot, latlon.values.tolist())
        pool.close()
        pool.join()
        

class USAccidentDownloader(FoliumCrawl):
    def __init__(self):
        self.min_count = 2
        self.sample_num = 30000
        self.save_path = f'./data/foilum-image_{self.min_count}_{self.zoom_start}'
        self.html_path = f'{self.save_path}/html'
        self.png_path = f'{self.save_path}/png'
                
    def work(self, csv_path):
        from multiprocessing import Pool, cpu_count
        
        print('cpu_count: ', cpu_count())
        us = pd.read_csv(csv_path,   header = 0, engine = 'python')
        lonlat = us.loc[:, ['latBin', 'lonBin', 'count']]
        count = lonlat[lonlat["count"] < self.min_count].reset_index()
        count = count.loc[:, ['latBin', 'lonBin']]
        count = count.sample(n=min(self.sample_num, len(count) ), random_state=1004, replace=False)
        count = count[10000:]
        lon_lat_list = count.values.tolist()
        pool = Pool(cpu_count()-1)
        pool.starmap(self.screenshot, lon_lat_list)
        pool.close()
        pool.join()
    
    
if __name__ == '__main__':
    # fmd = FoilumMapDownloader()
    # fmd.make_dir()
    # fmd.work('data/us_accident_lon_lat_severity_count.csv')
    fc = FoliumCrawl()
    fc.make_dir()
    fc.work('D:\\1_SW2\\data\\for_cnn\\lon_lat_list.csv')