# -- coding: utf-8 --
from ...api.baidu import poi as poi_api
from ...model.baidu import poi as poi_model


def get_poi_by_region(request, page=1, size=20):
    r = poi_api.get_poi_by_region(request, page, size)
    if r.status_code == 200:
        response = r.json()

        if response["status"] == 0:
            items = []
            for item in response["results"]:
                items.append(poi_model.Response.Item(item.get("uid", ""), item.get("name", ""), item.get("location", ""), item.get("address", ""), item.get(
                    "province", ""), item.get("city", ""), item.get("area", ""), item.get("street_id", ""), item.get("telephone", ""), item.get("detail_info", "")))

            return poi_model.Response(response["status"], response["message"], response["total"], items)
    return False
