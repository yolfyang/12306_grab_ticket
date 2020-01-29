# coding=utf-8
import json

from config.TicketEnmu import Ticket
from myException.PassengerUserException import PassengerUserException
import wrapcache
import TickerConfig


class GetPassengerDTOs:
    """
    获取乘客信息
    :return:
    """
    def __init__(self, select_obj, ticket_peoples=None, set_type=None, is_more_ticket_num=None):
        """
        :param select_obj: 登录实例
        :param ticket_peoples: 乘客
        :param set_type: 坐席
        """
        if ticket_peoples is None:
            ticket_peoples = []
        self.session = select_obj
        self.ticket_peoples = ticket_peoples
        self.is_more_ticket_num = is_more_ticket_num
        self.set_type = set_type

    def send_get_passenger_dtos(self):
        get_passenger_dt_os_result = self.session.httpClient.send(self.session.urls["get_passengerDTOs"], json.dumps({"_json_att": ""}))
        if get_passenger_dt_os_result.get("data", False) and get_passenger_dt_os_result["data"].get("normal_passengers", False):
            normal_passengers = get_passenger_dt_os_result['data']['normal_passengers']
            _normal_passenger = [normal_passengers[i] for i in range(len(normal_passengers)) if
                                 normal_passengers[i]["passenger_name"] in self.ticket_peoples]
            return _normal_passenger if _normal_passenger else [normal_passengers[0]]  # 如果配置乘车人没有在账号，则默认返回第一个用户
        else:
            if get_passenger_dt_os_result.get("data", False) and get_passenger_dt_os_result['data'].get("exMsg", False):
                print(get_passenger_dt_os_result['data'].get("exMsg", False))
            elif get_passenger_dt_os_result.get('messages', False):
                print(get_passenger_dt_os_result.get('messages', False))
            else:
                print(u"警告：您的账号可能买票有问题，获取不到联系人，请测试是否能正常下单，在捡漏或者购票！！！")
                print(u"警告：您的账号可能买票有问题，获取不到联系人，请测试是否能正常下单，在捡漏或者购票！！！")
                print(u"警告：您的账号可能买票有问题，获取不到联系人，请测试是否能正常下单，在捡漏或者购票！！！")
                # raise PassengerUserException(ticket.DTO_NOT_FOUND)

    def get_passenger_ticket_str(self, set_type):
        """
        获取getPassengerTicketStr 提交对应的代号码
        :param set_type: 坐席
        :return:
        """
        passenger_ticket_str = {
            '一等座': 'M',
            '特等座': 'P',
            '二等座': 'O',
            '商务座': 9,
            '硬座': 1,
            '无座': 1,
            '软座': 2,
            '软卧': 4,
            '硬卧': 3,
        }
        return str(passenger_ticket_str[set_type.replace(' ', '')])

    def get_passenger_ticket_strlist_and_oldpassenger_str(self, secret_str, secret_list):
        """
        获取提交车次人内容格式
        passengerTicketStr	O,0,1,文贤平,1,43052419950223XXXX,15618715583,N_O,0,1,梁敏,1,43052719920118XXXX,,N
        oldPassengerStr	文贤平,1,43052719920118XXXX,1_梁敏,1,43052719920118XXXX,1
        ps: 如果is_more_ticket打开了的话，那就是读取联系人列表里面前符合车次数量的前几个联系人
        :return:
        """
        passenger_ticket_str_list = []
        old_passenger_str = []
        tickers = []
        set_type = ""
        if wrapcache.get("user_info"):  # 如果缓存中有联系人方式，则读取缓存中的联系人
            user_info = wrapcache.get("user_info")
            print(u"使用缓存中查找的联系人信息")
        else:
            user_info = self.send_get_passenger_dtos()
            wrapcache.set("user_info", user_info, timeout=9999999)
        if not user_info:
            raise PassengerUserException(Ticket.DTO_NOT_IN_LIST)
        if len(user_info) < self.is_more_ticket_num:  # 如果乘车人填错了导致没有这个乘车人的话，可能乘车人数会小于自动乘车人
            self.is_more_ticket_num = len(user_info)
        if secret_str:
            set_type = self.get_passenger_ticket_str(self.set_type)
            if self.is_more_ticket_num is 1:
                passenger_ticket_str_list.append(
                    '0,' + user_info[0]['passenger_type'] + "," + user_info[0][
                        "passenger_name"] + "," +
                    user_info[0]['passenger_id_type_code'] + "," + user_info[0]['passenger_id_no'] + "," +
                    user_info[0]['mobile_no'] + ',N,' + user_info[0]["allEncStr"])
                old_passenger_str.append(
                    user_info[0]['passenger_name'] + "," + user_info[0]['passenger_id_type_code'] + "," +
                    user_info[0]['passenger_id_no'] + "," + user_info[0]['passenger_type'] + '_')
            else:
                for i in range(self.is_more_ticket_num):
                    passenger_ticket_str_list.append(
                        '0,' + user_info[i]['passenger_type'] + "," + user_info[i][
                            "passenger_name"] + "," + user_info[i]['passenger_id_type_code'] + "," + user_info[i][
                            'passenger_id_no'] + "," + user_info[i]['mobile_no'] + ',N,' + user_info[i]["allEncStr"] + '_' + set_type)
                    old_passenger_str.append(
                        user_info[i]['passenger_name'] + "," + user_info[i]['passenger_id_type_code'] + "," +
                        user_info[i]['passenger_id_no'] + "," + user_info[i]['passenger_type'] + '_')
        elif secret_list:
            """
            候补订单有多少个联系人，就候补多少个联系人了，没有优先提交之说
            1#XXXX#1#***************77X#bf6ae40d3655ae7eff005ee21d95876b38ab97a8031b464bc2f74a067e3ec957;
            """
            for user in user_info:
                tickers.append(f"1#{user['passenger_name']}#1#{user['passenger_id_no']}#{user['allEncStr']};")

        return {
            "passengerTicketStrList": set_type + "," + ",".join(passenger_ticket_str_list),
            "passengerTicketStrByAfterLate": "".join(tickers),
            "oldPassengerStr": "".join(old_passenger_str),
            "code": Ticket.SUCCESS_CODE,
            "set_type": set_type,
            "status": True,
            "user_info": user_info,
        }
