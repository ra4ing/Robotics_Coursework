import time

from pymycobot import MyCobotSocket
import numpy as np
from pymycobot.mycobot import MyCobot


class Arm:
    def __init__(self):
        self.arm = MyCobotSocket("192.168.162.238", 9000)
        self.arm.connect("/dev/ttyAMA0", "1000000")
        # self.arm = MyCobot("/dev/ttyAMA0", "1000000")
        self.set_init_angle()
        self.shift_angle = 6

    def __cal_angle(self, a):
        error = np.array(a) - np.array(self.__get_angle())
        for i in error:
            if abs(i) >= 5:
                return True
        return False

    def __get_angle(self):
        tmp = self.arm.get_angles()
        if len(tmp) == 0:
            return [0, 0, 0, 0, 0, 0]
        else:
            return tmp

    def move_to(self, angle):
        while self.__cal_angle(angle):
            self.arm.sync_send_angles(angle, 40)

    def open_gripper(self):
        while self.arm.get_gripper_value() < 90:
            self.arm.set_gripper_state(0, 30)
            time.sleep(1)

    def close_gripper(self):
        while self.arm.get_gripper_value() > 70:
            self.arm.set_gripper_state(1, 30)
            time.sleep(1)

    def set_init_angle(self):
        self.move_to([0, -20, -70, 5, 100, -90])
        self.open_gripper()

    def set_detect_state_angle(self):
        self.move_to([96.24, 52.11, -64.42, 5, 86.22, -90])

    def grip_book_0(self):
        self.set_init_angle()
        self.move_to([52.03, 16.08, -42.27, -1.75, 90.67, -32.16])

        self.move_to([45.7, 32.34, -41.92, 2.02, 82.26, -39.72])

        self.close_gripper()

        # self.move_to([36.65, 22.14, -71.89, -21.44, 81.91, -59.41])
        self.move_to([0, -20, -70, 5, 100, -90])

    def grip_book_1(self):
        self.set_init_angle()
        self.move_to([29.35, -20.21, -7.91, 7.55, 97.91, -58.27])

        self.move_to([23.46, 20.83, -24.52, 0.79, 80.41, -66.53])

        self.close_gripper()

        # self.move_to([17, 1.49, -45.0, -7, 87.89, -70.92])
        self.move_to([0, -20, -70, 5, 100, -90])

    def grip_book_2(self):
        self.set_init_angle()
        self.move_to([-1.66, -36.65, 1.14, 4.92, 91.23, -95.18])

        self.move_to([4.13, 7.47, -6.5, -2.63, 76.02, -85.25])

        self.close_gripper()

        # self.move_to([-2, 0, -46.75, -7.91, 80, -87.8])
        self.move_to([0, -20, -70, 5, 100, -90])

    def grip_book_3(self):
        self.set_init_angle()
        self.move_to([-32.78, -2.02, -21.97, 5.18, 86.66, -118.82])

        self.move_to([-32.16, 9.05, -6.59, 3.33, 66.79, -117.59])

        self.close_gripper()

        # self.move_to([-46, 0, -70, 20, 100, -112.67])
        self.move_to([0, -20, -70, 5, 100, -90])

    def send_book(self):
        self.move_to([0, -50, -56, 0, 90, -90])

        self.move_to([90, -50, -56, 0, 90, -90])

        self.move_to([90, 0, -42, 0, 10, -90])

        self.close_gripper()

        while self.__cal_angle([75, 0, -42, 0, 10, -90]):
            self.arm.sync_send_angles([75, 0, -42, 0, 10, -90], 5)
        # self.move_to([(90-self.shift_angle), 0, -42, 0, 10, -90])
        # self.shift_angle *= 2

        self.open_gripper()

        self.move_to([75, 2, -66.26, 0, -1, -90])

    def detect_book_0(self):
        self.set_init_angle()
        self.move_to([52.03, 16.08, -42.27, -1.75, 90.67, -32.16])

    def detect_book_1(self):
        self.set_init_angle()
        self.move_to([18.63, 24.52, -36.73, 6.41, 91.66, -70.4])

    def detect_book_2(self):
        self.set_init_angle()
        self.move_to([-5.0, 14.15, -20.65, 4.83, 89.73, -95.18])

    def detect_book_3(self):
        self.set_init_angle()
        self.move_to([-32.78, -2.02, -21.97, 5.18, 86.66, -118.82])


if __name__ == '__main__':
    arm = Arm()
    # arm.grip_book_3()
    # arm.send_book()


