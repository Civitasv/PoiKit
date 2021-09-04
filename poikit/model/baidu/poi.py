# -- coding: utf-8 --
import json


class Request(object):
    def __init__(self, ak, hexagon, query=None, tag=None, scope="1", filter_exp="", coord_type=3, extensions_adcode="true") -> None:
        if query is None:
            query = []
        if tag is None:
            tag = []
        self.ak = ak
        self.query = '$'.join(query)
        self.tag = ','.join(tag)
        self.center = hexagon.center
        self.radius = hexagon.radius
        self.scope = scope
        self.filter_exp = filter_exp
        self.coord_type = coord_type
        self.extensions_adcode = extensions_adcode


class Response(object):
    class Item(object):
        def __init__(self, uid, name, location, address, province, city, area, adcode, street_id, telephone, detail_info) -> None:
            self.uid = uid
            self.name = name
            self.lng = location["lng"]
            self.lat = location["lat"]
            self.address = address
            self.province = province
            self.city = city
            self.area = area
            self.adcode = adcode
            self.street_id = street_id
            self.telephone = telephone
            self.detail_info = json.dumps(detail_info, ensure_ascii=False)

        def __str__(self) -> str:
            return '{' + 'uid={}, name={}, address={}, location={}, {}, telephone={}, province={}, city={}, area={}, adcode={}, street_id={}, detail_info={}'.format(self.uid, self.name, self.address, str(self.lng), str(self.lat), self.telephone, self.province, self.city, self.area, self.adcode, self.street_id, self.detail_info) + '}'

        def __hash__(self):
            return hash(self.uid)

        def __eq__(self, arg):
            if not arg or type(self) != type(arg):
                return False

            return self.uid == arg.uid

    def __init__(self, status, message, total, items) -> None:
        self.status = status
        self.message = message
        self.total = total
        self.pois = items

    def __str__(self) -> str:
        return '{' + 'status={}, message={}, total={}, '.format(self.status, self.message, self.total) + "pois=[" + ", ".join(map(str, self.pois)) + "]" + '}'
