import cv2
from robomaster import *
import time
import random
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
"""
蓝线上点的信息
"""
#####################################################################
distance=[400]
def sub_data_handler(sub_info):
    global distance
    distance = sub_info
##############################################



##############################################
line = []
def on_detect_line(line_info):
    number = len(line_info)
    line.clear()
    if number > 0:
        line_type = line_info[0]
        for i in range(1, number):
            x, y, ceta, c = line_info[i]
            line.append(PointInfo(x, y, ceta, c))
    else:
        print('未识别到线')
"""
识别蓝线并储存
"""
#####################################################################
if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_robot.set_robot_mode(mode='chassis_lead')

    ep_led = ep_robot.led
    ep_camera = ep_robot.camera
    ep_chassis = ep_robot.chassis
    ep_gimbal = ep_robot.gimbal
    ep_camera.start_video_stream(display=False)

    ep_vision = ep_robot.vision
    ep_vision.sub_detect_info(name="line", color="blue", callback=on_detect_line)

    ep_sensor = ep_robot.sensor
    ep_sensor.sub_distance(freq=5, callback=sub_data_handler)
    ep_led.set_led(comp=led.COMP_ALL, r=180, g=255, b=120, effect=led.EFFECT_ON)
    while True:
        img = ep_camera.read_cv2_image(strategy="newest")

        if 400>=distance[0]>300:#减速区
            ep_chassis.drive_speed(x=0.1, y=0, z=0)
            print("---------slow---------")
            print(str(distance[0])+"@")
        elif 300>=distance[0]>100:
            ep_chassis.drive_speed(x=0,y=0,z=0)
            print("---------stop---------")
            print(str(distance[0])+"@")
        elif 100>=distance[0]>1:#后退区
            ep_chassis.drive_speed(x=-0.1,y=0,z=0)
            print("---------back---------")
            print(str(distance[0])+"@")
        else:
            line_tmp = line.copy()
            for j in range(0, len(line_tmp)):
                cv2.circle(img, line_tmp[j].pt, 3, line_tmp[j].color, -1)
            if len(line_tmp) > 0:
                point_x_3 = line_tmp[4]._x
                error_3 = point_x_3 - 0.5
                angle_output = 90 * error_3

                point_x_8 = line_tmp[8]._x
                error_8 = 0.5 - point_x_8
                speed_output = 0.85 - 0.6 * abs(error_8)

                ep_chassis.drive_speed(x=0.25, y=0, z=angle_output)

                print(str(distance[0])+"@")
            else:
                ep_chassis.drive_speed(x=-0.1, y=0, z=0)


        time.sleep(0.001)


        cv2.imshow("Line", img)



        key = cv2.waitKey(1)
        if key == 27:
            print("视频结束")
            ep_chassis.drive_speed(x=0, y=0, z=0)
            break
        #  使用esc快速退出，防止在手动终止时小车不受控情况

    result = ep_vision.unsub_detect_info(name="line")
    cv2.destroyAllWindows()
    ep_camera.stop_video_stream()
    ep_robot.close()
