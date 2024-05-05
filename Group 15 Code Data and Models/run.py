from robomaster import *
import time
import torch
import torchvision
from PIL import Image
import cv2

class ROBOT():
    """the robot with its unit and function
    """
    def __init__(self) -> None:
        self.garbage = None
        self.ep_robot = robot.Robot()
        self.ep_robot.initialize(conn_type='ap')
        self.ep_robot.set_robot_mode(mode="chassis_lead")

        self.ep_chassis = self.ep_robot.chassis
        self.ep_camera = self.ep_robot.camera
        self.ep_led = self.ep_robot.led
        self.ep_vision = self.ep_robot.vision
        self.ep_gimbal = self.ep_robot.gimbal
        self.ep_blaster = self.ep_robot.blaster

        self.state = 4
        self.last_state = 4
        self.time_stop = 10
        self.time_last = time.process_time()
        self.time_cur = time.process_time()
        self.time_tmp1 = 0

    def quit(self):
        """quit the robot
        """
        cv2.destroyAllWindows()
        self.ep_camera.stop_video_stream()
        self.ep_robot.close()


    def on_detected_people(self):
        """when the robot detect people, it will stop and wait for 5 seconds
        """
        time.sleep(5)
        time_last += 5
        

    def getCapture(self,frame):
        """adjudge whether there is garbage in the frame the gain from the robot's camera

        Args:
            frame (image): the image gain from robot

        Returns:
            bool: if there is garbage
        """
        image = Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))

        transform = torchvision.transforms.Compose([
            torchvision.transforms.Resize((256, 256)),
            torchvision.transforms.ToTensor()
        ])

        image = transform(image)

        model = torch.load("ra4ing_100.pth", map_location=torch.device('cpu'))

        image = torch.reshape(image, (1, 3, 256, 256))
        model.eval()
        with torch.no_grad():
            output = model(image)
        
        classification = {
            0: "其他垃圾一次性快餐盒",
            1: "可回收易拉罐",
            2: "可回收饮料瓶"
        }

        flag = 0
        idx = output.argmax(1).item()
        minn = 99999
        for i in range(len(output[0])):
            if i != idx:
                minn = min(minn, output[0][idx].item() - output[0][i].item())
        if minn > 4:
            flag = 1
            self.garbage = classification.get(output.argmax(1).item())
            print("检测到{}垃圾".format(classification.get(output.argmax(1).item())))
        return flag


    def alert(self):
        """when robot find garbage, alert
        """
        self.ep_led.set_led(comp=led.COMP_ALL, r=255, g=0, b=0,freq=0.5)
        self.ep_led.set_gimbal_led(comp='top_all',
                    r=255,
                    g=0,
                    b=0,
                    led_list=[0, 1, 2, 3],
                    effect='on')
        self.ep_blaster.set_led(brightness=255, effect='on')
        self.ep_blaster.fire('ir',20)


    def change_speed(self):
        """the route of the robot's patrol
        """
        #当前运行方向
        states = {
            0: 15, # 前进时间
            1: 30, # 左移时间
            2: 60, # 右移时间
            3: 30, # 回到主路时间
            4: 2   # 开始等待时间
        }
        #当前运行方向速度
        speeds = {
            0: (0.2, 0),
            1: (0,-0.2),
            2: (0,-0.2),
            3: (0,-0.2),
            4: (0,0)
        }
        time_cur = time.perf_counter()
        if time_cur-time_last>states.get(self.state):
            if self.state == 4:
                self.state = 0
            else:
                if self.last_state == 0 and self.state == 1:
                    self.ep_chassis.move(0,0,180).wait_for_completed()
                elif self.last_state == 1 and self.state == 2:
                    self.ep_chassis.move(0,0,180).wait_for_completed()
                self.last_state = self.state
                self.state = (self.state+1)%4
            x,y = speeds.get(self.state)
            self.ep_chassis.drive_speed(x,y)
            time_last = time_cur


    def led_recover(self):
        """after alert, the robot's led will recover from red
        """
        self.ep_led.set_led(comp=led.COMP_ALL, r=0, g=0, b=0,freq=0.5)
        self.ep_led.set_gimbal_led(comp='top_all',
                    r=0,
                    g=0,
                    b=0,
                    led_list=[0, 1, 2, 3],
                    effect='on')
        self.ep_blaster.set_led(brightness=0, effect='on')


    def process(self,frame):
        """gain image and control robot to do something

        Args:
            frame (image): gain from the robot's camera
        """
        if self.getCapture(frame):
            self.ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
            self.alert()
            time.sleep(self.time_stop)
            time_last += self.time_stop
            time_tmp += self.time_stop + 5
            self.led_recover()


    def detect_people(self):
        """Turn the gimbal to the direction of robot movement to detect pedestrians
        """
        self.ep_chassis.drive_speed(0,0)
        angle = 0

        if self.state == 0:
            angle = 0
        elif self.state == 1:
            angle = -90
        elif self.state == 2:
            angle = -90
        elif self.state == 3:
            angle = -90
        
        self.ep_gimbal.moveto(pitch=-110, yaw=angle, pitch_speed=180, yaw_speed=180).wait_for_completed()
        self.ep_vision.sub_detect_info("person", callback=self.on_detected_people)
        time.sleep(1)
        time_last+=1
        self.ep_vision.unsub_detect_info("person")
        self.ep_gimbal.moveto(pitch=-110, yaw=0, pitch_speed=180, yaw_speed=180).wait_for_completed()
        

        frame = self.ep_camera.read_cv2_image(strategy="newest")
        if frame is not None:
            self.process(frame)

        # recover
        speeds = {
            0: (0.2, 0),
            1: (0,-0.2),
            2: (0,-0.2),
            3: (0,-0.2),
            4: (0,0)
        }
        x,y = speeds.get(self.state)
        self.ep_chassis.drive_speed(x,y)


    def main(self):
        """the main function of robot's patrol
        """
        #===============================初始化==============================#
        self.ep_led.set_led(comp=led.COMP_ALL, r=0, g=0, b=0)
        self.ep_gimbal.moveto(pitch=-110, yaw=0, pitch_speed=30, yaw_speed=30).wait_for_completed()
        self.ep_camera.start_video_stream(display=False, resolution="360p")
        

        #===============================遍历实验室===============================#
        self.time_last = time.perf_counter()
        self.time_tmp1 = time.perf_counter()
        self.time_tmp2 = time.perf_counter()

        while True:
            # gain image
            frame = self.ep_camera.read_cv2_image(strategy="newest")
            if frame is None:
                continue

            time_now = time.perf_counter()
            # Images are detected every 0.3 seconds
            if time_now - time_tmp1 > 0.3:
                time_tmp1 = time.perf_counter()
                self.process(frame)
            
            # Pedestrian detection every 1 second
            if time_now - time_tmp2 > 5:
                time_tmp2 = time.perf_counter()
                self.detect_people()
            
            # Follow the prescribed route
            self.change_speed()

            # Press Q to exit
            key = cv2.waitKey(1)
            if cv2.waitKey(25) & 0xFF == ord('Q'):
                break

