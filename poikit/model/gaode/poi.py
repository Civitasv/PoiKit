# -- coding: utf-8 --
import json


class Request(object):
    def __init__(self, key, rect, keywords=None, types=None, extensions="base") -> None:
        if keywords is None:
            keywords = []
        if types is None:
            types = []
        self.key = key
        self.polygon = "{},{}|{},{}".format(
            rect.left, rect.top, rect.right, rect.bottom)
        self.keywords = "|".join(keywords)
        self.types = "|".join(types)
        self.extensions = extensions


class Response(object):
    class Item(object):
        def __init__(self, id, name, type, typecode, address, location, tel, pname, cityname, adname, details_info) -> None:
            self.id = id
            self.name = name
            self.type = type
            self.typecode = typecode
            self.address = address
            self.lng = float(location.split(",")[0])
            self.lat = float(location.split(",")[1])
            self.tel = tel
            self.pname = pname
            self.cityname = cityname
            self.adname = adname
            self.details = json.dumps(details_info, ensure_ascii=False)

        def __str__(self) -> str:
            return '{' + 'id={}, name={}, type={}, typecode={},address={}, location={}, {}, tel={}, province={}, city={}, adname={}'.format(self.id, self.name, self.type, self.typecode, self.address, str(self.lng), str(self.lat), self.tel, self.pname, self.cityname, self.adname) + '}'

    def __init__(self, status, info, infocode, count, items) -> None:
        self.status = status
        self.info = info
        self.infocode = infocode
        self.count = int(count)
        self.pois = items

    def __str__(self) -> str:
        return '{' + 'status={}, info={}, infocode={}, count={}, '.format(self.status, self.info, self.infocode, str(self.count)) + "pois=[" + ", ".join(map(str, self.pois)) + "]" + '}'
