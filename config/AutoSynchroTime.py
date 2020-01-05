# coding=utf-8
import os
import platform

import ntplib
import datetime


def auto_synchro_time():
    """
    同步北京时间，执行时候，请务必用sudo，sudo，sudo 执行，否则会报权限错误，windows打开ide或者cmd请用管理员身份
    :return:
    """
    c = ntplib.NTPClient()

    hosts = ['ntp1.aliyun.com', 'ntp2.aliyun.com', 'ntp3.aliyun.com', 'ntp4.aliyun.com', 'cn.pool.ntp.org',
             'edu.ntp.org.cn', 'tw.ntp.org.cn', 'us.ntp.org.cn', 'jp.ntp.org.cn']

    print(u"正在同步时间，请耐心等待30秒左右，如果下面有错误发送，可以忽略！！")
    print(u"系统当前时间{}".format(str(datetime.datetime.now())[:22]))
    system = platform.system()
    if system == "Windows":
        for host in hosts:
            # noinspection PyBroadException
            try:
                response = c.request(host)
                if response:
                    break
            except Exception as e:
                print(e)
    else:  # mac同步地址，如果ntpdate未安装，brew install ntpdate    linux 安装 yum install -y ntpdate
        for host in hosts:
            sin = os.popen('ntpdate {}'.format(host))
            if sin is 0:
                break
    print(u"同步后时间:{}".format(str(datetime.datetime.now())[:22]))


if __name__ == '__main__':
    auto_synchro_time()
