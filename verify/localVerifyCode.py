# coding: utf-8
import time

import TickerConfig
from verify.login_and_get_cookies_with_selenium import Login

import base64
import os
from os.path import dirname
import cv2
import numpy as np
from tensorflow import keras
import tensorflow as tf
from verify import pretreatment
from verify.mlearn_for_image import preprocess_input

graph = tf.get_default_graph()
PATH = lambda p: os.path.abspath(os.path.join(dirname(dirname(__file__)), p))
TEXT_MODEL = ""
IMG_MODEL = ""


def get_text(img, offset=0):
    text = pretreatment.get_text(img, offset)
    text = cv2.cvtColor(text, cv2.COLOR_BGR2GRAY)
    cv2.imshow("text", text)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()
    text = text / 255.0
    h, w = text.shape
    text.shape = (1, h, w, 1)
    return text


def base64_to_image(base64_code):
    # base64解码
    img_data = base64.b64decode(base64_code)
    # 转换为np数组
    img_array = np.fromstring(img_data, np.uint8)
    # 转换成opencv可用格式
    img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)
    cv2.imshow("randcode", img)
    cv2.waitKey(3000)
    # cv2.destroyAllWindows()
    return img


class Verify:
    def __init__(self):
        self.textModel = ""
        self.imgModel = ""
        self.load_img_model()
        self.load_text_model()

    def load_text_model(self):
        if not self.textModel:
            self.textModel = keras.models.load_model(PATH('model.v2.0.h5'))
        else:
            print("无需加载模型model.v2.0.h5")

    def load_img_model(self):
        if not self.imgModel:
            self.imgModel = keras.models.load_model(PATH('12306.image.model.h5'))

    def verify(self, fn):
        verify_titles = ['打字机', '调色板', '跑步机', '毛线', '老虎', '安全帽', '沙包', '盘子', '本子', '药片', '双面胶', '龙舟', '红酒', '拖把', '卷尺',
                         '海苔', '红豆', '黑板', '热水袋', '烛台', '钟表', '路灯', '沙拉', '海报', '公交卡', '樱桃', '创可贴', '牌坊', '苍蝇拍', '高压锅',
                         '电线', '网球拍', '海鸥', '风铃', '订书机', '冰箱', '话梅', '排风机', '锅铲', '绿豆', '航母', '电子秤', '红枣', '金字塔', '鞭炮',
                         '菠萝', '开瓶器', '电饭煲', '仪表盘', '棉棒', '篮球', '狮子', '蚂蚁', '蜡烛', '茶盅', '印章', '茶几', '啤酒', '档案袋', '挂钟', '刺绣',
                         '铃铛', '护腕', '手掌印', '锦旗', '文具盒', '辣椒酱', '耳塞', '中国结', '蜥蜴', '剪纸', '漏斗', '锣', '蒸笼', '珊瑚', '雨靴', '薯条',
                         '蜜蜂', '日历', '口哨']
        # 读取并预处理验证码
        img = base64_to_image(fn)
        text = get_text(img)
        imgs = np.array(list(pretreatment.get_imgs(img)))
        imgs = preprocess_input(imgs)
        text_list = []
        # 识别文字
        self.load_text_model()
        global graph
        with graph.as_default():
            label = self.textModel.predict(text)
        label = label.argmax()
        text = verify_titles[label]
        text_list.append(text)
        # 有可能是两个词
        # 获取下一个词
        # 根据第一个词的长度来定位第二个词的位置
        if len(text) == 1:
            offset = 27
        elif len(text) == 2:
            offset = 47
        else:
            offset = 60
        text = get_text(img, offset=offset)
        if text.mean() < 0.95:
            with graph.as_default():
                label = self.textModel.predict(text)
            label = label.argmax()
            text = verify_titles[label]
            text_list.append(text)
        print("题目为{}".format(text_list))
        # 加载图片分类器
        self.load_img_model()
        with graph.as_default():
            labels = self.imgModel.predict(imgs)
        labels = labels.argmax(axis=1)
        results = []
        for pos, label in enumerate(labels):
            label = verify_titles[label]
            print(pos + 1, label)
            if label in text_list:
                results.append(str(pos + 1))
        cv2.imshow("temp", img)
        cv2.waitKey(8000)
        cv2.destroyAllWindows()
        return results


def img_from_file_base64():
    """
    从硬盘读取文件并转换为base64格式
    :return:
    """
    with open("tkcode.png", "rb") as f:
        # b64encode是编码，b64decode是解码
        base64_data = base64.b64encode(f.read())
        # base64.b64decode(base64data)
        print(base64_data)
    return base64_data


if __name__ == '__main__':
    v = Verify()
    """
    a = Login('https://kyfw.12306.cn/otn/resources/login.html', '12306账号', '密码')
    a.login()
    time.sleep(2)
    im = a.get_pic()
    """
    import random
    import requests
    while True:
        url = "https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sjrand&{0}&callback=jQuery19108016482864806321_1554298927290&_=1554298927293"
        url = url.format(random.random())
        r = requests.get(url)
        img = eval(r.content.decode().split("(")[1].split(")")[0]).get("image")
        v.verify(img)
