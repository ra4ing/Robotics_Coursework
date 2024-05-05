import time

from Robot import Robot
from Connector import Connector

import keyboard


def detect_marker(connector):
    print(connector.send_command("detect_marker")['output'])


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


# def send_book(connector, marker_id):
#     response = None
#     if marker_id == 0:
#         response = connector.send_command("grip_up_book_0")
#     elif marker_id == 1:
#         response = connector.send_command("grip_up_book_1")
#     elif marker_id == 2:
#         response = connector.send_command("grip_up_book_2")
#     elif marker_id == 3:
#         response = connector.send_command("grip_up_book_3")
#     print(response['output'])


def main():
    connector = Connector()
    set_detect_state(connector)

    detect_time = time.time()
    last_marker_id = -2
    count = 0

    while True:

        have_marker, marker_id = False, -1
        # 检查标签
        if time.time() - detect_time >= 1:
            detect_marker(connector)
            have_marker, marker_id = judge_marker(connector)
            detect_time = time.time()

        # 检查是否到达标签与送书
        if have_marker and marker_id != last_marker_id:
            print("detected marker: " + str(marker_id))
            # send_book(connector, marker_id)
            grip_book(connector, marker_id)
            set_detect_state(connector)
            last_marker_id = marker_id
            count += 1

        # 退出
        if keyboard.is_pressed('esc'):
            break


if __name__ == '__main__':
    main()
