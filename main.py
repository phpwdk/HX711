#! /usr/bin/python3
import time, sys
import RPi.GPIO as GPIO
from hx711 import HX711
from common import common


def main():
    # 初始化秤
    hx = HX711(5, 6)
    hx.set_reading_format("MSB", "MSB")
    # 去皮设置,2KG的砝码（2kg=2000），-882000 ÷ 2000 = -441
    hx.set_reference_unit(1)
    hx.reset()
    tare = hx.tare()
    print("皮重: %s" % tare)
    # 循环读取数值
    while 1:
        try:
            # 打印重量
            val = max(0, int(hx.get_weight(5)))
            print("重量: " % val)
            # 通知服务器
            api_url_path = "https://disc.wkh01.top/device/weigh/v1"
            url = "%s?serial=%s&weight=%d" % (api_url_path, common.serial(), val)
            response = common.get(url)
            if not response:
                raise ValueError("访问网络失败")
            print(response.info)
            hx.power_down()
            hx.power_up()
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
