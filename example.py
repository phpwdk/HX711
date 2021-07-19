#! /usr/bin/python3

import time, sys
import RPi.GPIO as GPIO
from hx711 import HX711

# 去皮重量
referenceUnit = 1


def cleanAndExit():
    print("Cleaning...")
    # 关闭IO口
    GPIO.cleanup()
    print("Bye!")
    sys.exit()


# 初始化GPIO口,树莓派IO5数据口(DOUT),IO6时钟口(PD_SCK)
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
# 去皮设置,2KG的砝码（2kg=2000），-882000 ÷ 2000 = -441
hx.set_reference_unit(referenceUnit)
hx.reset()
tare = hx.tare()
print("皮重: %s" % tare)

# HX711有两个通道,但一般都是A通道
# hx.tare_A()
# hx.tare_B()

while True:
    try:
        # 打印重量
        val = hx.get_weight(5)
        # val = max(0, int(hx.get_weight(5)))
        print("重量: " % val)

        # 从两个通道获取重量（如果您连接了称重传感器）
        # val_A = hx.get_weight_A(5)
        # val_B = hx.get_weight_B(5)
        # print "A: %s  B: %s" % ( val_A, val_B )

        hx.power_down()
        hx.power_up()
        # 延时100毫秒
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
