# -*- coding: utf8 -*-
import TickerConfig
from config.urlConf import urls
from myUrllib.httpUtils import HTTPClient

PUSH_BEAR_API_PATH = "https://pushbear.ftqq.com/sub"


def send_push_bear(msg):
    """
    pushBear微信通知
    :param msg: 通知内容 content
    :return:
    """
    if TickerConfig.PUSHBEAR_CONF["is_pushbear"] and TickerConfig.PUSHBEAR_CONF["send_key"].strip() != "":
        try:
            send_push_bear_urls = urls.get("Pushbear")
            data = {
                "sendkey": TickerConfig.PUSHBEAR_CONF["send_key"].strip(),
                "text": "购票成功通知",
                "desp": msg
            }
            http_client = HTTPClient(0)
            send_push_bea_rsp = http_client.send(send_push_bear_urls, data=data)
            if send_push_bea_rsp.get("code") is 0:
                print(u"已下发 pushbear 微信通知, 请查收")
            else:
                print(send_push_bea_rsp)
        except Exception as e:
            print(u"pushbear 配置有误 {}".format(e))
    else:
        pass


if __name__ == '__main__':
    send_push_bear(1)
