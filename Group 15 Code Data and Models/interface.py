from tkinter import *
from run import *
import time
from PIL import Image, ImageTk

LOG_LINE_NUM = 0
""" The human-computer interaction interface of the project

        

        
    """

class MY_GUI():
    """The human-computer interaction interface of the project

       This class contains an instantiated object of the Tk and
       ROBOT classes. By creating an object of this class, you 
       can connect with the robot and operate on the robot.

    """
    def __init__(self):
        """init the gui and start the robot
        """
        self.window = Tk()
        self.robot = ROBOT()
        self.window.title("Gargage detection tool")  #wnidows name
        self.window.geometry('1080x640+10+10')
        #label
        self.stream_label = Label(self.window, text="Real-time picture of robot")
        self.stream_label.grid(row=3, column=1)
        self.classify_label = Label(self.window, text="garbage")
        self.classify_label.grid(row=3, column=2)
        self.log_label = Label(self.window, text="log")
        self.log_label.grid(row=5, column=1)
        #video stream
        self.video = Label(self.window)
        self.video.grid(row=4, column=1)
        self.garbage = Label(self.window)
        self.garbage.grid(row=4, column=2)
        #text
        self.log_data_Text = Text(self.window, width=66, height=9)  # log
        self.log_data_Text.grid(row=6, column=1)
        #button
        self.start_button = Button(
            self.window,
            text="start",
            bg="lightblue",
            width=10,
            command=self.start_robot)
        self.start_button.grid(row=1, column=1)
        self.exit_button = Button(self.window,
                                  text="quit",
                                  bg="lightblue",
                                  width=10,
                                  command=self.exit_robot)
        self.exit_button.grid(row=1, column=2)


    def display(self):
        """display the video that obtain by the camera of the robot
        """
        picture = cv2.VideoCapture(0)
        while picture is not None:

            ret, frame = picture.read()  # Read the pictures
            if ret == True:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # Change the color to keep the original color when playing
                current_image = Image.fromarray(img).resize(
                    (540, 320))  # Converts an Image to an image object
                imgtk = ImageTk.PhotoImage(image=current_image)
                self.video.imgtk = imgtk
                self.video.config(image=imgtk)
                self.video.update()

            if self.robot.garbage is not None:
                self.write_log_to_Text("Dectected {}".format(
                    self.robot.garbage))
                self.garbage.imgtk = imgtk
                self.garbage.config(image=imgtk)
                self.robot.garbage = None

    def start_robot(self):
        """let robot begain to patrol
        """
        self.robot.main()
        self.write_log_to_Text("INFO:Robot booting")
        self.write_log_to_Text("...")
        self.write_log_to_Text("...")
        self.write_log_to_Text("INFO:Start success")
        self.write_log_to_Text("INFO:Robot patrolling")

    def exit_robot(self):
        """exit the patrol of the robot
        """
        self.exit_robot.quit()
        self.write_log_to_Text("INFO:Robot quiting")
        self.write_log_to_Text("...")
        self.write_log_to_Text("...")
        self.write_log_to_Text("INFO:Exit success")

    # obtain the current time
    def get_current_time(self):
        """gain current time

        Returns:
            string: current time
        """
        current_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                     time.localtime(time.time()))
        return current_time

    # print the log
    def write_log_to_Text(self, logmsg):
        """write_log_to_Text

        Args:
            logmsg (string): The message that need to be wrote in the log 
        """
        global LOG_LINE_NUM
        current_time = self.get_current_time()
        logmsg_in = str(current_time) + " " + str(logmsg) + "\n"
        if LOG_LINE_NUM <= 7:
            self.log_data_Text.insert(END, logmsg_in)
            LOG_LINE_NUM = LOG_LINE_NUM + 1
        else:
            self.log_data_Text.delete(1.0, 2.0)
            self.log_data_Text.insert(END, logmsg_in)

    def loop(self):
        """the main function to excute the gui
        """
        self.window.mainloop()


def gui_start():
    """start the gui, robot and let robot begain to work
    """
    init_window = MY_GUI()
    init_window.display()
    init_window.loop()


if __name__ == '__main__':
    gui_start()