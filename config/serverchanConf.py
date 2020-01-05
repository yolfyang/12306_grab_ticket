# -*- coding: utf8 -*-
import TickerConfig
from config.urlConf import urls
from myUrllib.httpUtils import HTTPClient

PUSH_SERVER_CHAN_PATH = "https://sc.ftqq.com"


def send_server_chan(msg):
    """
    pushBear微信通知
    :param msg: 通知内容 content
    :return:
    """
    if (
        TickerConfig.SERVER_CHAN_CONF["is_server_chan"]
        and TickerConfig.SERVER_CHAN_CONF["secret"].strip() != ""
    ):
        try:
            secret = TickerConfig.SERVER_CHAN_CONF["secret"].strip()
            send_server_chan_urls = urls.get("ServerChan")
            send_server_chan_urls["req_url"] += f'{secret}.send'

            params = {"text": "购票成功通知", "desp": msg}
            http_client = HTTPClient(0)
            send_server_chan_rsp = http_client.send(send_server_chan_urls, params=params)
            if send_server_chan_rsp.get("errno") == 0:
                print(u"已下发 Server酱 微信通知, 请查收")
            else:
                print(send_server_chan_rsp)
        except Exception as e:
            print(u"Server酱 配置有误 {}".format(e))


if __name__ == "__main__":
    send_server_chan(1)
