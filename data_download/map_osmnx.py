# 2022 Nor-s

import osmnx as ox, networkx as nx, geopandas as gpd, matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, LineString
from descartes import PolygonPatch
import requests
import matplotlib.cm as cm
import matplotlib.colors as colors
from random import sample
from multiprocessing import Pool, cpu_count
import pandas as pd
import os

ox.config(use_cache=True, log_console=False)
ox.__version__

def make_dirs(dirs):
    if not os.path.exists(dirs):
        os.makedirs(dirs)

class KoreaRoadMap():
    def __init__(self):
        self.city_list = ['서울', '부산', '대구', '인천', '광주', '대전', '울산']
        self.city_size = len(self.city_list)
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
        self.save_folder = './data/korea_load/'
        self.save_img_folder = f'{self.save_folder}/images'
        self.sample_size = [2000,  1000,   1000,   2000,   1000,   1000,   2000]
        self.dist = 50 # 100m
        self.network_type = 'all'

    def init_directory(self):
        make_dirs(self.save_folder)
        make_dirs(self.save_img_folder)

    def get_city_graph(self, city_name):
        return ox.graph_from_place(f'{city_name}, 대한민국', network_type='drive', simplify=False) 
    
    def is_out_of_range_lon_lat(self, lon, lat, dist, city_lon_lat_list):
        # (lon, lat) 좌표가 city_lon_lat_list의 좌표들과의 거리가 최소 dist 이상인지 확인
        from haversine import haversine
        for lon2, lat2 in city_lon_lat_list:
            d = haversine((lat, lon), (lat2, lon2), unit = 'm')
            if d <= dist:
                return False
        return True
    
    def get_graph_and_list(self, city_idx):
        G = self.get_city_graph(self.city_list[city_idx])
        G_list = list(G.nodes)

        return [G, G_list]
    
    def get_lon_lat_list(self, G, G_list ,idx_list):
        lon_lat_list = []

        for idx in idx_list:
            node_id = G_list[idx]
            lon = G.nodes[node_id]['x'] 
            lat = G.nodes[node_id]['y'] 
            lon_lat_list.append([lon, lat])
        
        return lon_lat_list
    
    def get_city_lon_lat(self, city_idx):
        G, G_list = self.get_graph_and_list(city_idx)
        idx_list = range(0, len(G_list))
        print(f'city_idx: {city_idx}, idx_list: {len(idx_list)}')
        return self.get_lon_lat_list(G, G_list, idx_list)


    def get_random_city_lon_lat(self, city_idx):
        G, G_list = self.get_graph_and_list(city_idx)
        random_list = sample(range(0, len(G_list)), self.sample_size[city_idx])
        print(f'city_idx: {city_idx}, random_list: {len(random_list)}')
        return self.get_lon_lat_list(G, G_list, random_list)

    def save_map_image(self, lon, lat, idx):
        try:
            point = (lat, lon)
            fp = f"{self.save_img_folder}/{int(idx)}.png"
            fig, ax = ox.plot_figure_ground(
                        point=point, 
                        dist=self.dist,
                        filepath =fp,
                        network_type=self.network_type, 
                        street_widths=self.street_widths, 
                        dpi=self.dpi,
                        save=True,
                        show=False,
                        close=True,
                        )
            
        except Exception as e:
            print(f'error {lat}, {lon}: {str(e)}')
            return
        # print(f'{int(idx)}.png : {lon}, {lat}')
    
    def work_save_map_image(self, lon_lat_list):
        pool = Pool(cpu_count())

        print('\n--------------start map--------------\n')
        pool.starmap(self.save_map_image, lon_lat_list)
        pool.close()
        pool.join()
        print('==============end  work==============\n')
        


