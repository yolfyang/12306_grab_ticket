# -*- coding: utf-8 -*-
import datetime
import os
import random
import sys
import time

from myException.ticketConfigException import ticketConfigException

rushRefreshMinTimeIntval = 2000
rushRefreshMaxTimeIntval = 3600000
rushRefreshTimeIntval = 100
# 最早运行时刻
maxRunTime = 6
# 程序停止时刻
maxRunStopTime = 23
# 可售天数
maxDate = 29

RS_SUC = 0
RS_TIMEOUT = 1
RS_JSON_ERROR = 2
RS_OTHER_ERROR = 3

seat_conf = {'商务座': 32,
             '一等座': 31,
             '二等座': 30,
             '特等座': 25,
             '软卧': 23,
             '硬卧': 28,
             '软座': 24,
             '硬座': 29,
             '无座': 26,
             '动卧': 33,
             }
if sys.version_info.major == 2:
    seat_conf_2 = dict([(v, k) for (k, v) in seat_conf.iteritems()])
else:
    seat_conf_2 = dict([(v, k) for (k, v) in seat_conf.items()])


def get_now_time_stamp():
    return time.time()


def dec_make_dir(func):
    def handle_func(*args, **kwargs):
        dirname = func(*args, **kwargs)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        elif not os.path.isdir(dirname):
            pass
        return dirname
    return func


def get_work_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#
# def fileOpen(path):
#     """
#     文件读取兼容2和3
#     :param path: 文件读取路径
#     :return:
#     """
#     try:
#         with open(path, "r", ) as f:
#             return f
#     except TypeError:
#         with open(path, "r", ) as f:
#             return f


@dec_make_dir
def get_tmp_dir():
    return os.path.join(get_work_dir(), "tmp")


@dec_make_dir
def get_log_dir():
    return os.path.join(get_tmp_dir(), "log")


@dec_make_dir
def get_cache_dir():
    return os.path.join(get_tmp_dir(), "cache")


@dec_make_dir
def get_vcode_dir():
    return os.path.join(get_tmp_dir(), "vcode")


def get_vcode_image_file(image_name):
    return os.path.join(get_vcode_dir(), image_name + ".jpg")


def get_cache_file(cache_type):
    return os.path.join(get_cache_dir(), cache_type + ".cache")


def check_sleep_time(session):
    now = datetime.datetime.now()
    if now.hour >= maxRunStopTime or now.hour < maxRunTime:
        print(u"12306休息时间，本程序自动停止,明天早上六点将自动运行")
        open_time = datetime.datetime(now.year, now.month, now.day, maxRunTime)
        if open_time < now:
            open_time += datetime.timedelta(1)
        time.sleep((open_time - now).seconds + round(random.uniform(1, 10)))
        session.call_login()


def check_date(station_dates):
    """
    检查日期是否合法
    :param station_dates:
    :return:
    """
    today = datetime.datetime.now()
    max_day = (today + datetime.timedelta(maxDate)).strftime("%Y-%m-%d")
    for station_date in station_dates[::-1]:
        date = datetime.datetime.strftime(datetime.datetime.strptime(station_date, "%Y-%m-%d"), "%Y-%m-%d")
        if date < today.strftime("%Y-%m-%d") or date > max_day:
            print(u"警告：当前时间配置有小于当前时间或者大于最大时间: {}, 已自动忽略".format(station_date))
            station_dates.remove(station_date)
            if not station_dates:
                print(u"当前日期设置无符合查询条件的，已被全部删除，请查证后添加!!!")
                raise ticketConfigException(u"当前日期设置无符合查询条件的，已被全部删除，请查证后添加!!!")
        else:
            station_dates[station_dates.index(station_date)] = date
    return station_dates
