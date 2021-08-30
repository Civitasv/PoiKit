# -- coding: utf-8 --
from typing import Optional
from ...model.gaode.poi import Request
from . import requests
from . import baseUrl

url = "/place/polygon"


def get_poi_by_polygon(request: Request, page: Optional[int] = 1, size: Optional[int] = 20, extensions: Optional[str] = "base"):
    params = {
        "key": request.key,
        "polygon": request.polygon,
        "keywords": request.keywords,
        "types": request.types,
        "extensions": extensions,
        "page": page,
        "size": size
    }
    return requests.get(baseUrl + url, params)
