# -- coding: utf-8 --
from typing import Optional
from ...api.gaode import poi as poi_api
from ...model.gaode import poi as poi_model


def get_poi_by_polygon(request: poi_model.Request, page: Optional[int] = 1, size: Optional[int] = 20, extensions: Optional[str] = "base"):
    r = poi_api.get_poi_by_polygon(request, page, size, extensions)

    if r.status_code == 200:
        response = r.json()
        items = []
        for item in response["pois"]:
            items.append(poi_model.Response.Item(item["id"], item["name"], item["type"], item["typecode"],
                         item["address"], item["location"], item["tel"], item["pname"],
                         item["cityname"], item["adname"]))

        return poi_model.Response(
            response["status"], response["info"], response["infocode"], response["count"], items)
    else:
        return False
