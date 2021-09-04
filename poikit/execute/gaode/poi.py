# -- coding: utf-8 --
import geopandas
import json
import csv
import time
import threading
import concurrent.futures
import re

from geopandas.io.file import read_file
from ...model.gaode import poi as poi_model
from ...model.rect import Rect
from ...repository.gaode import poi as poi_repo
from ...model.crawl import CrawlType
from ...api.datav import bound

# 线程锁
lock = threading.Lock()


def crawl_poi(keys, crawl_type, data, keywords, types, threshold, thread_num, qps, output, extensions="base"):
    if crawl_type == CrawlType.RECT:
        execute(keys, data, keywords, types, extensions,
                threshold, thread_num, qps, output)
    elif crawl_type == CrawlType.ADCODE or crawl_type == CrawlType.USER_CUSTOM:
        df = geopandas.read_file(bound.get_district_url(
            data)) if crawl_type == CrawlType.ADCODE else geopandas.read_file(data)
        bounds = df.bounds
        rect = Rect(bounds.at[0, 'maxy'], bounds.at[0, 'maxx'],
                    bounds.at[0, 'miny'], bounds.at[0, 'minx'])
        execute(keys, rect, keywords, types, extensions,
                threshold, thread_num, qps, output)


def execute(keys, rect, keywords, types, extensions, threshold, thread_num, qps, output):
    _keys = list(filter(check_key, keys))  # 所有合法key
    if not check_rect(rect):
        print("{} 格式错误，请检查".format(rect))
        return
    _per_execute_time = per_execute_time(len(_keys), thread_num, qps)

    # 1. 网格剖分
    grids = []
    initial_pois = []
    generate_grids(grids, initial_pois,
                   keys[0], rect, keywords, types, extensions, threshold)

    # 2. 开始爬取
    result = []
    for i in range(0, len(grids)):
        result.extend(get_poi(keys, grids[i], initial_pois[i],
                              _per_execute_time, thread_num, keywords, types, extensions))

    print("该区域外接矩形内共有POI数据：{}条".format(len(result)))

    # 3. 导出数据
    export(result, output)
    print("数据已导出至{}，注意，目前数据为其外接矩形数据，请使用相关软件进一步过滤".format(output))


def check_key(key):
    rexp = r'^[a-zA-Z0-9]+$'
    return True if re.match(rexp, key) else False


def check_rect(rect):
    return between(rect.top, -90, 90) and between(rect.bottom, -90, rect.top) and between(rect.right, -180, 180) and between(rect.left, -180, rect.right)


def per_execute_time(key_num, thread_num, qps):
    return thread_num / (qps * key_num)


def generate_grids(grids, initial_pois, key, rect, keywords, types, extensions, threshold):
    page = 1
    size = 20
    res = poi_repo.get_poi_by_polygon(
        poi_model.Request(key, rect, keywords, types, extensions), page, size)
    if not res or res.count == 0:
        return

    if res.count > threshold:
        child_width = (rect.right - rect.left) / 2
        child_height = (rect.top - rect.bottom) / 2

        for i in range(2):
            for j in range(2):
                generate_grids(grids,
                               initial_pois,
                               Rect(rect.bottom + (j + 1) * child_height,
                                    rect.left + (i + 1) * child_width,
                                    rect.bottom + j * child_height,
                                    rect.left + i * child_width),
                               keywords,
                               types,
                               extensions,
                               threshold)
    else:
        grids.append(rect)
        initial_pois.append(res)


def get_poi(keys, grid, initial_poi, per_execute_time, thread_num, keywords, types, extensions):
    result = initial_poi.pois
    total = initial_poi.count
    size = 20
    task_num = int(total / size) + 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
        results = [executor.submit(per_poi_task, keys=keys, per_execute_time=per_execute_time,
                                   grid=grid, keywords=keywords, types=types, extensions=extensions, page=page, size=size) for page in range(2, task_num + 1)]

        for f in concurrent.futures.as_completed(results):
            item_result = f.result()
            if item_result:
                result.extend(item_result.pois)
    return result


def per_poi_task(keys, per_execute_time, grid, keywords, types, extensions, page, size):
    start = time.perf_counter()
    key = get_key(keys)

    if not key:
        return False

    res = poi_repo.get_poi_by_polygon(
        poi_model.Request(key, grid, keywords, types, extensions), page, size)

    if not res or res.infocode != '10000':
        with lock:
            if key in keys:
                res = retry(key, grid, keywords, types, extensions, page, size)
                if not res or res.infocode != '10000':
                    # 数据获取失败
                    print("数据获取失败，key={},keywords={},types={},infocode={}".format(
                        key, keywords, types, res.infocode if res else "res == null"))
                    keys.remove(key)
                else:
                    return res

            while len(keys) != 0:
                # 尝试其他key
                key = get_key(keys)
                res = poi_repo.get_poi_by_polygon(
                    poi_model.Request(key, grid, keywords, types, extensions), page, size)

                if not res or res.infocode != '10000':
                    res = retry(key, grid, keywords, types,
                                extensions, page, size)
                    if not res or res.infocode != '10000':
                        # 数据获取失败
                        print("数据获取失败，key={},keywords={},types={},infocode={}".format(
                            key, keywords, types, res.infocode if res else "res == null"))
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


def retry(key, grid, keywords, types, extensions, page, size):
    for _ in range(3):
        res = poi_repo.get_poi_by_polygon(
            poi_model.Request(key, grid, keywords, types, extensions), page, size)
        if not res or res.infocode != '10000':
            retry(key, grid, keywords, types, page, size)
        else:
            return res
    return False


def export(result, output):
    filetype = output.split(".")[-1]

    if filetype == 'csv':
        with open(output, mode="w", newline='', encoding="utf-8") as result_file:
            csv_writer = csv.writer(
                result_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(["id", "name", "type", "typecode", "address",
                                "lng", "lat", "tel", "pname", "cityname", "adname", "details"])
            for item in result:
                csv_writer.writerow([item.id, item.name, item.type, item.typecode, item.address,
                                     item.lng, item.lat, item.tel, item.pname, item.cityname, item.adname, item.details])
    elif filetype == "geojson" or filetype == "shp":
        geojson = {}
        features = []
        for item in result:
            item_obj = {"type": "Feature"}
            item_obj["properties"] = {
                "id": str(item.id),
                "name": str(item.name),
                "type": str(item.type),
                "typecode": str(item.typecode),
                "address": str(item.address),
                "tel": str(item.tel),
                "pname": str(item.pname),
                "cityname": str(item.cityname),
                "adname": str(item.adname),
                "details": str(item.details)
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
