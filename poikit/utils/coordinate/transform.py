# -- coding: utf-8 --
import math
from ...model.point import Point

PIX = math.pi * 3000 / 180
PI = math.pi
A = 6378245.0
EE = 0.00669342162296594323


def bd09_to_gcj02(point):
    x = point.lng - 0.0065
    y = point.lat - 0.006
    z = math.sqrt(x**2 + y**2) - 0.00002 * math.sin(y * PIX)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * PIX)
    gcj02Lng = z * math.cos(theta)
    gcj02Lat = z * math.sin(theta)
    return Point(gcj02Lng, gcj02Lat)


def gcj02_to_bd09(point):
    z = math.sqrt(point.lng ** 2 + point.lat ** 2) + \
        0.00002 * math.sin(point.lat * PIX)
    theta = math.atan2(point.lat, point.lng) + 0.000003 * \
        math.cos(point.lng * PIX)
    bd09Lng = z * math.cos(theta) + 0.0065
    bd09Lat = z * math.sin(theta) + 0.006
    return Point(bd09Lng, bd09Lat)


def gcj02_to_wgs84(point):
    if out_of_china(point):
        return False
    d_lat = transform_lat(point.lng - 105.0, point.lat - 35.0)
    d_lng = transform_lng(point.lng - 105.0, point.lat - 35.0)
    rad_lat = point.lat / 180.0 * PI
    magic = math.sin(rad_lat)
    magic = 1.0 - EE * magic * magic

    sqrt_magic = math.sqrt(magic)
    d_lat = d_lat * 180.0 / ((A * (1 - EE)) / (magic * sqrt_magic) * PI)
    d_lng = d_lng * 180.0 / (A / sqrt_magic * math.cos(rad_lat) * PI)
    wgs84_lat = point.lat - d_lat
    wgs84_lng = point.lng - d_lng
    return Point(wgs84_lng, wgs84_lat)


def wgs84_to_gcj02(point):
    if out_of_china(point):
        return False
    d_lat = transform_lat(point.lng - 105.0, point.lat - 35.0)
    d_lng = transform_lng(point.lng - 105.0, point.lat - 35.0)
    rad_lat = point.lat / 180.0 * PI
    magic = math.sin(rad_lat)
    magic = 1.0 - EE * magic * magic

    sqrt_magic = math.sqrt(magic)
    d_lat = d_lat * 180.0 / ((A * (1 - EE)) / (magic * sqrt_magic) * PI)
    d_lng = d_lng * 180.0 / (A / sqrt_magic * math.cos(rad_lat) * PI)
    gcj02_lat = point.lat + d_lat
    gcj02_lng = point.lng + d_lng
    return Point(gcj02_lng, gcj02_lat)


def bd09_to_wgs84(point):
    return gcj02_to_wgs84(bd09_to_gcj02(point))


def wgs84_to_bd09(point):
    return gcj02_to_bd09(wgs84_to_gcj02(point))


def transform_lat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * \
        lat + 0.1 * lng * lat + 0.2 * math.sqrt(math.abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) + 40.0 *
            math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) + 320.0 *
            math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret


def transform_lng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
        0.1 * lng * lat + 0.1 * math.sqrt(math.abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) + 40.0 *
            math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 *
            math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret


def out_of_china(point):
    return point.lng < 72.004 or point.lng > 137.8347 or point.lat < 0.8293 or point.lat > 55.8271
