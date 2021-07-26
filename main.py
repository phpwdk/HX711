#! /usr/bin/python3
import time, sys, json
import RPi.GPIO as GPIO
from hx711 import HX711
from common import common

# 去皮重量
referenceUnit = 9.497
switch = '0'


def main():
    # 初始化秤
    hx = HX711(5, 6)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(referenceUnit)
    hx.reset()
    hx.tare()
    # 通知服务器设备启动
    api_url_path = "https://disc.wkh01.top/device/weigh/v1"
    url = "%s?serial=%s&weight=%d" % (api_url_path, common.serial(), 0)
    response = common.get(url)
    if not response:
        print("访问网络失败")
    print(response)
    is_switch = response['data']['switch']
    # 循环读取数值
    while 1:
        try:
            # 打印重量
            # val = max(0, int(hx.get_weight(5)))
            # weight = calculated_weight(val)
            # print("重量: " % weight)
            # 断电休眠
            if is_switch == '0':
                hx.power_down()
            else:
                hx.power_down()
                hx.power_up()
                # 重新启动忽略前4次采集
                for x in range(4):
                    hx.read_long()
                # 采集15次数据样本,取平均值
                weight = hx.read_average()
                print("重量: " % weight)
            # 延时100毫秒
            time.sleep(0.1)

        except (KeyboardInterrupt, SystemExit):
            cleanAndExit()


def cleanAndExit():
    # 关闭IO口
    GPIO.cleanup()
    print("Bye!")
    sys.exit()


if __name__ == '__main__':
    main()
