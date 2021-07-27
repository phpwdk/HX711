#! /usr/bin/python3
import time, sys, math
import RPi.GPIO as GPIO
from hx711 import HX711
from common import COMMON

# 去皮重量
referenceUnit = 9.497
switch = 0
pd_sck = 6
dout = 5


def calculated_weight(weight):
    return max(0, round(int(weight) / 100) * 10)


def main():
    com = COMMON()
    # 初始化秤
    GPIO.cleanup()
    hx = HX711(dout, pd_sck)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(referenceUnit)
    hx.reset()
    hx.tare()
    # 通知服务器设备启动
    api_url_path = "https://disc.wkh01.top/device/weigh/v1"
    url = "%s?serial=%s&weight=%d" % (api_url_path, com.serial(), 0)
    response = com.get(url)
    if not response:
        print("访问网络失败")
    # print(response)
    is_switch = response['data']['switch']
    peeled = response['data']['peeled']
    old_weight = 0
    # 循环读取数值
    while 1:
        try:
            weight = 0
            p = 0
            # 去皮
            if peeled == 1:
                hx.reset()
                hx.tare()
                p = 1
            else:
                # 断电休眠
                if is_switch == 1:
                    if GPIO.input(pd_sck) == 0:
                        print('断电')
                        GPIO.output(pd_sck, True)
                else:
                    hx.power_down()
                    hx.power_up()
                    # 采集15次数据样本,取平均值
                    weight = calculated_weight(hx.get_weight(5))
                    print("weight: %d" % weight)
            # 上报设备数据
            api_url_path = "https://disc.wkh01.top/device/weigh/v1"
            url = "%s?serial=%s&weight=%d&peeled=%d" % (api_url_path, com.serial(), weight, p)
            response = com.get(url)
            if response:
                is_switch = response['data']['switch']
                peeled = response['data']['peeled']
            if old_weight != weight:
                stop_time = 0.1
                old_weight = weight
            else:
                stop_time = 3
            time.sleep(stop_time)

        except (KeyboardInterrupt, SystemExit):
            cleanAndExit()


def cleanAndExit():
    # 关闭IO口
    GPIO.cleanup()
    print("Bye!")
    sys.exit()


if __name__ == '__main__':
    main()
