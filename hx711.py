import RPi.GPIO as GPIO
import time
import threading


class HX711:
    # dout 输入数据, pd_sck 时钟
    def __init__(self, dout, pd_sck, gain=128):
        self.PD_SCK = pd_sck

        self.DOUT = dout

        # Mutex for reading from the HX711, in case multiple threads in client
        # software try to access get values from the class at the same time.
        self.readLock = threading.Lock()

        # 引脚编号方式
        GPIO.setmode(GPIO.BCM)
        # 设置输出时钟频率
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        # 设置输入数据通道
        GPIO.setup(self.DOUT, GPIO.IN)

        self.GAIN = 0

        self.REFERENCE_UNIT = 1
        self.REFERENCE_UNIT_B = 1

        self.OFFSET = 1
        self.OFFSET_B = 1
        self.lastVal = int(0)

        self.DEBUG_PRINTING = False

        self.byte_format = 'MSB'
        self.bit_format = 'MSB'

        self.set_gain(gain)

        time.sleep(1)

    def convertFromTwosComplement24bit(self, inputValue):
        return -(inputValue & 0x800000) + (inputValue & 0x7fffff)

    def is_ready(self):
        return GPIO.input(self.DOUT) == 0

    # 设置增益通道
    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2

        GPIO.output(self.PD_SCK, False)

        # 读出一组原始字节并将其丢弃。
        self.readRawBytes()

    # 读取增益通道
    def get_gain(self):
        if self.GAIN == 1:
            return 128
        if self.GAIN == 3:
            return 64
        if self.GAIN == 2:
            return 32
        return 0

    # 读取数据位
    def readNextBit(self):
        # 时钟
        GPIO.output(self.PD_SCK, True)
        GPIO.output(self.PD_SCK, False)
        value = GPIO.input(self.DOUT)

        # 将 Boolean 转换为 int 并返回它
        return int(value)

    # 读取一字节数据
    def readNextByte(self):
        byteValue = 0

        # 读取位并从顶部或底部构建字节，具体取决于
        # MSB 还是 LSB 位模式.
        for x in range(8):
            if self.bit_format == 'MSB':
                byteValue <<= 1
                byteValue |= self.readNextBit()
            else:
                byteValue >>= 1
                byteValue |= self.readNextBit() * 0x80

        return byteValue

    # 读取原始字节
    def readRawBytes(self):
        # 锁
        self.readLock.acquire()

        # 等到 HX711 准备好让我们读取样本
        while not self.is_ready():
            pass

        # 从 HX711 读取三个字节的数据
        firstByte = self.readNextByte()
        secondByte = self.readNextByte()
        thirdByte = self.readNextByte()

        # HX711 通道和增益系数由读取的位数设置
        # 24 个数据位.
        for i in range(self.GAIN):
            # 将 HX711 稍微计时一下然后扔掉.
            self.readNextBit()
        # 解锁
        self.readLock.release()

        # 根据我们的配置方式，返回原始字节的有序列表
        if self.byte_format == 'LSB':
            return [thirdByte, secondByte, firstByte]
        else:
            return [firstByte, secondByte, thirdByte]

    def read_long(self):
        # 以原始字节的形式从 HX711 获取样本
        dataBytes = self.readRawBytes()

        if self.DEBUG_PRINTING:
            print(dataBytes, )

        # 将原始字节加入单个 24 位 2s 补码值
        twosComplementValue = ((dataBytes[0] << 16) |
                               (dataBytes[1] << 8) |
                               dataBytes[2])

        if self.DEBUG_PRINTING:
            print("Twos: 0x%06x" % twosComplementValue)

        # 从 24 位二进制补码转换为有符号值
        signedIntValue = self.convertFromTwosComplement24bit(twosComplementValue)

        # 记录我们读过的最新样本值
        self.lastVal = signedIntValue

        # 返回我们从 HX711 读取的样本值
        return int(signedIntValue)

    # 读取平均值
    def read_average(self, times=3):
        # 抽取合理数量的样本
        if times <= 0:
            raise ValueError("HX711()::read_average(): times must >= 1!!")

        # 如果我们只对一个值求平均值，只需读取它并返回它
        if times == 1:
            return self.read_long()

        # 如果我们对少量值进行平均，只需取中位数.
        if times < 5:
            return self.read_median(times)

        # 如果我们要采集大量样本，我们会将它们收集在一个列表中，删除离群值，然后取剩余集合的平均值
        valueList = []

        for x in range(times):
            valueList += [self.read_long()]

        valueList.sort()

        # 我们将从收集的顶部和底部修剪 20% 的离群样本
        trimAmount = int(len(valueList) * 0.2)

        # 修剪边缘情况值
        valueList = valueList[trimAmount:-trimAmount]

        # 返回剩余样本的平均值
        return sum(valueList) / len(valueList)

    # 读取一个时钟周期平均值
    def read_median(self, times=3):
        if times <= 0:
            raise ValueError("HX711::read_median()：时间必须大于零！")

        # If times == 1, 返回一个读数
        if times == 1:
            return self.read_long()

        valueList = []

        for x in range(times):
            valueList += [self.read_long()]

        valueList.sort()

        # 如果时间是奇数，我们可以只取中心值
        if (times & 0x1) == 0x1:
            return valueList[len(valueList) // 2]
        else:
            # 如果时间是偶数，我们必须取算术平均值的两个中间值
            midpoint = len(valueList) / 2
            return sum(valueList[midpoint:midpoint + 2]) / 2.0

    def get_value(self, times=3):
        return self.get_value_A(times)

    def get_value_A(self, times=3):
        return self.read_median(times) - self.get_offset_A()

    def get_value_B(self, times=3):
        # 对于通道 B，我们需要 set_gain(32)
        g = self.get_gain()
        self.set_gain(32)
        value = self.read_median(times) - self.get_offset_B()
        self.set_gain(g)
        return value

    # 读取重量
    def get_weight(self, times=3):
        return self.get_weight_A(times)

    def get_weight_A(self, times=3):
        value = self.get_value_A(times)
        value = value / self.REFERENCE_UNIT
        return value

    def get_weight_B(self, times=3):
        value = self.get_value_B(times)
        value = value / self.REFERENCE_UNIT_B
        return value

    def tare(self, times=15):
        return self.tare_A(times)

    def tare_A(self, times=15):
        backupReferenceUnit = self.get_reference_unit_A()
        self.set_reference_unit_A(1)

        value = self.read_average(times)

        if self.DEBUG_PRINTING:
            print("Tare A value:", value)

        self.set_offset_A(value)

        # Restore the reference unit, now that we've got our offset.
        self.set_reference_unit_A(backupReferenceUnit)

        return value

    def tare_B(self, times=15):
        # Backup REFERENCE_UNIT value
        backupReferenceUnit = self.get_reference_unit_B()
        self.set_reference_unit_B(1)

        # for channel B, we need to set_gain(32)
        backupGain = self.get_gain()
        self.set_gain(32)

        value = self.read_average(times)

        if self.DEBUG_PRINTING:
            print("Tare B value:", value)

        self.set_offset_B(value)

        # Restore gain/channel/reference unit settings.
        self.set_gain(backupGain)
        self.set_reference_unit_B(backupReferenceUnit)

        return value

    def set_reading_format(self, byte_format="LSB", bit_format="MSB"):
        if byte_format == "LSB":
            self.byte_format = byte_format
        elif byte_format == "MSB":
            self.byte_format = byte_format
        else:
            raise ValueError("Unrecognised byte_format: \"%s\"" % byte_format)

        if bit_format == "LSB":
            self.bit_format = bit_format
        elif bit_format == "MSB":
            self.bit_format = bit_format
        else:
            raise ValueError("Unrecognised bitformat: \"%s\"" % bit_format)

    def set_offset(self, offset):
        self.set_offset_A(offset)

    def set_offset_A(self, offset):
        self.OFFSET = offset

    def set_offset_B(self, offset):
        self.OFFSET_B = offset

    def get_offset(self):
        return self.get_offset_A()

    def get_offset_A(self):
        return self.OFFSET

    def get_offset_B(self):
        return self.OFFSET_B

    def set_reference_unit(self, reference_unit):
        self.set_reference_unit_A(reference_unit)

    def set_reference_unit_A(self, reference_unit):
        # 确保我们没有被要求使用无效的参考单位。
        if reference_unit == 0:
            raise ValueError("HX711::set_reference_unit_A() 不能接受 0 作为参考单位！")
            return

        self.REFERENCE_UNIT = reference_unit

    def set_reference_unit_B(self, reference_unit):
        # 确保我们没有被要求使用无效的参考单位。
        if reference_unit == 0:
            raise ValueError("HX711::set_reference_unit_A() 不能接受 0 作为参考单位！")
            return

        self.REFERENCE_UNIT_B = reference_unit

    def get_reference_unit(self):
        return get_reference_unit_A()

    def get_reference_unit_A(self):
        return self.REFERENCE_UNIT

    def get_reference_unit_B(self):
        return self.REFERENCE_UNIT_B

    def power_down(self):
        # 锁,防止其它进程操作
        self.readLock.acquire()
        # 时钟输出一个上升沿
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)
        # 停留100微秒
        time.sleep(0.0001)
        # 解锁
        self.readLock.release()

    def power_up(self):
        # 锁,防止其它进程操作
        self.readLock.acquire()
        # 时钟输出下降沿
        GPIO.output(self.PD_SCK, False)
        # 停留100微妙,设备重启
        time.sleep(0.0001)
        # 解锁
        self.readLock.release()
        # 增益通道不是128时丢弃
        if self.get_gain() != 128:
            self.readRawBytes()

    def reset(self):
        self.power_down()
        self.power_up()
