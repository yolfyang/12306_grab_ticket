# -*- coding=utf-8 -*-
import datetime
import operator
import os
from os.path import dirname
import requests
from config import urlConf
import threading
from config.urlConf import urls
from myUrllib.httpUtils import HTTPClient

cdn_list = []


class CDNProxy(threading.Thread):
    """
    对CDN进行处理的模块
    """

    def __init__(self, cdns):
        super().__init__()
        self.cdns = cdns
        self.urlConf = urlConf.urls
        self.httpClient = requests
        self.city_list = []
        self.timeout = 5

    def run(self):
        for cdn in self.cdns:
            http = HTTPClient(0)
            url = urls["loginInitCdn"]
            http._cdn = cdn.replace("\n", "")
            start_time = datetime.datetime.now()
            rep = http.send(url)
            ret_time = (datetime.datetime.now() - start_time).microseconds / 1000
            if rep and "message" not in rep and ret_time < 3000:
                if cdn.replace("\n", "") not in cdn_list:  # 如果有重复的cdn，则放弃加入
                    print(f"加入cdn: {cdn}")
                    cdn_list.append({"ip": cdn.replace("\n", ""), "time": ret_time})


def open_cdn_file(cdn_file):
    cdn = []
    path_now = dirname(__file__)
    path = os.path.join(dirname(path_now), cdn_file)
    # path = os.path.join(os.path.dirname(__file__), f'../{cdn_file}')    #此句windows不能正常工作
    # noinspection PyBroadException
    try:
        with open(path, "r", encoding="utf-8") as f:
            for i in f.readlines():
                if i and "kyfw.12306.cn:443" not in i:
                    cdn.append(i.replace("\n", ""))
        return cdn
    except Exception:
        with open(path, "r") as f:
            for i in f.readlines():
                if i and "kyfw.12306.cn:443" not in i:
                    cdn.append(i.replace("\n", ""))
        return cdn


def sort_cdn():
    """
    对cdn进行排序
    :return:
    """
    ips = []
    cs = sorted(cdn_list, key=operator.itemgetter('time'))
    for c in cs:
        print(f"当前ip: {c['ip']}, 延时: {c['time']}")
        ips.append(c["ip"])
    return ips


def filter_cdn():
    """
    过滤cdn, 过滤逻辑为当前cdn响应值小于1000毫秒
    过滤日志:
        加入cdn: 116.77.75.146
    :return:
    """
    cdns = open_cdn_file("cdn_list")
    cdnss = [cdns[i:i + 50] for i in range(0, len(cdns), 50)]
    cdn_thread = []
    for cdn in cdnss:
        t = CDNProxy(cdn)
        cdn_thread.append(t)
    for cdn_t in cdn_thread:
        cdn_t.start()
    for cdn_j in cdn_thread:
        cdn_j.join()

    print(f"当前有效cdn个数为: {len(cdn_list)}")
    if cdn_list:
        ips = sort_cdn()
        path = os.path.join(dirname(dirname(__file__)), 'filter_cdn_list')
        f = open(path, "a+")
        f.seek(0)
        f.truncate()
        f.writelines("")
        for ip in ips:
            f.writelines(f"{ip}\n")
        f.close()


if __name__ == '__main__':
    filter_cdn()
