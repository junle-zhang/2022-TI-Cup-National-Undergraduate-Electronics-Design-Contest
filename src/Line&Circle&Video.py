import sensor, image, time, math, mjpeg
from pyb import UART

# ==============================Dot=================================


def UserDotDataPack(flag, X, Y):
    Temp_X = int(X)
    Temp_Y = int(Y)

    Cross_data = bytearray(
        [0xAA, 0x30, flag, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return Cross_data


# ==============================Line================================


def UserLineDataPack(flag, Angle, Distance):
    Temp_Angle = int(Angle)
    Temp_Distance = int(Distance)

    Line_data = bytearray([
        0xAA, 0x31, flag, Temp_Angle >> 8, Temp_Angle, Temp_Distance >> 8,
        Temp_Distance, 0xFF
    ])
    return Line_data


def Line_Theta(Line):
    if Line.y2() == Line.y1():
        return 90
    angle = math.atan(
        (Line.x1() - Line.x2()) / (Line.y2() - Line.y1())) * 180 / math.pi
    return angle


def Line_Distance(Line):
    return (Line.x1() + Line.x2()) / 2 - 80


def CalculateIntersection(line1, line2):
    a1 = line1.y2() - line1.y1()
    b1 = line1.x1() - line1.x2()
    c1 = line1.x2() * line1.y1() - line1.x1() * line1.y2()

    a2 = line2.y2() - line2.y1()
    b2 = line2.x1() - line2.x2()
    c2 = line2.x2() * line2.y1() - line2.x1() * line2.y2()
    if (a1 * b2 - a2 * b1) != 0 and (a2 * b1 - a1 * b2) != 0:
        cross_x = int((b1 * c2 - b2 * c1) / (a1 * b2 - a2 * b1))
        cross_y = int((c1 * a2 - c2 * a1) / (a1 * b2 - a2 * b1))

        cross_x = cross_x - 80
        cross_y = 60 - cross_y
        return (cross_x, cross_y)
    else:
        return (0, 0)


def LineCheck(img):

    Lines = img.find_lines(threshold=1200,
                           theta_margin=25,
                           rho_margin=25,
                           roi=ROIS)
    Len_Lines = len(Lines)
    Min_angle = 180

    if Len_Lines == 0:
        Pack_Line = UserLineDataPack(0, 0, 0)
        Uart.write(Pack_Line)
        Pack_Dot = UserDotDataPack(0, 0, 0)
        Uart.write(Pack_Dot)
    else:
        #print("发现线")
        Temp_Line = Lines[0]
        for line in Lines:
            if abs(Line_Theta(line)) < Min_angle:
                Temp_Line = line
                Min_angle = abs(Line_Theta(line))

        if (abs(Line_Theta(Temp_Line)) > 30):
            Pack_Line = UserLineDataPack(0, 0, 0)
            Uart.write(Pack_Line)
        else:
            img.draw_line(Temp_Line.line(), [255, 0, 0], 2)
            Pack_Line = UserLineDataPack(1, Line_Theta(Temp_Line),
                                         Line_Distance(Temp_Line))
            Uart.write(Pack_Line)

        if (Len_Lines == 1):
            Pack_Dot = UserDotDataPack(0, 0, 0)
            Uart.write(Pack_Dot)

        elif (Len_Lines == 2):
            x, y = CalculateIntersection(Lines[0], Lines[1])
            if (x < 80 and x > -80 and y < 60 and y > -60):
                Pack_Dot = UserDotDataPack(1, x, y)
                Uart.write(Pack_Dot)
                img.draw_cross(x + 80, -y + 60, 5, color=[255, 0, 0])
                #print("发现交叉")
            else:
                Pack_Dot = UserDotDataPack(0, 0, 0)
                Uart.write(Pack_Dot)
        elif (Len_Lines >= 3):
            Pack_Dot = UserDotDataPack(0, 0, 0)
            Uart.write(Pack_Dot)

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
        [0xAA, 0x32, flag, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return Circle_data


def Circlecheck(img):
    global Circle_State_Counter

    Circles = img.find_circles(threshold=1000,
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
            print("找到圆")
            img.draw_circle(Circles[0].x(),
                            Circles[0].y(),
                            Circles[0].r(),
                            color=(255, 0, 0))
            Pack_Circle = UserCircleDataPack(1, Circles[0].x() - 80,
                                             60 - Circles[0].y())
            Uart.write(Pack_Circle)

# ==============================ColorRecognition==============================
class Recognition(object):
    flag = 0
    color = 0
    cx = 0
    cy = 0

Recognition = Recognition()
# 红色阈值
red_threshold = (40, 91, 34, 127, -60, 96)
# 绿色阈值
green_threshold = (42, 100, -84, -26, -2, 108)
# 蓝色阈值
blue_threshold = (40, 97, -68, 26, -64, -27)

# 颜色1: 红色的颜色代码
red_color_code = 1
# 颜色2: 绿色的颜色代码
green_color_code = 2
# 颜色3的代码
blue_color_code = 3


def UserColorDataPack(flag, color, X, Y):
    Temp_Color=int(color)
    Temp_X = int(X)
    Temp_Y = int(Y)
    Circle_data = bytearray(
        [0xAA, 0x34, flag, Temp_Color, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return Circle_data

def FindMax(blobs):
    max_size = 1
    if blobs:
        max_blob = 0
        for blob in blobs:
            blob_size = blob.w() * blob.h()
            if ((blob_size > max_size) & (blob_size > 50)):
                if (math.fabs(blob.w() / blob.h() - 1) < 2.0):
                    max_blob = blob
                    max_size = blob.w() * blob.h()
        return max_blob
    else:
        return None


def ColorRecognition(img):
    # 在图像中寻找满足颜色阈值约束(color_threshold, 数组格式), 像素阈值pixel_threshold， 色块面积大小阈值(area_threshold)的色块
    blobs = img.find_blobs([red_threshold, green_threshold, blue_threshold],
                           area_threshold=500)
    max_blob = FindMax(blobs)  #找到最大的那个
    if max_blob:
        #如果找到了目标颜色
        x = max_blob[0]
        y = max_blob[1]
        width = max_blob[2]  # 色块矩形的宽度
        height = max_blob[3]  # 色块矩形的高度
        center_x = max_blob[5]  # 色块中心点x值
        center_y = max_blob[6]  # 色块中心点y值
        color_code = max_blob[8]  # 颜色代码
        #颜色识别
        if color_code == red_color_code:
            #img.draw_string(x, y - 10, "red", color=(0xFF, 0x00, 0x00))
            Recognition.flag = 1
            Recognition.color = 1
            print("red")
            Recognition.cx = center_x - img.width()/2
            Recognition.cy = img.height()/2 - center_y
        elif color_code == green_color_code:
            #img.draw_string(x, y - 10, "green", color=(0x00, 0xFF, 0x00))
            Recognition.flag = 1
            Recognition.color = 2
            print("green")
            Recognition.cx = center_x - img.width()/2
            Recognition.cy = img.height()/2 - center_y
        elif color_code == blue_color_code:
            #img.draw_string(x, y - 10, "blue", color=(0x00, 0x00, 0xFF))
            Recognition.flag = 1
            Recognition.color = 3
            print("blue")
            Recognition.cx = center_x - img.width()/2
            Recognition.cy = img.height()/2 - center_y
        else:
            Recognition.flag = 0
            Recognition.color = 0
            Recognition.cx = 0
            Recognition.cy = 0
        #用矩形标记出目标颜色区域
        img.draw_rectangle([x, y, width, height])
        #在目标颜色区域的中心画十字形标记
        img.draw_cross(center_x, center_y)
        Pack_Color = UserColorDataPack(Recognition.flag, Recognition.color, Recognition.cx,Recognition.cy)
        Uart.write(Pack_Color)






# =====================Variable===========================
ROIS = (30, 0, 100, 120)
Line_Start_Flag = bytearray([0XAA, 0X32])
Line_Stop_Flag = bytearray([0XAA, 0X33])
Video_Start_Flag = bytearray([0XAA, 0X10])
Video_Stop_Flag = bytearray([0XAA, 0X11])
Circle_Start_Flag = bytearray([0XAA, 0X34])
Circle_Stop_Flag = bytearray([0XAA, 0X35])
#Color_Start_Flag = bytearray([0XAA, 0X40])
#Color_Stop_Flag = bytearray([0XAA, 0X41])
Uart = UART(3, 500000)
Uart.init(500000)

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)  # 设置相机模块的像素模式
sensor.set_framesize(sensor.QQVGA)  # 设置相机分辨率160*120
sensor.skip_frames(time=3000)  # 时钟
sensor.set_auto_whitebal(False)  # 若想追踪颜色则关闭白平衡
clock = time.clock()  # 初始化时钟

Line_State = 0
Circle_State = 1
Video_State = 0
#Color_State = 0
# ========================main=============================
while (True):
    clock.tick()
    img = sensor.snapshot()
    if Uart.any():
        Uart3_Cmd = Uart.read()
        for cmd in Uart3_Cmd:
                if (cmd == 0xAA):
                    frame_start_flag = 1
                elif (frame_start_flag == 1 and cmd != 0xAA):
                    if (cmd == 0x10):
                        Video_State = 1
                        m = mjpeg.Mjpeg("example.mjpeg")#录像文件初始化
                    elif cmd == 0x11:
                        Video_State = 0
                        m.close(clock.fps())
                    elif cmd == 0x34:
                        Circle_State = 1
                    elif cmd == 0x35:
                        Circle_State = 0
                    elif cmd == 0x32:
                        Line_State = 1
                    elif cmd == 0x33:
                        Line_State = 0
                    #elif cmd == 0x36:
                    #    Color_State = 1
                    #elif cmd == 0x37:
                    #    Color_State = 0
                    #frame_start_flag = 0

    if Line_State == 1:
        LineCheck(img)
    if Circle_State == 1:
        Circlecheck(img)
    if Video_State == 1:
        m.add_frame(img)
   # if Color_State == 1:
   #     ColorRecognition(img)



# ***************** End of File *******************
