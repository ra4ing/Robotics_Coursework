import time

from Robot import Robot
from Connector import Connector

import keyboard


def detect_marker(connector):
    connector.send_command("detect_marker")


def judge_marker(connector):
    response = connector.send_command("have_marker?")
    if response['output']:
        return True, response['marker_id']
    else:
        return False, -1


def set_detect_state(connector):
    print(connector.send_command("start_detect")['output'])


def grip_book(connector, marker_id):
    print(connector.send_grip_book_command(marker_id))


def have_over(connector):
    return connector.send_command('over?')['over']


def main():
    robot = Robot()
    robot.change_to_follow_line()

    connector = Connector()
    set_detect_state(connector)

    detect_time = time.time()
    last_marker_id = -2
    shelf = 3
    turn_back = True

    while True:

        if shelf >= 4:
            if turn_back:
                robot.adjust_self()
                robot.back_to_start()
                turn_back = False

        have_marker, marker_id = False, -1
        # 检查标签
        if time.time() - detect_time >= 0.5:
            detect_marker(connector)
            have_marker, marker_id = judge_marker(connector)
            detect_time = time.time()

        # 检查是否到达标签与送书
        if have_marker and marker_id != last_marker_id:
            shelf += 1
            robot.adjust_self()
            print("detected marker: " + str(marker_id))
            # send_book(connector, marker_id)
            grip_book(connector, marker_id)
            set_detect_state(connector)
            last_marker_id = marker_id

            robot = Robot()
            robot.change_to_follow_line()

        else:
            robot.follow_line()
            # robot.chassis.drive_speed(x=0.1, y=0, z=0)
            # robot.adjust_self()

        # 退出
        if keyboard.is_pressed('esc'):
            break


if __name__ == '__main__':
    main()
