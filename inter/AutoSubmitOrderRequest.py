# coding=utf-8
import urllib
from collections import OrderedDict

from config.TicketEnmu import Ticket
from inter.CheckRandCodeAnsyn import checkRandCodeAnsyn
from inter.GetQueueCountAsync import getQueueCountAsync
from inter.GetRandCode import get_rand_code
import TickerConfig


class AutoSubmitOrderRequest:
    """
    快读提交订单通道
    """
    def __init__(self, select_obj,
                 secret_str,
                 train_date,
                 query_from_station_name,
                 query_to_station_name,
                 passenger_ticket_str,
                 old_passenger_str,
                 train_no,
                 station_train_code,
                 left_ticket,
                 set_type, ):
        self.set_type = set_type
        try:
            self.secretStr = urllib.unquote(secret_str)
        except AttributeError:
            self.secretStr = urllib.parse.unquote(secret_str)
        self.train_date = train_date
        self.query_from_station_name = query_from_station_name
        self.query_to_station_name = query_to_station_name
        self.passengerTicketStr = passenger_ticket_str.rstrip("_{0}".format(self.set_type))
        self.oldPassengerStr = old_passenger_str
        self.session = select_obj
        self.train_no = train_no
        self.stationTrainCode = station_train_code
        self.leftTicket = left_ticket

    def data_par(self):
        """
        参数结构
        自动提交代码接口-autoSubmitOrderRequest
            - 字段说明
                - secretStr 车票代码
                - train_date 乘车日期
                - tour_flag 乘车类型
                - purpose_codes 学生还是成人
                - query_from_station_name 起始车站
                - query_to_station_name 结束车站
                - cancel_flag 默认2，我也不知道干嘛的
                - bed_level_order_num  000000000000000000000000000000
                - passengerTicketStr   乘客乘车代码
                - oldPassengerStr  乘客编号代码
        :return:
        """
        data = OrderedDict()
        data["secretStr"] = self.secretStr
        data["train_date"] = self.train_date
        data["tour_flag"] = "dc"
        data["purpose_codes"] = "ADULT"
        data["query_from_station_name"] = TickerConfig.FROM_STATION
        data["query_to_station_name"] = TickerConfig.TO_STATION
        data["cancel_flag"] = 2
        data["bed_level_order_num"] = "000000000000000000000000000000"
        data["passengerTicketStr"] = self.passengerTicketStr
        data["oldPassengerStr"] = self.oldPassengerStr
        return data

    def send_auto_submit_order_request(self):
        """
        请求下单接口
        :return:
        """
        urls = self.session.urls["autoSubmitOrderRequest"]
        data = self.data_par()
        auto_submit_order_request_result = self.session.httpClient.send(urls, data)
        if auto_submit_order_request_result and \
                auto_submit_order_request_result.get("status", False) and\
                auto_submit_order_request_result.get("httpstatus", False) == 200:
            request_result_data = auto_submit_order_request_result.get("data", {})
            if request_result_data:
                result = request_result_data.get("result", "")
                if_show_passcode = request_result_data.get("ifShowPassCode", "N")
                if_show_passcode_time = int(request_result_data.get("ifShowPassCodeTime", "1000")) / float(1000)
                print(Ticket.AUTO_SUBMIT_ORDER_REQUEST_C)
                g = getQueueCountAsync(session=self.session,
                                       train_no=self.train_no,
                                       stationTrainCode=self.stationTrainCode,
                                       fromStationTelecode=self.query_from_station_name,
                                       toStationTelecode=self.query_to_station_name,
                                       leftTicket=self.leftTicket,
                                       set_type=self.set_type,
                                       users=len(TickerConfig.TICKET_PEOPLES),
                                       station_dates=self.train_date,
                                       passengerTicketStr=self.passengerTicketStr,
                                       oldPassengerStr=self.oldPassengerStr,
                                       result=result,
                                       ifShowPassCodeTime=if_show_passcode_time,
                                       )
                if if_show_passcode == "Y":  # 如果需要验证码
                    print(u"需要验证码")
                    print(u"正在使用自动识别验证码功能")
                    for i in range(3):
                        rand_code = get_rand_code(is_auto_code=True, auto_code_type=2)
                        checkcode = checkRandCodeAnsyn(self.session, rand_code, "")
                        if checkcode == 'TRUE':
                            print(u"验证码通过,正在提交订单")
                            data['randCode'] = rand_code
                            break
                        else:
                            print(u"验证码有误, {0}次尝试重试".format(i + 1))
                    print(u"验证码超过限定次数3次，放弃此次订票机会!")
                g.sendGetQueueCountAsync()
        else:
            print(Ticket.AUTO_SUBMIT_ORDER_REQUEST_F)
            if auto_submit_order_request_result.get("messages", ""):
                print("".join(auto_submit_order_request_result.get("messages", "")))
            elif auto_submit_order_request_result.get("validateMessages", ""):
                print("".join(auto_submit_order_request_result.get("validateMessages", "")))
