from geopandas import base
from . import requests
from . import base_url

url = '/place/v2/search'


def get_poi_by_region(request, page=1, size=20):
    params = {
        "query": request.query,
        "tag": request.tag,
        "region": request.region,
        "city_limit": request.city_limit,
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
