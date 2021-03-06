# -- coding: utf-8 --
from . import requests
from . import baseUrl

url = "/place/polygon"


def get_poi_by_polygon(request, page=1, size=20):
    params = {
        "key": request.key,
        "polygon": request.polygon,
        "keywords": request.keywords,
        "types": request.types,
        "extensions": request.extensions,
        "page": page,
        "size": size
    }
    return requests.get(baseUrl + url, params)
