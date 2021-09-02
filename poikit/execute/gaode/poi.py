# -- coding: utf-8 --
from poikit.model.gaode.rect import Rect
import re
import poikit.repository.gaode.poi as poi_repo
import poikit.model.gaode.poi as poi
import concurrent.futures
import threading
import time

# 线程锁
lock = threading.Lock()


def execute(keys, rect, keywords, types, threshold, thread_num, qps, output):
    _keys = list(filter(check_key, keys))  # 所有合法key
    print(_keys)
    if not check_rect(rect):
        print("{} 格式错误，请检查".format(rect))
        return
    _per_execute_time = per_execute_time(len(_keys), thread_num, qps) / 1000

    # 1. 网格剖分
    grids = []
    initial_pois = []
    generate_grids(grids, initial_pois,
                   keys[0], rect, keywords, types, threshold)

    # 2. 开始爬取
    result = []
    for i in range(0, len(grids)):
        result.extend(get_poi(keys, grids[i], initial_pois[i],
                              _per_execute_time, thread_num, keywords, types))

    print("该区域共有POI数据：{}条".format(len(result)))
    for r in result:
        print(r)


def check_key(key):
    rexp = r'^[a-zA-Z0-9]+$'
    return True if re.match(rexp, key) else False


def check_rect(rect):
    return between(rect.top, -90, 90) and between(rect.bottom, -90, rect.top) and between(rect.right, -180, 180) and between(rect.left, -180, rect.right)


def per_execute_time(key_num, thread_num, qps):
    return 1000 * thread_num / qps * key_num


def generate_grids(grids, initial_pois, key, rect, keywords, types, threshold):
    page = 1
    size = 20
    res = poi_repo.get_poi_by_polygon(
        poi.Request(key, rect, keywords, types), page, size)
    if not res or res.count == 0:
        return

    if res.count > threshold:
        child_width = (rect.right - rect.left) / 2
        child_height = (rect.top - rect.bottom) / 2

        for i in range(2):
            for j in range(2):
                generate_grids(grids, initial_pois, Rect(rect.bottom + (j + 1) * child_height,
                                                         rect.left +
                                                         (i + 1) * child_width,
                                                         rect.bottom + j * child_height,
                                                         rect.left + i * child_width),
                               keywords, types, threshold)
    else:
        grids.append(rect)
        initial_pois.append(res)


def get_poi(keys, grid, initial_poi, per_execute_time, thread_num, keywords, types):
    result = initial_poi.pois
    total = initial_poi.count
    size = 20
    task_num = int(total / size) + 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
        results = [executor.submit(per_poi_task, keys=keys, per_execute_time=per_execute_time,
                                   grid=grid, keywords=keywords, types=types, page=page, size=size) for page in range(2, task_num + 1)]

        for f in concurrent.futures.as_completed(results):
            item_result = f.result()
            if item_result:
                result.extend(item_result.pois)
    return result


def per_poi_task(keys, per_execute_time, grid, keywords, types, page, size):
    start = time_ms()
    key = get_key(keys)

    if not key:
        return False

    res = poi_repo.get_poi_by_polygon(
        poi.Request(key, grid, keywords, types), page, size)

    if not res or res.infocode != '10000':
        with lock:
            if key in keys:
                res = retry(key, grid, keywords, types, page, size)
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
                    poi.Request(key, grid, keywords, types), page, size)

                if not res or res.infocode != '10000':
                    res = retry(key, grid, keywords, types, page, size)
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
    end = time_ms()
    if(end - start < per_execute_time):
        time.sleep(per_execute_time)

    return res


def get_key(keys):
    if len(keys) == 0:
        return False
    key = keys.pop()
    keys.insert(0, key)
    return key


def retry(key, grid, keywords, types, page, size):
    for _ in range(3):
        res = poi_repo.get_poi_by_polygon(
            poi.Request(key, grid, keywords, types), page, size)
        if not res or res.infocode != '10000':
            retry(key, grid, keywords, types, page, size)
        else:
            return res
    return False


def time_ms():
    return int((round(time.time())))


def between(num, start, end):
    return num >= start and num <= end
