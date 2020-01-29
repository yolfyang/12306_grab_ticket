# coding=utf-8
from config.urlConf import urls


def login_aysn_suggest(session, username, password):
    """
    登录接口
    ps: 不需要验证码
    :return:
    """
    login_aysn_suggest_urls = urls.get("loginAysnSuggest")
    data = {
        "loginUserDTO.user_name": username,
        "userDTO.password":	password
    }
    login_aysn_suggest_rsp = session.httpClient.send(urls=login_aysn_suggest_urls, data=data)
    if login_aysn_suggest_rsp and login_aysn_suggest_rsp.get("httpstatus") is 200 and login_aysn_suggest_rsp.get("data", {}).get("loginCheck") == "Y":
        print(u"登录成功")
    else:
        print(u"登录失败, {0} {1}".format("".join(login_aysn_suggest_rsp.get("messages")), login_aysn_suggest_rsp.get("validateMessages")))
