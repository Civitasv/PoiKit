# -- coding: utf-8 --

class Request(object):
    def __init__(self, ak, query, region, tag="", city_limit="false", extensions_adcode="false", scope="1", filter_exp="", coord_type=3) -> None:
        self.ak = ak
        self.query = query
        self.region = region
        self.tag = tag
        self.city_limit = city_limit
        self.extensions_adcode = extensions_adcode
        self.scope = scope
        self.filter_exp = filter_exp
        self.coord_type = coord_type


class Response(object):
    class Item(object):
        def __init__(self, uid, name, location, address, province, city, area, street_id, telephone, detail_info) -> None:
            self.uid = uid
            self.name = name
            self.lng = location["lng"]
            self.lat = location["lat"]
            self.address = address
            self.province = province
            self.city = city
            self.area = area
            self.street_id = street_id
            self.telephone = telephone
            self.detail_info = detail_info

        def __str__(self) -> str:
            return '{' + 'uid={}, name={}, address={}, location={}, {}, telephone={}, province={}, city={}, area={}, street_id={}, detail_info={}'.format(self.uid, self.name, self.address, str(self.lng), str(self.lat), self.telephone, self.province, self.city, self.area, self.street_id, self.detail_info) + '}'

    def __init__(self, status, message, total, items) -> None:
        self.status = status
        self.message = message
        self.total = total
        self.pois = items

    def __str__(self) -> str:
        return '{' + 'status={}, message={}, total={}, '.format(self.status, self.message, self.total) + "pois=[" + ", ".join(map(str, self.pois)) + "]" + '}'
