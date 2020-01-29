# coding=utf-8
import base64
import copy
import random


def get_passcode_neworder_and_login(session, img_type):
    """
    下载验证码
    :param session:
    :param img_type: 下载验证码类型，login=登录验证码，其余为订单验证码
    :return:
    """
    if img_type == "login":
        code_img_url = copy.deepcopy(session.urls["getCodeImg"])
        code_img_url["req_url"] = code_img_url["req_url"].format(random.random())
    else:
        code_img_url = copy.deepcopy(session.urls["codeImgByOrder"])
        code_img_url["req_url"] = code_img_url["req_url"].format(random.random())
    print(u"下载验证码...")
    img_path = './tkcode.png'
    result = session.httpClient.send(code_img_url)
    try:
        if isinstance(result, dict):
            print(u"下载验证码失败, 请手动检查是否ip被封，或者重试，请求地址：https://kyfw.12306.cn{}".format(code_img_url.get("req_url")))
            return False
        else:
            print(u"下载验证码成功")
            # noinspection PyBroadException
            try:
                with open(img_path, 'wb', encoding="utf-8") as img:
                    img.write(result)
            except Exception:
                with open(img_path, 'wb') as img:
                    img.write(result)
            return result
    except OSError:
        print(u"验证码下载失败，可能ip被封，确认请手动请求: {0}".format(code_img_url))


def get_passcode_neworder_and_login1(session, img_type):
    """
    获取验证码2
    :param session:
    :param img_type:
    :return:
    """
    if img_type == "login":
        code_img_url = copy.deepcopy(session.urls["getCodeImg1"])
        code_img_url["req_url"] = code_img_url["req_url"].format(random.random())
    else:
        code_img_url = copy.deepcopy(session.urls["codeImgByOrder"])
        code_img_url["req_url"] = code_img_url["req_url"].format(random.random())
    print(u"下载验证码...")
    img_path = './tkcode.png'
    code_img_url_rsp = session.httpClient.send(code_img_url)
    if not isinstance(code_img_url_rsp, str):
        print("验证码获取失败")
        return
    result = eval(code_img_url_rsp.split("(")[1].split(")")[0]).get("image")
    try:
        if isinstance(result, dict):
            print(u"下载验证码失败, 请手动检查是否ip被封，或者重试，请求地址：https://kyfw.12306.cn{}".format(code_img_url.get("req_url")))
            return False
        else:
            print(u"下载验证码成功")
            # noinspection PyBroadException
            try:
                with open(img_path, 'wb', encoding="utf-8") as img:
                    img.write(result)
            except Exception:
                with open(img_path, 'wb') as img:
                    img.write(base64.b64decode(result))
            return result
    except OSError:
        print(u"验证码下载失败，可能ip被封或者文件写入没权限")


if __name__ == '__main__':
    pass
