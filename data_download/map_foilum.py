import folium
from selenium import webdriver
import os
import pandas as pd
import time
# Esri.WorldImagery
# CartoDB.PositronNoLabels  https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png
# CartoDB.VoyagerNoLabels
# create a map object with a desired initial map center and initial map zoom
# https://stackoverflow.com/questions/62621475/python-folium-custom-tile-setting

def make_dirs(dirs):
    if not os.path.exists(dirs):
        os.makedirs(dirs)
        
class FoilumMapDownloader():
    def __init__(self):
        self.min_count = 2
        self.zoom_start = 18
        self.save_path = f'./data/foilum-image_{self.min_count}_{self.zoom_start}'
        self.html_path = f'{self.save_path}/html'
        self.png_path = f'{self.save_path}/png'
        self.tiles = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png'
        self.attr= 'CartoDB.Voyager'
        self.max_zoom=18
        self.width = 1024
        self.height = 1024
        self.sleep_time = 2.5
        self.sample_num = 30000
        
    def make_dir(self):
        make_dirs(self.save_path)
        make_dirs(self.html_path)
        make_dirs(self.png_path)
    
    def screenshot(self, lat, lon):
        mapObj = folium.Map(location=[lat, lon],
                    zoom_start=self.zoom_start, 
                    tiles= self.tiles, 
                    attr= self.attr,
                    max_zoom=self.max_zoom)
        mapFname =  f'{self.html_path}/output_{lat}_{lon}.html'
        mapObj.save(mapFname)
        mapUrl = 'file://{0}/{1}'.format(os.getcwd(), mapFname)
        driver = webdriver.Firefox()
        driver.set_window_size(self.width, self.height)
        driver.get(mapUrl)
        time.sleep(self.sleep_time)
        driver.save_screenshot(f'{self.png_path}/{lat}_{lon}.png')
        driver.quit()
    
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
    fmd = FoilumMapDownloader()
    fmd.make_dir()
    fmd.work('data/us_accident_lon_lat_severity_count.csv')