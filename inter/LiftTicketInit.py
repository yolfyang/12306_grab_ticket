# coding=utf-8
import re


class LeftTicketInit:
    def __init__(self, session):
        self.session = session

    def req_left_ticket_init(self):
        """
        请求抢票页面
        :return:
        """
        urls = self.session.urls["left_ticket_init"]
        # 获取初始化的结果
        result = self.session.httpClient.send(urls)
        # 用正则表达式查出CLeftTicketUrl的值
        # print(result)
        match_obj = re.search('var CLeftTicketUrl = \'(.*)\'', result, re.M | re.I)
        if match_obj:
            # 如果有值，替换queryUrl
            self.session.queryUrl = match_obj.group(1)
        return {
            "status": True
        }
