class Recognition(object):
    flag = 0
    color = 0
    cx = 0
    cy = 0

Recognition = Recognition()
# 红色阈值
red_threshold = (15, 91, 34, 127, -60, 96)
# 绿色阈值
green_threshold = (20, 100, -84, -26, -2, 108)
# 蓝色阈值
blue_threshold = (20, 97, -68, 26, -64, -27)

# 颜色1: 红色的颜色代码
red_color_code = 1
# 颜色2: 绿色的颜色代码
green_color_code = 2
# 颜色3的代码
blue_color_code = 4


def UserColorDataPack(flag, color, X, Y):
    Temp_Color=int(color)
    Temp_X = int(X)
    Temp_Y = int(Y)
    Color_data = bytearray(
        [0xAA, 0x23, flag, Temp_Color, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return Color_data

def FindMax(blobs):
    max_size = 1
    if blobs:
        max_blob = 0
        for blob in blobs:
            blob_size = blob.w() * blob.h()
            if ((blob_size > max_size) & (blob_size > 100)):
                if (math.fabs(blob.w() / blob.h() - 1) < 2.0):
                    max_blob = blob
                    max_size = blob.w() * blob.h()
        return max_blob
    else:
        return None


def ColorRecognition(img):
    # 在图像中寻找满足颜色阈值约束(color_threshold, 数组格式), 像素阈值pixel_threshold， 色块面积大小阈值(area_threshold)的色块
    blobs = img.find_blobs([red_threshold, green_threshold, blue_threshold],
                           area_threshold=400)
    #max_blob = FindMax(blobs)  #找到最大的那个
    #if max_blob:
    for max_blob in blobs:
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
            img.draw_string(x, y - 10, "green", color=(0x00, 0xFF, 0x00))
            Recognition.flag = 1
            Recognition.color = 2
            print("green")
            Recognition.cx = center_x - img.width()/2
            Recognition.cy = img.height()/2 - center_y
        elif color_code == blue_color_code:
            img.draw_string(x, y - 10, "blue", color=(0x00, 0x00, 0xFF))
            Recognition.flag = 1
            Recognition.color = 4
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



import sensor, image, time, math, lcd
from pyb import LED
from pyb import UART
#初始化镜头
sensor.reset()
sensor.set_pixformat(sensor.RGB565)  #设置相机模块的像素模式
sensor.set_framesize(sensor.QVGA)  #设置相机分辨率
sensor.skip_frames(time=3000)  #时钟
sensor.set_auto_whitebal(False)  #若想追踪颜色则关闭白平衡
sensor.set_auto_gain(True) # 颜色跟踪必须自动增益
clock = time.clock()  #初始化时钟

sensor.set_contrast(1)  #设置相机图像对比度。-3至+3
sensor.set_gainceiling(16)  #设置相机图像增益上限。2, 4, 8, 16, 32, 64, 128。

Uart = UART(3, 500000)
Uart.init(500000)


# =====================Variable===========================
Color_Start_Flag = bytearray([0xAA, 0x24])
Color_Stop_Flag = bytearray([0xAA, 0x25])
Color_State = 1

# =====================Main===========================
while(True):
    img=sensor.snapshot()
    if Uart.any():
        cmd = Uart.read()
        if cmd == Color_Start_Flag:
            Color_State = 1
        elif cmd == Color_Stop_Flag:
            Color_State = 0
    if Color_State == 1:
        ColorRecognition(img)

