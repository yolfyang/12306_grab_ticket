#!/usr/bin/env python
# coding:utf-8
from selenium import webdriver
import time
import requests
from hashlib import md5
import re
import base64
from selenium.webdriver.common.action_chains import ActionChains
import cv2
import numpy as np


class ChaojiyingClient(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password = password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def post_pic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        return r.json()

    def report_error(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


class Login:
    def __init__(self, url, username, passwd):
        self.url = url
        self.username = username
        self.passwd = passwd

    def login(self):
        self.browser = webdriver.Chrome()
        self.browser.get(self.url)
        time.sleep(2)
        login_select = self.browser.find_element_by_class_name('login-hd-account')
        login_select.click()
        user = self.browser.find_element_by_id('J-userName')
        word = self.browser.find_element_by_id('J-password')
        user.send_keys(self.username)
        word.send_keys(self.passwd)

    def get_pic(self):
        tag = self.browser.find_element_by_class_name('imgCode')
        temp = tag.get_attribute('src')
        b64_pic = re.sub(r'data:image/jpg;base64,', '', temp)
        # pic = base64.b64decode(b64_pic)
        self.browser.quit()
        return b64_pic

    def click(self, j):
        temp = j.get('pic_str')
        locations = [list(map(int, i.split(','))) for i in temp.split('|')]    # [[11, 22], [33, 44]]
        for location in locations:
            ActionChains(self.browser).move_to_element_with_offset(self.browser.find_element_by_class_name('imgCode'),
                                                                   location[0], location[1]).click().perform()
            time.sleep(1)
        self.browser.find_element_by_id('J-login').click()

    def get_cookies(self):
        return self.browser.get_cookies()


def show_pic(img):
    cv2.imshow("test", img)
    cv2.waitKey(5000)
    cv2.destroyAllWindows()


def img_from_file_base64():
    with open("../tkcode.png", "rb") as f:
        # b64encode是编码，b64decode是解码
        base64_data = base64.b64encode(f.read())
        # base64.b64decode(base64data)
        print(base64_data)
    return base64_data


def base64_to_mat(base64_data):
    img_data = base64.b64decode(base64_data)
    nparr = np.fromstring(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def mat_to_base64(img):
    img_encode = cv2.imencode('.png', img)[1]
    data_encode = np.array(img_encode)
    str_encode = data_encode.tostring()
    print(base64.b64encode(str_encode))
    return base64.b64encode(str_encode)


if __name__ == '__main__':
    a = Login('https://kyfw.12306.cn/otn/resources/login.html', '12306账号', '密码')
    a.login()
    time.sleep(2)
    im = a.get_pic()												# 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
    img_np = base64_to_mat(im)
    show_pic(img_np)
    chaojiying = ChaojiyingClient('超级鹰账号', '密码', '软件id')  # 用户中心>>软件ID 生成一个替换 96001
    z = chaojiying.post_pic(im, 9004)
    print(z)
    a.click(z)	  								# 1902 验证码类型  官方网站>>价格体系 3.4+版 print 后要加()
    print(a.get_cookies())
