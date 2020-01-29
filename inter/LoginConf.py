# coding=utf-8
from config.urlConf import urls


def login_conf(session):
    """
    判断登录是否需要验证码
    :param session:
    :return:
    """
    login_conf_url = urls.get("loginConf")
    login_conf_rsp = session.httpClient.send(urls=login_conf_url, data={})
    if login_conf_rsp and login_conf_rsp.get("data", {}).get("is_login_passCode") == "N":
        print(u"不需要验证码")
        return False
    else:
        print(u"需要验证码")
        return True


if __name__ == '__main__':
    pass
