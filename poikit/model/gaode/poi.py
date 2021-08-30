# -- coding: utf-8 --
from typing import List, Optional


class Request(object):
    def __init__(self, key: str, left: float, up: float, right: float, bottom: float, keywords: Optional[List[str]] = None, types: Optional[List[str]] = None) -> None:
        if keywords is None:
            keywords = []
        if types is None:
            types = []
        self.key = key
        self.polygon = "{},{}|{},{}".format(left, up, right, bottom)
        self.keywords = "|".join(keywords)
        self.types = "|".join(types)


class Response(object):
    class Item(object):
        def __init__(self, id: str, name: str, type: str, typecode: str, address: str, location: str, tel: str, pname: str, cityname: str, adname: str) -> None:
            self.id = id
            self.name = name
            self.type = type
            self.typecode = typecode
            self.address = address
            self.lon = float(location.split(",")[0])
            self.lat = float(location.split(",")[1])
            self.tel = tel
            self.pname = pname
            self.cityname = cityname
            self.adname = adname

        def __str__(self) -> str:
            return '{' + 'id={}, name={}, type={}, typecode={},address={}, location={}, {}, tel={}, province={}, city={}, adname={}'.format(self.id, self.name, self.type, self.typecode, self.address, str(self.lon), str(self.lat), self.tel, self.pname, self.cityname, self.adname) + '}'

    def __init__(self, status: str, info: str, infocode: str, count: str, items: Item) -> None:
        self.status = status
        self.info = info
        self.infocode = infocode
        self.count = int(count)
        self.pois = items

    def __str__(self) -> str:
        return '{' + 'status={}, info={}, infocode={}, count={}, '.format(self.status, self.info, self.infocode, str(self.count)) + "pois=[" + ", ".join(map(str, self.pois)) + "]" + '}'
