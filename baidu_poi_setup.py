# -- coding: utf-8 --

import poikit.model.baidu.poi as poi_model
import poikit.repository.baidu.poi as poi_repository

ak = ["99Wx6UCaC50AaD6vtFV7N6iTXhH29UyP"]

query = "ATM机"
tag = "银行"
region = "北京"
threshold = 200
thread_num = 4
qps = 50
output = "test.geojson"

print(poi_repository.get_poi_by_region(
    poi_model.Request(ak[0], query, region)))
