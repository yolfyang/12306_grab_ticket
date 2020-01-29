#! env python
# coding: utf-8
# 功能：对图像进行预处理，将文字部分单独提取出来
# 并存放到ocr目录下
# 文件名为原验证码文件的文件名
import random
import base64

import TickerConfig

import hashlib
import os
import pathlib

import cv2
import numpy as np
import requests
import scipy.fftpack


PATH = 'imgs'


def download_image():
    # 抓取验证码
    # 存放到指定path下
    # 文件名为图像的MD5
    # url = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=login&rand=sjrand'
    url = "https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sjrand&{0}&callback=jQuery19108016482864806321_1554298927290&_=1554298927293"
    url = url.format(random.random())
    r = requests.get(url)
    fn = hashlib.md5(r.content).hexdigest()
    result = eval(r.content.decode().split("(")[1].split(")")[0]).get("image")
    img = base64.b64decode(result)
    nparr = np.fromstring(img, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # show_img(img)
    with open(f'{PATH}/{fn}.jpg', 'wb') as fp:
        fp.write(img)
    return img


def download_images():
    pathlib.Path(PATH).mkdir(exist_ok=True)
    for idx in range(40000):
        download_image()
        print(idx)


def get_text(img, offset=0):
    # 得到图像中的文本部分
    return img[3:22, 120 + offset:177 + offset]


def avhash(im):
    im = cv2.resize(im, (8, 8), interpolation=cv2.INTER_CUBIC)
    avg = im.mean()
    im = im > avg
    im = np.packbits(im)
    return im


def phash(im):
    """
    phash全称是感知哈希算法（Perceptual hash algorithm），使用这玩意儿可以对每个图片生成一个值，
    如两个图分别是2582314446007581403 与 2582314446141799129 （转为二进制再比较），
    然后计算他们的hamming distance，简单的说就是数一数二进制之后有几位不同。
    整个处理流程有点像对文章去重时先算simhash再算hamming distance，很多东西都可以直接套用过来。
    phash具体的实现可以很多地方都有了，可以搜到很多差不多的内容，在这我也就简单的记录下:
    1)缩小尺寸 为了后边的步骤计算简单些
    2)简化色彩 将图片转化成灰度图像，进一步简化计算量
    3)计算DCT 计算图片的DCT变换，得到32*32的DCT系数矩阵。
    4)缩小DCT 虽然DCT的结果是32*32大小的矩阵，但我们只要保留左上角的8*8的矩阵，这部分呈现了图片中的最低频率。
    5)计算平均值 如同均值哈希一样，计算DCT的均值。
    6)计算hash值 根据8*8的DCT矩阵，设置0或1的64位的hash值，大于等于DCT均值的设为”1”，小于DCT均值的设为“0”。
    组合在一起，就构成了一个64位的整数，这就是这张图片的指纹。
    """
    im = cv2.resize(im, (32, 32), interpolation=cv2.INTER_CUBIC)
    show_img(im)
    im = scipy.fftpack.dct(scipy.fftpack.dct(im, axis=0), axis=1)
    im = im[:8, :8]
    med = np.median(im)
    im = im > med
    im = np.packbits(im)
    return im


def show_img(img):
    cv2.imshow("temp", img)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()


def _get_imgs(img):
    interval = 5
    length = 67
    for x in range(40, img.shape[0] - length, interval + length):
        for y in range(interval, img.shape[1] - length, interval + length):
            yield img[x:x + length, y:y + length]


def get_imgs(img):
    imgs = []
    for img in _get_imgs(img):
        # show_img(img)
        imgs.append(img)
        # imgs.append(phash(img))
    return imgs


def pretreat():
    if not os.path.isdir(PATH):
        download_images()
    texts, imgs = [], []
    for img in os.listdir(PATH):
        img = os.path.join(PATH, img)
        img = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
        texts.append(get_text(img))
        imgs.append(get_imgs(img))
    return texts, imgs


def load_data(path='data.npz'):
    if not os.path.isfile(path):
        texts, imgs = pretreat()
        np.savez(path, texts=texts, images=imgs)
    f = np.load(path)
    return f['texts'], f['images']


if __name__ == '__main__':
    texts, imgs = load_data()
    print(texts.shape)
    print(imgs.shape)
    imgs = imgs.reshape(-1, 8)
    print(np.unique(imgs, axis=0).shape)