class KoreaRandomRoadMapDownloader(KoreaRoadMap):
    def __init__(self):
        super().__init__()

        self.save_folder = f'./data/random_{self.dist}/'
        self.save_img_folder = f'{self.save_folder}/images'
        self.lon_lat_csv_filename = f'{self.save_folder}/lon_lat_list.csv'
        self.sample_size = [40000,  5000, 5000, 5000, 5000, 5000, 5000]
        self.sample_num = 30000

        self.df_lon_lat = pd.DataFrame(columns=['lon', 'lat', 'id'])

        self.init_directory()

       
    def init_lon_lat_df(self):
        print('--------------init_df--------------\n')
        try:        
            self.df_lon_lat = pd.read_csv(self.lon_lat_csv_filename, encoding = 'cp949', header = 0, engine = 'python')
        except Exception:
            lonlat_id = 0
            lon_lat_df_list = []

            for idx in range(0, self.city_size):
                print(f'{self.city_list[idx]}')
                lon_lat_list = self.get_random_city_lon_lat(idx)
                for lon, lat in lon_lat_list:
                    lon_lat_df_list.append(pd.DataFrame.from_records({'lon': [lon], 'lat': [lat], 'id': [lonlat_id]}))
                    lonlat_id += 1
            self.df_lon_lat = pd.concat(lon_lat_df_list, ignore_index=True)
            self.df_lon_lat = self.df_lon_lat.sample(n=min(self.sample_num, len(self.df_lon_lat) ), random_state=1004, replace=False)
            self.df_lon_lat.to_csv(self.lon_lat_csv_filename, encoding='cp949', index = False)

        return self.df_lon_lat
    
    
    def work(self):
        print('cpu_count: ', cpu_count())
        print('\n==============start work==============\n')
        self.init_lon_lat_df()
        self.df_lon_lat = self.df_lon_lat.loc[:, ["lon","lat", "id"]]
        lon_lat_list = self.df_lon_lat.values.tolist()
        pool = Pool(cpu_count())
        print('\n--------------start map--------------\n')
        pool.starmap(self.save_map_image, lon_lat_list)
        pool.close()
        pool.join()
        print('==============end  work==============\n')
    
class KoreaNoAccidentRoadMapDownloader(KoreaRoadMap):
    def __init__(self):
        super().__init__()
        self.city_list = ['서울', '부산', '대구', '인천', '광주', '대전', '울산']
        self.city_size = len(self.city_list)

        self.df_lon_lat = pd.DataFrame(columns=['lon', 'lat', 'id'])
        self.min_dist = 500 # 500
        self.sample_num = 30000
        self.sample_size = [40000,  5000, 5000, 5000, 5000, 5000, 5000]

        self.save_folder = f'./data/no_accident_{self.dist}_{self.min_dist}/'
        self.save_img_folder = f'{self.save_folder}/images'
        self.lon_lat_csv_filename = f'{self.save_folder}/lon_lat_list.csv'


        self.init_directory()
        self.accident_filename = 'D:\\1_SW2\\data\\17_21_이륜차_사고다발지역(좌표o).csv'
    
    def get_accident_lon_lat(self):
        motorcycle = pd.read_csv(self.accident_filename, encoding = 'cp949', index_col = 0, header = 0, engine = 'python')
        motorcycle = motorcycle.reset_index()
        
        lon = motorcycle['경도'].values.tolist()
        lat = motorcycle['위도'].values.tolist()
        
        return list(zip(lon, lat))
        

    def init_lon_lat_df(self, accident_lon_lat_list):
        print('--------------init_df--------------\n')
        try:        
            self.df_lon_lat = pd.read_csv(self.lon_lat_csv_filename, encoding = 'cp949', header = 0, engine = 'python')
        except Exception:
            lonlat_id = 0
            # https://zephyrus1111.tistory.com/115
            lon_lat_df_list = []
            for idx in range(0, self.city_size):
                print(f'{self.city_list[idx]}')
                lon_lat_list = self.get_random_city_lon_lat(idx)
                print(f'- lon_lat_list: {len(lon_lat_list)}')
                for lon, lat in lon_lat_list:
                    if self.is_out_of_range_lon_lat(lon, lat, self.min_dist, accident_lon_lat_list):
                        lon_lat_df_list.append(pd.DataFrame.from_records({'lon': [lon], 'lat': [lat], 'id': [lonlat_id]}))
                        lonlat_id += 1
                print(f'- lon_lat_df_list: {len(lon_lat_df_list)}')
            self.df_lon_lat = pd.concat(lon_lat_df_list, ignore_index=True)
            self.df_lon_lat = self.df_lon_lat.sample(n=min(self.sample_num, len(self.df_lon_lat) ), random_state=1004, replace=False)
            self.df_lon_lat.to_csv(self.lon_lat_csv_filename, encoding='cp949', index = False)

        return self.df_lon_lat

    def work(self):
        print('no accident')
        print('cpu_count: ', cpu_count())
        print('\n==============start work==============\n')
        self.init_lon_lat_df(self.get_accident_lon_lat())
        self.df_lon_lat = self.df_lon_lat.loc[:, ["lon","lat", "id"]]
        
        lon_lat_list = self.df_lon_lat.values.tolist()
        pool = Pool(cpu_count())

        print('\n--------------start map--------------\n')
        pool.starmap(self.save_map_image, lon_lat_list)
        pool.close()
        pool.join()
        print('==============end  work==============\n')

