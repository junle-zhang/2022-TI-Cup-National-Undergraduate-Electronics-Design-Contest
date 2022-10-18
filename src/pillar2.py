class Recognition(object):
    flag = 0
    color = 0
    cx = 0
    cy = 0

Recognition = Recognition()
# 红色阈值
red_threshold = (0, 91, 34, 127, -60, 96)
# 绿色阈值
green_threshold = (20, 100, -84, -26, -2, 108)
# 蓝色阈值
blue_threshold = (20, 97, -68, 26, -64, -27)
# 黑色阈值
#black_threshold = (0, 31, -20, 49, -36, 58)
black_threshold = (0, 16, -128, 127, -128, 127)
# 颜色1: 红色的颜色代码
red_color_code = 1
# 颜色2: 绿色的颜色代码
green_color_code = 2
# 颜色3的代码
blue_color_code = 4

target_color_code = 1

Distance_Const = 2000
#18cm->55
#28cm->35
#38cm->26
#48cm->21
#58cm->19.5


def Distance(blob):
    Lm = (blob[2]+blob[3])/2
    return int(Distance_Const/Lm)


def UserPillarDataPack(flag, cx, blob):
    distance=Distance(blob)
    print(distance)
    Pillar_data = bytearray(
        [0xAA, 0x24, flag, cx >> 8, cx, distance >> 8, distance, 0xFF])
    return Pillar_data

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


def PillarRecognition(img):
    ROI = (0, int(img.height()/3), int(img.width()), int(img.height()/3))
    # 在图像中寻找满足颜色阈值约束(color_threshold, 数组格式), 像素阈值pixel_threshold， 色块面积大小阈值(area_threshold)的色块
    blobs = img.find_blobs([black_threshold], roi = ROI,
                           area_threshold=100)
    max_blob = FindMax(blobs)  #找到最大的那个
    if max_blob:
        #如果找到了目标颜色
        x = max_blob[0]
        y = max_blob[1]
        width = max_blob[2]  # 色块矩形的宽度
        height = max_blob[3]  # 色块矩形的高度
        center_x = max_blob[5]  # 色块中心点x值
        color_code = max_blob[8]  # 颜色代码
        #颜色识别
        #if color_code == target_color_code:
            #img.draw_string(x, y - 10, "red", color=(0xFF, 0x00, 0x00))
        Recognition.flag = 1
        #print("识别成功")
        Recognition.cx = center_x - img.width()/2
        img.draw_rectangle([x, y, width, height])
        Pack_Pillar = UserPillarDataPack(Recognition.flag, center_x, max_blob)
        #print(Pack_Pillar)
        Uart.write(Pack_Pillar)
    else:
        Recognition.flag = 0
        Recognition.cx = 0





import sensor, image, time, math, lcd, mjpeg
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
Pillar_Start_Flag = bytearray([0xAA, 0x26])
Pillar_Stop_Flag = bytearray([0xAA, 0x27])
Pillar_State = 0

# =====================Main===========================
m = mjpeg.Mjpeg("example.mjpeg")#录像文件初始化
while(True):
    clock.tick()
    img=sensor.snapshot()
    if Uart.any():
        cmd = Uart.read()
        if cmd == Pillar_Start_Flag:
            Pillar_State = 1
        elif cmd == Pillar_Stop_Flag:
            Pillar_State = 0
            m.close(clock.fps())
            break
    if Pillar_State == 1:
        PillarRecognition(img)
    m.add_frame(img)

