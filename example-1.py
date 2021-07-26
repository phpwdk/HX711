# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time


class Hx711():
    def setup(self):
        self.SCK = 31
        self.DT = 29
        self.flag = 1
        self.initweight = 0
        self.weight = 0
        self.delay = 0.09
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.SCK, GPIO.OUT)
        GPIO.setup(self.DT, GPIO.IN)
        GPIO.setup(self.DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def start(self):
        GPIO.output(self.SCK, 0)
        if GPIO.input(self.SCK):
            time.sleep(self.delay)
        value = 0
        while GPIO.input(self.DT):
            time.sleep(self.delay)
        for i in range(24):
            GPIO.output(self.SCK, 1)
            if (0 == GPIO.input(self.SCK)):
                time.sleep(self.delay)
            value = value << 1
            GPIO.output(self.SCK, 0)
            if GPIO.input(self.SCK):
                time.sleep(self.delay)
            if GPIO.input(self.DT) == 1:
                value += 1
        GPIO.output(self.SCK, 1)
        GPIO.output(self.SCK, 0)
        value = int(value / 94.97)
        if self.flag == 1:
            self.flag = 0
            self.initweight = value
            print(self.initweight)
        else:
            self.weight = abs(value - self.initweight)
            print(self.weight)


if __name__ == '__main__':
    send = Hx711()
    send.setup()
    while True:
        send.start()
        time.sleep(0.2)
