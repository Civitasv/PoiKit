# -- coding: utf-8 --

import poikit.repository.gaode.poi as poi_repo
import poikit.model.gaode.poi as poi
print(poi_repo.get_poi_by_polygon(poi.Request(
    "17b3ad7ccaafe0b0fd1041ce89d20024", 116.460988, 40.006919, 116.48231, 39.99713, ["肯德基"], ["050301"])))
