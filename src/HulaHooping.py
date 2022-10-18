import sensor, image, time, math, mjpeg
from pyb import UART
import pyb
# ==============================Circle==============================

# ==============================Circle==============================

Circle_State_Counter = 0


def UserCircleDataPack(flag, X, Y):
    """
    用于打包圆的数据

    Arguments:
        flag {int} -- 检测是否有圆
        X {int} -- X坐标
        Y {int} -- Y坐标

    Returns:
        bytearray -- 数据包
    """
    Temp_X = int(X)
    Temp_Y = int(Y)
    Circle_data = bytearray(
        [0xAA, 0x25, flag, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return Circle_data


def Circlecheck(img):
    global Circle_State_Counter

    Circles = img.find_circles(threshold=3500,
                               x_margin=5,
                               y_margin=5,
                               r_margin=30)
    Len_Circles = len(Circles)
    if Len_Circles == 0:
        Circle_State_Counter = 0
        Pack_Circle = UserCircleDataPack(0, 0, 0)
        Uart.write(Pack_Circle)
    else:
        if Circle_State_Counter < 5:
            Circle_State_Counter = Circle_State_Counter + 1
        else:
            img.draw_circle(Circles[0].x(),
                            Circles[0].y(),
                            Circles[0].r(),
                            color=(255, 0, 0))
            Pack_Circle = UserCircleDataPack(1, Circles[0].x() - 80,
                                             60 - Circles[0].y())
            Uart.write(Pack_Circle)


# =====================Variable===========================
Hoop_Start_Flag = bytearray([0XAA, 0X28])
Hoop_Stop_Flag = bytearray([0XAA, 0X29])
Uart = UART(3, 500000)
Uart.init(500000)

s1 = pyb.Servo(1)  #在P7引脚创建servo对象
s2 = pyb.Servo(2)  #在P8引脚创建servo对象

sensor.reset()
sensor.set_pixformat(sensor.RGB565)  # 设置相机模块的像素模式
sensor.set_framesize(sensor.QQVGA)  # 设置相机分辨率160*120
sensor.skip_frames(time=3000)  # 时钟
sensor.set_auto_whitebal(False)  # 若想追踪颜色则关闭白平衡
clock = time.clock()  # 初始化时钟

Hoop_State = 1

# ========================main=============================
#m = mjpeg.Mjpeg("example.mjpeg")#录像文件初始化

while (True):
    clock.tick()
    img = sensor.snapshot()#.lens_corr(1.8)
    if Uart.any():
        cmd = Uart.read()
        if cmd == Hoop_Start_Flag:
            Hoop_State = 1
            s1.angle(90, 1500)
            s2.angle(0, 1500)
        elif cmd == Hoop_Stop_Flag:
            Hoop_State = 0
            #m.close(clock.fps())
            break
    if Hoop_State == 1:
        Circlecheck(img)
    #m.add_frame(img)




# ***************** End of File *******************
