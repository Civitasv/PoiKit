from geopandas import base
from . import requests
from . import base_url

url = '/place/v2/search'


def get_poi_by_circle(request, page=1, size=20):
    params = {
        "query": request.query,
        "tag": request.tag,
        "location": "{},{}".format(request.center.lat, request.center.lng),
        "radius": request.radius,
        "radius_limit": "true",
        "extensions_adcode": request.extensions_adcode,
        "scope": request.scope,
        "filter": request.filter_exp,
        "coord_type": request.coord_type,
        "ak": request.ak,
        "output": 'json',
        "page_num": page,
        "page_size": size
    }

    return requests.get(base_url + url, params)
