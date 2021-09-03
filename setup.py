# -- coding: utf-8 --

from poikit.model.gaode.crawl import CrawlType
from poikit.model.gaode.rect import Rect
import poikit.execute.gaode.poi as poi

keys = ["17b3ad7ccaafe0b0fd1041ce89d20024"]

crawl_type = CrawlType.ADCODE
crawl_data = "410000"
# crawl_data = Rect(56.006919, 130.48231, 39.99713, 116.460988)
# crawl_data = "user.geojson"

keywords = ["肯德基"]
types = [""]
threshold = 800
thread_num = 4
qps = 50
output = "test.geojson"

poi.crawl_poi(keys, crawl_type, crawl_data, keywords,
              types, threshold, thread_num, qps, output)
