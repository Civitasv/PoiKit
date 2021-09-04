# -- coding: utf-8 --
import geopandas
import json
import csv
import time
import threading
import concurrent.futures
import re
import math

from ...model.point import Point
from ...model.baidu import poi as poi_model
from ...model.baidu.hexagon import Hexagon
from ...repository.baidu import poi as poi_repo
from ...model.crawl import CrawlType
from ...model.rect import Rect
from ...api.datav import bound

# 线程锁
lock = threading.Lock()


def crawl_poi(keys, crawl_type, data, query, tag, thread_num, qps, output, coord_type=3, scope="1", filter_exp=""):
    if crawl_type == CrawlType.RECT:
        execute(keys, data, query, tag, thread_num, qps,
                output, coord_type, scope, filter_exp)
    elif crawl_type == CrawlType.ADCODE or crawl_type == CrawlType.USER_CUSTOM:
        df = geopandas.read_file(bound.get_district_url(
            data)) if crawl_type == CrawlType.ADCODE else geopandas.read_file(data)
        bounds = df.bounds
        rect = Rect(bounds.at[0, 'maxy'], bounds.at[0, 'maxx'],
                    bounds.at[0, 'miny'], bounds.at[0, 'minx'])
        execute(keys, rect, query, tag, thread_num, qps,
                output, coord_type, scope, filter_exp)


def execute(keys, rect, query, tag, thread_num, qps, output, coord_type, scope, filter_exp):
    _keys = list(filter(check_key, keys))  # 所有合法key
    if not check_rect(rect):
        print("{} 格式错误，请检查".format(rect))
        return
    _per_execute_time = per_execute_time(len(_keys), thread_num, qps)

    # 1. 使用正六边形对矩形剖分
    hexagons = []
    generate_hexagons(hexagons, rect)

    # 2. 开始爬取
    result = []
    for hexagon in hexagons:
        result.extend(get_poi(keys, hexagon, _per_execute_time,
                      thread_num, query, tag, coord_type, scope, filter_exp))

    print("该区域共有POI数据：{}条".format(len(result)))

    # 3. 去重
    result = list(set(result))
    print("去重完成，该区域共有POI数据：{}条".format(len(result)))
    # 4. 导出数据
    export(result, output)


def check_key(key):
    rexp = r'^[a-zA-Z0-9]+$'
    return True if re.match(rexp, key) else False


def check_rect(rect):
    return between(rect.top, -90, 90) and between(rect.bottom, -90, rect.top) and between(rect.right, -180, 180) and between(rect.left, -180, rect.right)


def per_execute_time(key_num, thread_num, qps):
    return thread_num / (qps * key_num)


def generate_hexagons(hexagons, rect):
    r = 0.05  # 单位：度
    r_m = 6000  # 单位：m
    distance = r * math.sin(math.pi / 6) * 2  # 六边形圆心之间的距离
    x_start = rect.left
    y_start = rect.bottom + r * math.cos(math.pi / 3)

    while True:
        i = 0
        while True:
            hexagon = Hexagon(Point(x_start if i % 2 == 0 else x_start + distance / 2,
                                    y_start), r_m)
            hexagons.append(hexagon)
            if y_start + r > rect.top:
                break
            y_start += 3 * r / 2
            i += 1
        if x_start + distance / 2 > rect.right:
            break
        x_start += distance


def get_poi(keys, hexagon, per_execute_time, thread_num, query, tag, coord_type, scope, filter_exp):
    result = []

    # 获取第一页数据
    first_page = poi_repo.get_poi_by_circle(poi_model.Request(
        keys[0], hexagon, query, tag, scope, filter_exp, coord_type))
    if not first_page or first_page.status != 0:
        return result

    total = first_page.total
    size = 20
    task_num = int(total / size) + 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
        results = [executor.submit(per_poi_task,
                                   keys=keys,
                                   per_execute_time=per_execute_time,
                                   hexagon=hexagon,
                                   query=query,
                                   tag=tag,
                                   coord_type=coord_type,
                                   scope=scope,
                                   filter_exp=filter_exp,
                                   page=page,
                                   size=size)
                   for page in range(2, task_num + 1)]

        for f in concurrent.futures.as_completed(results):
            item_result = f.result()
            if item_result:
                result.extend(item_result.pois)
    return result


