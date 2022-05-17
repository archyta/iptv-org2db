import re

import requests
import json
import time
from pymongo import MongoClient

API_SERVER = 'https://iptv-org.github.io/api/'

PROXIES = {
    'http': 'http://192.168.31.98:2080',
    'https': 'http://192.168.31.98:2080',
}

session = MongoClient('mongodb://192.168.31.98:32768/')
db = session["IPTV"]


def query_data(url):
    result = {}
    try:
        response = requests.get(url, proxies=PROXIES)
        result = json.loads(response.text)
    except Exception as e:
        print("faild query from iptv-org.github.io::", e)
    return result


def update_data(records, collection, keys=[]):
    table = db[collection]
    arr = []  # 初始化一个空列表
    cnt = table.count_documents({})
    if len(records) > 0:
        if cnt == 0:  # 如果是空表，则用批插入
            i = 0
            for it in records:
                now = int(time.time())
                it["updated"] = now
                arr.append(it)
                i += 1
                if i % 2000 == 0:  # 每次批量插入的数量，2000条插入一次
                    try:
                        table.insert_many(arr)
                    except Exception as e:
                        print("an exception while updated data ::", e)
                    arr = []
                else:
                    continue
            try:
                table.insert_many(arr)  # 余下的一次性插入
            except Exception as e:
                print("an exception while updated channels ::", e)
        else:  # 非空表，一次一条插入
            for it in records:
                now = int(time.time())
                it["updated"] = now
                # q = {"channel": it.get("channel", "")}
                q = {x: it.get(x, "") for x in keys}
                try:
                    record = table.find_one_and_update(q, update={"$set": it}, upsert=True)
                except Exception as e:
                    print("an exception while updated data ::", e)


def query_test(collection, cond):
    table = db[channels]
    record = table.find({"name": {"$regex": "^'{0}'".format('CCTV')}})
    for r in record:
        print(r)


if __name__ == '__main__':
    # query_test()

    res = query_data(API_SERVER + 'guides.json')
    update_data(res, collection="guides", keys=["channel", "site", "lang"])

    res = query_data(API_SERVER + 'categories.json')
    update_data(res, collection="categories", keys=["id"])

    res = query_data(API_SERVER + 'languages.json')
    update_data(res, collection="languages", keys=["code"])

    res = query_data(API_SERVER + 'countries.json')
    update_data(res, collection="countries", keys=["code", "lang"])

    res = query_data(API_SERVER + 'subdivisions.json')
    update_data(res, collection="subdivisions", keys=["code", "country"])

    res = query_data(API_SERVER + 'regions.json')
    update_data(res, collection="regions", keys=["code"])

    res = query_data(API_SERVER + 'streams.json')
    update_data(res, collection="streams", keys=["channel", "url"])

    res = query_data(API_SERVER + 'channels.json')
    update_data(res, collection="channels", keys=["id", "country"])

    # BLOCKLIST_API = API_SERVER + 'blocklist.json'
