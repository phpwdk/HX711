# HX711与树莓派通信实现电子秤功能
----
##python2
> pip install numpy
>
> pip install Rpi.GPIO 

##python3
> pip install Rpi.GPIO2
----

##HX711中文文档
> https://max.book118.com/html/2017/0525/109008848.shtm

##HX711英文文档
> https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf

----

##排针需要焊上去，所以又买了电烙铁。现在开始
````
组装配件（卖家有教程），故不再赘述 
走线 HX711共有6个连接，但是我们只用其中4个
黑色：E- 
绿色：A- 
白色：A + 
红色：E + 
````

##HX711接树莓派
````
VCC至Raspberry Pi Pin 2（5V） 
GND至Raspberry Pi引脚6（GND） 
DT至Raspberry Pi Pin 29（GPIO 5） 
SCK至Raspberry Pi引脚31（GPIO 6）
```` 

##树莓派接线图
![树莓派节选图](https://pic4.zhimg.com/80/v2-e04f0b941f3987676597d4d2b1792cff_720w.jpg)

##校正称
````
执行
> python example.py
显示的值可能正也可能负，这个不重要，例如用2KG的砝码（2kg=2000），-882000 ÷ 2000 = -441，
进入example.py文件修改
referenceUnit = -441
````
