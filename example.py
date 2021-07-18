#! /usr/bin/python3

import time
import sys

EMULATE_HX711 = False

referenceUnit = 1

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711


def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        # 关闭IO口
        GPIO.cleanup()

    print("Bye!")
    sys.exit()


# 初始化GPIO端口
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()
print("已去皮,现在可以使用秤")

# 要使用两个通道，您需要将它们都去皮
# hx.tare_A()
# hx.tare_B()

while True:
    try:
        # 打印重量
        val = hx.get_weight(5)
        print(val)

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
