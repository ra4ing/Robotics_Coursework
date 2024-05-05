import cv2
from robomaster import *
import time
import numpy as np
#####################################################################
markers = []
line = []
gettext = []
cnt = 0
capturing = False
red_capturing = False
l = 0
p_ret = False
start_time = -5
# 参数集合
#####################################################################
class CircleInfo:
    def __init__(self, x, y, radius):
        self._x = x
        self._y = y
        self._radius = int(radius)
    @property
    def pt(self):
        return int(self._x), int(self._y)
# 圆信息
#####################################################################
class MarkerInfo:
    def __init__(self, x, y, w, h, info):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._info = info

    @property
    def pt1(self):
        return int((self._x - self._w / 2) * 640), int((self._y - self._h / 2) * 360)

    @property
    def pt2(self):
        return int((self._x + self._w / 2) * 640), int((self._y + self._h / 2) * 360)

    @property
    def center(self):
        return int(self._x * 640), int(self._y * 360)

    @property
    def text(self):
        return self._info
# marker信息
#####################################################################
class PointInfo:
    def __init__(self, x, y, theta, c):
        self._x = x
        self._y = y
        self._theta = theta
        self._c = c

    @property
    def pt(self):
        return int(self._x * 1280), int(self._y * 720)

    @property
    def color(self):
        return 255, 255, 255
# 线信息
#####################################################################
def on_detect_marker(marker_info):
    number = len(marker_info)
    markers.clear()
    for i in range(0, number):
        x, y, w, h, info = marker_info[i]
        markers.append(MarkerInfo(x, y, w, h, info))
# 获得marker信息
#####################################################################
def on_detect_line(line_info):
    number = len(line_info)
    line.clear()
    if number > 0:
        line_type = line_info[0]
        for i in range(1, number):
            x, y, ceta, c = line_info[i]
            line.append(PointInfo(x, y, ceta, c))
# 获得⚪信息
#####################################################################
def process(image) -> object:
    global pos
    # RGB转HSV色彩空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    low_hsv = np.array([0, 43, 46])
    high_hsv = np.array([5, 255, 255])

    mask = cv2.inRange(hsv, lowerb=low_hsv, upperb=high_hsv)  # 取值函数
    dst = cv2.blur(mask, (1, 16))  # 均值模糊 : 去掉提取完颜色的随机噪声图片

    circles = cv2.HoughCircles(dst, cv2.HOUGH_GRADIENT, 1, 100, param1=1, param2=25, minRadius=37, maxRadius=50)
    # 霍夫圆检测函数，其中的参数需要根据情况修改
    pos = [0, 0]
    ret = False
    if circles is not None:
        # print("Found", len(circles), "circles")
        for i in circles[0, :]:
            #print(i)
            c = CircleInfo(i[0], i[1], i[2])
            image = cv2.circle(image, c.pt, c._radius, (255, 255, 255), 2)  # 画圆
            image = cv2.circle(image, c.pt, 2, (255, 255, 255), 2)  # 画圆心

            pos[0] = i[0]
            pos[1] = i[1]
            print('圆形')
            ret = True
    else:
        ret = False
    return image, pos, ret
# 获取圆信息
#####################################################################
def red_light():
    global l
    global p_ret
    global red_capturing
    global pos
    global result
    global start_time

    red_capturing = True
    # 进行云台比例控制，保持识别物体位于视野中心
    while red_capturing:
        img = ep_camera.read_cv2_image(strategy="newest")
        if img is None:
            continue

        result, pos, p_ret = process(img)
        #print(p_ret)
        ep_chassis.drive_speed(x=0, y=0, z=0)
        if l <= 1 and time.time() - start_time > 5:
            time.sleep(1)
            cv2.putText(img, "Team 09 detects the red light", [200, 180], cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (255, 255, 255),
                        2, bottomLeftOrigin=None)
            cv2.imwrite(l.__str__() + 'Team 09 detects the red light.png', img)
            cv2.imshow(l.__str__() + 'Team 09 detects the red light.png', img)
            l += 1
            start_time = time.time()
        if not p_ret:
            red_capturing = False
