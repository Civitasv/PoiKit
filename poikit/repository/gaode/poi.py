# -- coding: utf-8 --
from ...api.gaode import poi as poi_api
from ...model.gaode import poi as poi_model


def get_poi_by_polygon(request, page=1, size=20):
    r = poi_api.get_poi_by_polygon(request, page, size)
    if r.status_code == 200:
        response = r.json()
        if response["status"] == '1':
            items = []
            for item in response["pois"]:
                if request.extensions == 'all':
                    details = {
                        "postcode": item.get("postcode", ""),
                        "website": item.get("website", ""),
                        "email": item.get("email", ""),
                        "pcode": item.get("emial", ""),
                        "citycode": item.get("citycode", ""),
                        "adcode": item.get("adcode", ""),
                        "entr_location": item.get("entr_location", ""),
                        "navi_poiid": item.get("navi_poiid", ""),
                        "gridcode": item.get("gridcode", ""),
                        "alias": item.get("alias", ""),
                        "business_area": item.get("business_area", ""),
                        "parking_type": item.get("parking_type", ""),
                        "tag": item.get("type", ""),
                        "indoor_map": item.get("indoor_map", ""),
                        "photos": item.get("photos", "")
                    }
                items.append(
                    poi_model.Response.Item(
                        item.get("id", ""),
                        item.get("name", ""),
                        item.get("type", ""),
                        item.get("typecode", ""),
                        item.get("address", ""),
                        item.get("location", ""),
                        item.get("tel", ""),
                        item.get("pname", ""),
                        item.get("cityname", ""),
                        item.get("adname", ""),
                        details if request.extensions == 'all' else ""))

            return poi_model.Response(
                response["status"], response["info"], response["infocode"], response["count"], items)

    return False
