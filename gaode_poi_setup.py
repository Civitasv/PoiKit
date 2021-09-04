# -- coding: utf-8 --

from poikit.model.crawl import CrawlType
import poikit.execute.gaode.poi as poi

keys = ["17b3ad7ccaafe0b0fd1041ce89d20024"]

crawl_type = CrawlType.ADCODE
crawl_data = "440305"
# crawl_data = Rect(56.006919, 130.48231, 39.99713, 116.460988)
# crawl_data = "user.geojson"

keywords = [""]
types = ["消防机关"]
threshold = 800
thread_num = 4
qps = 50
output = "test.csv"

poi.crawl_poi(keys, crawl_type, crawl_data, keywords,
              types, threshold, thread_num, qps, output, 'base')
