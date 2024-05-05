import cv2
from robomaster import *
import time


class Robot:
    def __init__(self):
        self.robot = robot.Robot()
        self.robot.initialize(conn_type="sta", sn="3JKCH9B00102L5")
        self.robot.set_robot_mode(mode="chassis_lead")

        self.chassis = self.robot.chassis
        self.camera = self.robot.camera
        self.vision = self.robot.vision
        self.sensor = self.robot.sensor

        self.__line = []

        self.camera.start_video_stream(display=False, resolution="360p")
        self.sensor.sub_distance(freq=10, callback=self.__stop)

        self.distance = 200

    def back_to_start(self):
        self.distance = -1
        self.chassis.move(0, 0, 180, z_speed=30).wait_for_completed()
        self.distance = 200
        # time.sleep(10)

    def __stop(self, distance):
        if distance[0] < self.distance:
            self.chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)

    def adjust_self(self):
        # self.chassis.drive_speed(x=0, y=0, z=0.49)
        self.chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)

    def get_frame(self):
        return self.camera.read_cv2_image(strategy="newest")

    def change_to_follow_line(self):
        self.vision.sub_detect_info(name="line", color="red", callback=self.__on_detect_line)

    def follow_line(self):
        """ 巡线

        : param line_info 线信息
        """

        line_tmp = self.__line.copy()
        # for j in range(0, len(line_tmp)):
        #     cv2.circle(self.get_frame(), line_tmp[j].pt, 3, line_tmp[j].color, -1)

        if len(line_tmp) > 0:
            point_x_3 = line_tmp[2].x
            error_3 = point_x_3 - 0.5
            angle_output = 60 * error_3

            self.chassis.drive_speed(x=0.1, y=0, z=angle_output)

    def __on_detect_line(self, line_info):
        """ 用于获得marker信息

        : param line_info 线信息
        """

        number = len(line_info)
        self.__line.clear()
        if number > 0:
            for i in range(1, number):
                x, y, ceta, c = line_info[i]
                self.__line.append(PointInfo(x, y, ceta, c))

    def __del__(self):
        self.chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
        self.robot.close()


class PointInfo:
    def __init__(self, x, y, theta, c):
        self.x = x
        self.y = y
        self.theta = theta
        self.c = c

    @property
    def pt(self):
        return int(self.x * 1280), int(self.y * 720)

    @property
    def color(self):
        return 255, 255, 255