def per_poi_task(keys, per_execute_time, hexagon, query, tag, coord_type, scope, filter_exp, page, size):
    start = time.perf_counter()
    key = get_key(keys)

    if not key:
        return False

    res = poi_repo.get_poi_by_circle(poi_model.Request(
        key, hexagon, query, tag, scope, filter_exp, coord_type))

    if not res or res.status != 0:
        with lock:
            if key in keys:
                res = retry(key, hexagon, query, tag, scope,
                            filter_exp, coord_type, page, size)
                if not res or res.infocode != 0:
                    # 数据获取失败
                    print("数据获取失败，key={},query={},tag={},message={}".format(
                        key, query, tag, res.message if res else "res == null"))
                    keys.remove(key)
                else:
                    return res

            while len(keys) != 0:
                # 尝试其他key
                key = get_key(keys)
                res = poi_repo.get_poi_by_circle(poi_model.Request(
                    key, hexagon, query, tag, scope, filter_exp, coord_type))

                if not res or res.infocode != 0:
                    res = retry(key, hexagon, query, tag, scope,
                                filter_exp, coord_type, page, size)
                    if not res or res.infocode != 0:
                        # 数据获取失败
                        print("数据获取失败，key={},query={},tag={},message={}".format(
                            key, query, tag, res.message if res else "res == null"))
                        keys.remove(key)
                    else:
                        return res
                else:
                    return res

            print("key 池已耗尽，无法继续获取数据")
            return False
    end = time.perf_counter()
    if(end - start < per_execute_time):
        time.sleep(per_execute_time - (end - start))

    return res


def get_key(keys):
    if len(keys) == 0:
        return False
    key = keys.pop()
    keys.insert(0, key)
    return key


def retry(key, hexagon, query, tag, coord_type, scope, filter_exp):
    for _ in range(3):
        res = poi_repo.get_poi_by_circle(poi_model.Request(
            key, hexagon, query, tag, scope, filter_exp, coord_type))
        if not res or res.infocode != 0:
            retry(key, hexagon, query, tag, coord_type, scope, filter_exp)
        else:
            return res
    return False


def export(result, output):
    filetype = output.split(".")[-1]

    if filetype == 'csv':
        with open(output, mode="w", newline='', encoding="utf-8") as result_file:
            csv_writer = csv.writer(
                result_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(["uid", "name", "address", "lng", "lat", "province",
                                "city", "area", "adcode", "street_id", "telephone", "details"])
            for item in result:
                csv_writer.writerow([item.uid, item.name, item.address, item.lng, item.lat, item.province, item.city,
                                    item.area, item.adcode, item.street_id, item.telephone, item.detail_info])
    elif filetype == "geojson" or filetype == "shp":
        geojson = {}
        features = []
        for item in result:
            item_obj = {"type": "Feature"}
            item_obj["properties"] = {
                "uid": str(item.uid),
                "name": str(item.name),
                "address": str(item.address),
                "province": str(item.province),
                "city": str(item.city),
                "area": str(item.area),
                "adcode": str(item.adcode),
                "street_id": str(item.street_id),
                "telephone": str(item.telephone),
                "details": str(item.detail_info),
            }
            item_obj["geometry"] = {"type": "Point",
                                    "coordinates": [item.lng, item.lat]}
            features.append(item_obj)
        geojson["type"] = "FeatureCollection"
        geojson["features"] = features
        if filetype == "geojson":
            with open(output, "w", encoding="utf-8") as result_file:
                result_file.write(json.dumps(
                    geojson, ensure_ascii=False, indent=4))
        else:
            df = geopandas.GeoDataFrame.from_features(geojson)
            df.to_file(output, driver="ESRI Shapefile", encoding="utf-8")


def between(num, start, end):
    return num >= start and num <= end
