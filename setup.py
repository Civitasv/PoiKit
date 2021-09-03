# -- coding: utf-8 --

from poikit.model.gaode.rect import Rect
import poikit.execute.gaode.poi as poi

keys = ["17b3ad7ccaafe0b0fd1041ce89d20024"]
rect = Rect(56.006919, 130.48231, 39.99713, 116.460988)
keywords = ["肯德基"]
types = ["050301"]
threshold = 800
thread_num = 4
qps = 50
output = "test.shp"

poi.execute(keys, rect, keywords, types, threshold, thread_num, qps, output)
