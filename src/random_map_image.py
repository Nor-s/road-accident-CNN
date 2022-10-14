import osmnx as ox, networkx as nx, geopandas as gpd, matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, LineString
from descartes import PolygonPatch
import requests
import matplotlib.cm as cm
import matplotlib.colors as colors
from random import sample
from multiprocessing import Pool
import pandas as pd

ox.config(use_cache=True, log_console=False)
ox.__version__

class KoreaRoadMapDownloader():
    def __init__(self):
        self.city_list = ['서울', '부산', '대구', '인천', '광주', '대전', '울산']
    


class KoreaRandomRoadMapDownloader():
    def __init__(self):
        self.city_list = ['서울', '부산', '대구', '인천', '광주', '대전', '울산']
        self.sample_size = [2000,  1000,   1000,   2000,   1000,   1000,   2000]
        self.city_size = len(self.city_list)
        self.save_folder = './data/random/'
        self.save_img_folder = f'{self.save_folder}/images'
        self.df_lon_lat = pd.DataFrame(columns=['lon', 'lat', 'id'])
        self.lon_lat_csv_filename = f'{self.save_folder}/lon_lat_list.csv'
        self.street_widths = {'footway' : 0.5,
                 'steps' : 0.5,
                 'pedestrian' : 0.5,
                 'path' : 0.5,
                 'track' : 0.5,
                 'service' : 2,
                 'residential' : 3,
                 'primary' : 5,
                 'motorway' : 6}
        self.dpi = 40
        self.init_directory()

    def init_directory(self):
        import os
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
        if not os.path.exists(self.save_img_folder):
            os.makedirs(self.save_img_folder)

    def get_city_graph(self, city_name):
        return ox.graph_from_place(f'{city_name}, 대한민국', network_type='drive', simplify=False) 
    
    def get_city_lon_lat(self, city_idx):
        lon_lat_list = []
        G = self.get_city_graph(self.city_list[city_idx])
        G_list = list(G.nodes)
        random_list = sample(range(0, len(G_list)), self.sample_size[city_idx])

        for rnd_idx in random_list:
            node_id = G_list[rnd_idx]
            lon = G.nodes[node_id]['x'] 
            lat = G.nodes[node_id]['y'] 
            lon_lat_list.append([lon, lat])
        
        return lon_lat_list
        
    def init_lon_lat_df(self):
        print('--------------init_df--------------\n')
        try:        
            self.df_lon_lat = pd.read_csv(self.lon_lat_csv_filename,encoding = 'cp949', header = 0, engine = 'python')
        except Exception:
            lonlat_id = 0
            for idx in range(0, self.city_size):
                print(f'{self.city_list[idx]}')
                lon_lat_list = self.get_city_lon_lat(idx)
                for lon, lat in lon_lat_list:
                    self.df_lon_lat = self.df_lon_lat.append({'lon': lon, 'lat': lat, 'id': lonlat_id}, ignore_index=True)
                    lonlat_id += 1
            self.df_lon_lat.to_csv(self.lon_lat_csv_filename, encoding='cp949', index = False)

        return self.df_lon_lat
    
    def get_map_image(self, lon, lat, idx):
        try:
            point = (lat, lon)
            fp = f"{self.save_img_folder}/{int(idx)}.png"
            fig, ax = ox.plot_figure_ground(
                        point=point, 
                        dist=100,
                        filepath =fp,
                        network_type='all', 
                        street_widths=self.street_widths, 
                        dpi=self.dpi,
                        save=True,
                        show=False,
                        close=True,
                        )
            
        except Exception as e:
            print(f'error {str(e)}')
            return
        print(f'{lon}, {lat}')
        
    
    
    def work(self):
        print('\n==============start work==============\n')
        self.init_lon_lat_df()
        lon_lat_list = self.df_lon_lat.values.tolist()
        pool = Pool()
        print('\n--------------start map--------------\n')
        pool.starmap(self.get_map_image, lon_lat_list)
        pool.close()
        pool.join()
        print('==============end  work==============\n')
    
class KoreaNoAccidentRoadMapDownloader(KoreaRandomRoadMapDownloader):
    pass
    
if __name__ == '__main__':

    map_downloader = KoreaRandomRoadMapDownloader()
    map_downloader.work()
