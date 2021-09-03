# -- coding: utf-8 --

from . import base_url


def get_district_url(adcode=100000):
    url = "{}{}.json".format(base_url, adcode)
    return url
