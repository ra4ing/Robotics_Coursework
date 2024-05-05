import time
import cv2
import cv2.aruco as aruco
import numpy as np


class Camera:
    def __init__(self):
        self.camera = None
        self.have_marker = False
        self.marker_id = -1

    def detect_marker(self, detect_time=1):
        self.have_marker = False
        self.marker_id = -1
        self.camera = cv2.VideoCapture(0)
        start_time = time.time()
        while (time.time() - start_time) <= detect_time:
            ret, frame = self.camera.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
            parameters = aruco.DetectorParameters()

            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

            if np.all(ids is not None):  # 检测到aruco标记
                self.have_marker = True
                for mid in ids:
                    self.marker_id = int(mid)
                    print("#########", self.marker_id)
                break
        if self.camera.isOpened():
            self.camera.release()

    def __del__(self):
        self.camera.release()  # 释放摄像头


if __name__ == '__main__':
    camera = Camera()
    for i in range(10):
        camera.detect_marker()
        print(camera.have_marker)
        print(i)
