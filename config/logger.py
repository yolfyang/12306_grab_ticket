# coding: utf-8

import os
import time
import logging

from config import configCommon

logger = None
loggerHandler = None
dateStr = ''  # 默认拥有日期后缀
suffix = ''   # 除了日期外的后缀


def set_suffix(s):
	global suffix
	suffix = s


def get_today_date_str():
	return time.strftime("%Y-%m-%d", time.localtime(configCommon.get_now_time_stamp()))


def set_date_str(s):
	global dateStr
	dateStr = s


def is_another_day(s):
	global dateStr
	return dateStr != s


def get_log_file():
	global dateStr, suffix
	rtn = os.path.join(configCommon.get_log_dir(), dateStr)
	if suffix:
		rtn += "_" + suffix
	return rtn + ".log"


def log(msg, func="info"):
	global logger, loggerHandler
	if not logger:
		logger = logging.getLogger()
		logger.setLevel(logging.INFO)
	if not loggerHandler:
		loggerHandler = logging.FileHandler(get_log_file())
	today_str = get_today_date_str()
	if is_another_day(today_str):
		set_date_str(today_str)
		logger.removeHandler(loggerHandler)
		fh = logging.FileHandler(get_log_file())
		fm = logging.Formatter(u'[%(asctime)s][%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)')
		fh.setFormatter(fm)
		logger.addHandler(fh)
	levels = {
		"debug": logger.debug,
		"info": logger.info,
		"warning": logger.warning,
		"error": logger.error,
		"critical": logger.critical
	}
	levels[func](msg)


if __name__ == "__main__":
	log("test")
