# 이미지 데이터를 통한 이륜차 사고다발지 예측

- 해외와는 다르게 국내 도로 이미지를 활용한 사고다발지 예측에 관한 프로젝트를 찾을 수 없었기에 국내 사고다발지 좌표데이터를 사용하여 사고다발지를 예측해보고자함.
- 다양한 시도를 통해 해외 관련 프로젝트들과 성능차이를 내보고자함.

## 데이터 수집

### CSV, Exel 데이터

- 국내 사고다발지 좌표: https://www.data.go.kr/data/15105286/openapi.do

- 서울시 공간 데이터 (데이터 탐색에 활용)
  - CCTV 좌표: https://www.localdata.go.kr/lif/lifeCtacDataView.do?opnEtcSvcId=12_04_08_E
  - 과속방지턱 좌표: https://www.localdata.go.kr/lif/lifeCtacDataView.do?opnEtcSvcId=12_04_06_E
  - 횡단보도 좌표: http://data.seoul.go.kr/dataList/OA-15554/S/1/datasetView.do
  - 신호등 좌표: http://data.seoul.go.kr/dataList/OA-15554/S/1/datasetView.do;jsessionid=4B75D6E2529334747BAE40CC7FB013D5.new_portal-svr-11


### 이미지 데이터

- Folium(위성) 사용
- OSMNX(도로 네트워크) 사용
- Google Earth Engine(수치고도) 사용

## 데이터 처리

- Folium 데이터: zoom을 17로, center crop 180으로 처리
- QGIS: 수집한 공간데이터인 서울시 데이터와 사고다발지 데이터를 합침.

## 데이터 탐색(상관분석)

### 도로형태와 사고와의 상관관계

![1669549713632](image/README/1669549713632.png)

두 이미지 집합간의 특징 거리를 계산하는 FID를 사용하여 도로 형태와 사고는 상관관계가 있다고 판단함.


### 교통 시설물 공간 데이터 탐색

![1669549179699](image/README/1669549179699.png)

- 과속방지턱, CCTV는 비교적 사상자수와 상관관계가 적음
- 횡단보도, 신호등은 상관관계가 있음
- 하지만, 위성 이미지에는 횡단 보도와 신호등과 같은 정보가 포함되어 있으므로, 직접적으로 사용하지 않음.



## 모델 설계

![1669548466518](image/README/1669548466518.png)

## 모델 학습

![1669548516565](image/README/1669548516565.png)

## 결과

![1669548418762](image/README/1669548418762.png)


## 관련 프로젝트 비교

|프로젝트|정확도|클래스 수|해상도|
|-|-|-|-|
|[Combining Satellite Imagery and Open Data to Map Road Safety](https://ojs.aaai.org/index.php/AAAI/article/view/11168/11027)|78%|3|Google Static Maps API 256×256 pixels, zoom levels (18, 19, and 20).|
|[RoadAccidents](https://github.com/Polmax/RoadAccidents)|78%| 2|200m x 200m| 
|[NYC_Traffic_Safety_Project](https://github.com/panzihang/NYC_Traffic_Safety_Project)| 74.29%| 5| ?|
|[Traffic-Accidents](https://github.com/chineseballer06/Traffic-Accidents)|82%|2|?|
