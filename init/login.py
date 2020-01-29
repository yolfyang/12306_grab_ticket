# -*- coding=utf-8 -*-
import copy
import time
from collections import OrderedDict
from time import sleep
import TickerConfig
from inter.GetPassCodeNewOrderAndLogin import get_passcode_neworder_and_login1
from inter.GetRandCode import get_rand_code
from inter.LoginAysnSuggest import login_aysn_suggest
from inter.LoginConf import login_conf
from myException.UserPasswordException import UserPasswordException


class GoLogin:
    def __init__(self, session, is_auto_code, auto_code_type):
        self.session = session
        self.randCode = ""
        self.is_auto_code = is_auto_code
        self.auto_code_type = auto_code_type

    def auth(self):
        """
        :return:
        """
        self.session.httpClient.send(self.session.urls["loginInitCdn1"])
        uamtk_static_url = self.session.urls["uamtk-static"]
        uamtk_static_data = {"appid": "otn"}
        result = self.session.httpClient.send(uamtk_static_url, uamtk_static_data)
        return result

    def code_check(self):
        """
        验证码校验
        :return:
        """
        code_check_url = copy.deepcopy(self.session.urls["codeCheck1"])
        code_check_url["req_url"] = code_check_url["req_url"].format(self.randCode, int(time.time() * 1000))
        fresult = self.session.httpClient.send(code_check_url)
        if not isinstance(fresult, str):
            print("登录失败")
            return
        fresult = eval(fresult.split("(")[1].split(")")[0])
        if "result_code" in fresult and fresult["result_code"] == "4":
            print(u"验证码通过,开始登录..")
            return True
        else:
            if "result_message" in fresult:
                print(fresult["result_message"])
            sleep(1)
            self.session.httpClient.del_cookies()

    def base_login(self, user, passwd):
        """
        登录过程
        :param user:
        :param passwd:
        :return: 权限校验码
        """
        logurl = self.session.urls["login"]

        login_data = OrderedDict()
        login_data["username"] = user,
        login_data["password"] = passwd,
        login_data["appid"] = "otn",
        login_data["answer"] = self.randCode,

        tresult = self.session.httpClient.send(logurl, login_data)
        if 'result_code' in tresult and tresult["result_code"] == 0:
            print(u"登录成功")
            tk = self.auth()
            if "newapptk" in tk and tk["newapptk"]:
                return tk["newapptk"]
            else:
                return False
        elif 'result_message' in tresult and tresult['result_message']:
            messages = tresult['result_message']
            if messages.find(u"密码输入错误") is not -1:
                raise UserPasswordException("{0}".format(messages))
            else:
                print(u"登录失败: {0}".format(messages))
                print(u"尝试重新登陆")
                return False
        else:
            return False

    def get_user_name(self, uamtk):
        """
        登录成功后,显示用户名
        :return:
        """
        if not uamtk:
            return u"权限校验码不能为空"
        else:
            uamauthclient_url = self.session.urls["uamauthclient"]
            data = {"tk": uamtk}
            uamauthclient_result = self.session.httpClient.send(uamauthclient_url, data)
            if uamauthclient_result:
                if "result_code" in uamauthclient_result and uamauthclient_result["result_code"] == 0:
                    print(u"欢迎 {} 登录".format(uamauthclient_result["username"]))
                    return True
                else:
                    return False
            else:
                self.session.httpClient.send(uamauthclient_url, data)
                url = self.session.urls["getUserInfo"]
                self.session.httpClient.send(url)

    def go_login(self):
        """
        登陆
        :return:
        """
        user, passwd = TickerConfig.USER, TickerConfig.PWD
        if not user or not passwd:
            raise UserPasswordException(u"温馨提示: 用户名或者密码为空，请仔细检查")
        login_num = 0
        while True:
            if login_conf(self.session):
                result = get_passcode_neworder_and_login1(session=self.session, img_type="login")
                if not result:
                    continue
                self.randCode = get_rand_code(self.is_auto_code, self.auto_code_type, result)
                print(self.randCode)
                login_num += 1
                self.auth()
                if self.code_check():
                    uamtk = self.base_login(user, passwd)
                    if uamtk:
                        self.get_user_name(uamtk)
                        break
            else:
                login_aysn_suggest(self.session, username=user, password=passwd)
                login_num += 1
                break