class KoreaAccidentRoadMapDownloader(KoreaRoadMap):
    def __init__(self):
        super().__init__()
        self.city_list = ['서울', '부산', '대구', '인천', '광주', '대전', '울산']
        self.city_size = len(self.city_list)

        self.df_lon_lat = pd.DataFrame(columns=['lon', 'lat', 'id'])

        self.save_folder = f'./data/accident_{self.dist}/'
        self.save_img_folder = f'{self.save_folder}/images'
        self.lon_lat_csv_filename = f'{self.save_folder}/lon_lat_list.csv'
        self.accident_filename = 'D:\\1_SW2\\data\\17_21_이륜차_사고다발지역(좌표o).csv'
        self.step = 7

        self.init_directory()
    
    def init_lon_lat_df(self):
        motorcycle = pd.read_csv(self.accident_filename, encoding = 'cp949', index_col = 0, header = 0, engine = 'python')
        motorcycle = motorcycle.reset_index()
        motorcycle['is_raw'] = True
        motorcycle['id'] = motorcycle.index
        lon_lat_id = motorcycle.index.max() + 1
        poly = motorcycle['다발지역폴리곤'].values.tolist()
        FID = motorcycle['사고다발지FID'].values.tolist()
        self.df_lon_lat = motorcycle.loc[:, ["사고다발지FID", "경도", "위도", "is_raw", "id"]]
        self.df_lon_lat = self.df_lon_lat.rename({'경도': 'lon', '위도': 'lat'}, axis=1)

        import json
        lon_lat_df_list = []
        for row in range(0, len(motorcycle)):
            p = json.loads(poly[row])
            for i in range(0, len(p['coordinates'][0]), self.step):
                point = p['coordinates'][0][i]    
                lat = point[1]
                lon = point[0]
                lon_lat_df_list.append(pd.DataFrame.from_records({'사고다발지FID': [FID[row]], 'lon': [lon], 'lat': [lat], 'id': [lon_lat_id], 'is_raw':[False]}))
                lon_lat_id+=1

        tmp_df = pd.concat(lon_lat_df_list, ignore_index=True)
        self.df_lon_lat = pd.concat(( self.df_lon_lat, tmp_df), ignore_index=True)
        self.df_lon_lat.to_csv(self.lon_lat_csv_filename, encoding='cp949', index = False)

    def work(self):
        print('accident')
        print('cpu_count: ', cpu_count())
        print('\n==============start work==============\n')
        self.init_lon_lat_df()
        self.df_lon_lat = self.df_lon_lat.loc[:, ["lon","lat", "id"]]
        self.work_save_map_image(self.df_lon_lat.values.tolist())

    
if __name__ == '__main__':


    # map_downloader = KoreaAccidentRoadMapDownloader()
    # map_downloader.work()

    # map_downloader = KoreaNoAccidentRoadMapDownloader()
    # map_downloader.work()    
    map_downloader = KoreaRandomRoadMapDownloader()
    map_downloader.work()
