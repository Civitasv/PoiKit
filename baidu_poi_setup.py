# -- coding: utf-8 --

from poikit.model.crawl import CrawlType
import poikit.execute.baidu.poi as poi

ak = ["99Wx6UCaC50AaD6vtFV7N6iTXhH29UyP"]

crawl_type = CrawlType.ADCODE
crawl_data = "440305"
# crawl_data = Rect(56.006919, 130.48231, 39.99713, 116.460988)
# crawl_data = "user.geojson"

keywords = ["消防机关"]
types = [""]
thread_num = 4
qps = 50
output = "test.csv"


poi.crawl_poi(ak, crawl_type, crawl_data, keywords,
              types, thread_num, qps, output)
