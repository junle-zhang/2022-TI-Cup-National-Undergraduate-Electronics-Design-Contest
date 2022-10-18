# Untitled - By: Accelerator - 周日 7月 17 2022

import sensor, image, time, lcd, mjpeg
from pyb import UART
from pyb import LED

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.VGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False)  # 必须关闭此功能，以防止图像冲洗…

clock = time.clock()

Uart = UART(3, 500000)
Uart.init(500000)

class QRcode(object):#数据太少了用不到这个类
    QRcodemessage = 0


QRcode = QRcode()

def UserQRcodeDataPack(flag, Message, X, Y):
    Temp_Message = int(Message)
    Temp_X = int(X) - 320
    Temp_Y = 240 - int(Y)
    QRcode_data = bytearray(
        [0xAA, 0x22, flag, Temp_Message, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return QRcode_data

def ScanQRcode(img):
    QRcodes=img.find_qrcodes()
    Len_QRcodes=len(QRcodes)

    if Len_QRcodes == 0:
        Pack_QRcode = UserQRcodeDataPack(0, 0, 320, 240)
        Uart.write(Pack_QRcode)
    else:
        for qrcode in QRcodes:
            img.draw_rectangle(qrcode.rect(), color=255)
            print('信息', qrcode.payload())
            Pack_QRcode = UserQRcodeDataPack(1, qrcode.payload(), qrcode.x()+qrcode.w()/2, qrcode.y()+qrcode.h()/2)
            Uart.write(Pack_QRcode)



# =====================Variable===========================
QRcode_Start_Flag = bytearray([0xAA, 0x20])
QRcode_Stop_Flag = bytearray([0xAA, 0x21])
QRcode_State = 1
led1=LED(1)
led2=LED(2)
# =====================Main===========================
m = mjpeg.Mjpeg("example.mjpeg")#录像文件初始化
while(True):
    clock.tick()
    led2.toggle()
    img = sensor.snapshot()
    if Uart.any():
        cmd = Uart.read()
        if cmd == QRcode_Start_Flag:
            QRcode_State = 1
            led1.on()
        elif cmd == QRcode_Stop_Flag:
            QRcode_State = 0
            led1.off()
            m.close(clock.fps())
    if QRcode_State == 1:
        ScanQRcode(img)
        m.add_frame(img)