# 识别红圆并停止
#####################################################################
def getCapture(frame1):
    global cnt
    global markers
    global capturing
    global text
    global gettext

    capturing = True
    ep_chassis.drive_speed(x=0, y=0, z=0)
    print("checking...")
    while capturing:
        frame1 = ep_camera.read_cv2_image(strategy="newest")
        if frame1 is None:
            continue
        for j in range(0, len(markers)):
            if len(markers) > 0:
                error_X = 0.5 - markers[j]._x
                error_y = markers[j]._y - 0.5
                if abs(error_X) <= 0.02 and abs(error_y) <= 0.02:
                    # cv2.rectangle(frame1, markers[j].pt2, markers[j].pt1,
                    #               (255, 255, 255))
                    cv2.putText(frame1,
                                "Team 09 detects a marker with ID of " + markers[j].text, markers[j].center,
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                                (255, 255, 255),
                                2, bottomLeftOrigin=None)
                    frame1 = cv2.resize(frame1, (640, 360))
                    markers_tmp = markers.copy()

                    cv2.imwrite(markers_tmp[0].text.__str__() + 'capture.png', frame1)
                    cv2.imshow(markers_tmp[0].text.__str__() + "capture.png", frame1)
                    print('get captured!')
                    gettext.append(int(markers_tmp[0].text))
                    list1 = set(gettext)
                    print(list1)
                    ep_gimbal.moveto(pitch=-120, yaw=0, pitch_speed=30,
                                     yaw_speed=30).wait_for_completed(timeout=2)
                    capturing = False
                    break
                else:
                    speed_x = 30 * error_X
                    speed_y = 30 * error_y
                    ep_gimbal.drive_speed(pitch_speed=-speed_y, yaw_speed=-speed_x)
                    time.sleep(0.005)
                    # return 0
                break
# 获取图片
#####################################################################
if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_robot.set_robot_mode(mode="chassis_lead")

    ep_chassis = ep_robot.chassis
    ep_camera = ep_robot.camera
    ep_led = ep_robot.led
    ep_vision = ep_robot.vision
    ep_gimbal = ep_robot.gimbal
    ep_led.set_led(comp=led.COMP_ALL, r=0, g=0, b=0)

    print("...正在回中云台...")
    ep_gimbal.moveto(pitch=-120, yaw=0, pitch_speed=30, yaw_speed=30).wait_for_completed()
    ep_camera.start_video_stream(display=False, resolution="360p")
# 初始化
#===================================================================while
    while True:
            frame = ep_camera.read_cv2_image(strategy="newest")
            if frame is None:
                continue
            result, pos, p_ret = process(frame)
#####################################################################
            ep_vision.unsub_detect_info(name="line")
            ep_vision.sub_detect_info(name="marker", callback=on_detect_marker)
            if len(markers) > 0 and int(markers[0].text) not in gettext:
                ep_chassis.drive_speed(x=0, y=0, z=0)
                time.sleep(0.5)
                getCapture(frame1=frame)
                ep_gimbal.moveto(pitch=-120, yaw=0, pitch_speed=30, yaw_speed=30).wait_for_completed()
                time.sleep(0.5)
# 检测marker
#####################################################################
            elif p_ret:
                ep_chassis.drive_speed(x=0, y=0, z=0)
                time.sleep(0.5)
                red_light()
                ep_gimbal.moveto(pitch=-120, yaw=0, pitch_speed=30, yaw_speed=30).wait_for_completed()
                time.sleep(0.5)
# 检测红灯
#####################################################################
            elif not (capturing or red_capturing):
                ep_vision.unsub_detect_info(name="marker")
                ep_vision.sub_detect_info(name="line", color="blue", callback=on_detect_line)
                line_tmp = line.copy()
                for j in range(0, len(line_tmp)):
                    cv2.circle(frame, line_tmp[j].pt, 3, line_tmp[j].color, -1)

                if len(line_tmp) > 0:
                    point_x_3 = line_tmp[2]._x
                    error_3 = point_x_3 - 0.5
                    angle_output = 120 * error_3

                    point_x_8 = line_tmp[8]._x
                    error_8 = 0.5 - point_x_8
                    speed_output = 0.85 - 0.6 * abs(error_8)

                    ep_chassis.drive_speed(x=0.2, y=0, z=angle_output)
# 检测线
#==================================================================
    ep_vision.unsub_detect_info(name="line")
    ep_vision.unsub_detect_info(name="marker")
    cv2.destroyAllWindows()
    ep_camera.stop_video_stream()
    ep_robot.close()
#　关闭
####################################################################
