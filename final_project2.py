from tkinter import *
from PIL import Image, ImageTk
import cv2
import smtplib
import numpy as np
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
import time
import depthai as dai
import os
import requests
####################################################################################
#set gpio
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(12,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(19,GPIO.OUT)

GPIO.setup(27,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)
  
GPIO.output(22,True)   #yellow
GPIO.output(23,True)   #green
GPIO.output(24,True)   #buzz
GPIO.output(27,False)   #red

pwm1 = GPIO.PWM(12,1000)#left pwm
pwm2 = GPIO.PWM(13,1000)#right pwm
pwm3 = GPIO.PWM(18,1000)#left pwm
pwm4 = GPIO.PWM(19,1000)#right pwm

pwm1.start(0)
pwm2.start(0)
pwm3.start(0)
pwm4.start(0)

####################################################################################

# Closer-in minimum depth, disparity range is doubled (from 95 to 190):
extended_disparity = False
# Better accuracy for longer distance, fractional disparity 32-levels:
subpixel = False
# Better handling for occlusions:
lr_check = True

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
depth = pipeline.create(dai.node.StereoDepth)
xout = pipeline.create(dai.node.XLinkOut)

xout.setStreamName("disparity")

# Properties
monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

# Create a node that will produce the depth map (using disparity output as it's easier to visualize depth this way)
depth.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
# Options: MEDIAN_OFF, KERNEL_3x3, KERNEL_5x5, KERNEL_7x7 (default)
depth.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
depth.setLeftRightCheck(lr_check)
depth.setExtendedDisparity(extended_disparity)
depth.setSubpixel(subpixel)

# Linking
monoLeft.out.link(depth.left)
monoRight.out.link(depth.right)
depth.disparity.link(xout.input)

# Define source and output
camRgb = pipeline.create(dai.node.ColorCamera)
xoutVideo = pipeline.create(dai.node.XLinkOut)

xoutVideo.setStreamName("video")

# Properties
camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setVideoSize(1920, 1080)

xoutVideo.input.setBlocking(False)
xoutVideo.input.setQueueSize(1)

# Linking
camRgb.video.link(xoutVideo.input)
###########################################################################################
#Email Variables
SMTP_SERVER = 'smtp.gmail.com' #Email Server (don't change!)
SMTP_PORT = 587 #Server Port (don't change!)
GMAIL_USERNAME = 'uibu714@gmail.com' #change this to match your gmail account
GMAIL_PASSWORD = 'huaymjdlllueggyd' #change this to match your gmail app-password

class Emailer:
    def sendmail(self, recipient, subject, content):

        #Create Headers
        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient,
                   "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)

        #Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()

        #Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

        #Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
        session.quit

sender = Emailer()
sendTo = 'sswk07939@gmail.com'
emailSubject = "Robot is start"
emailContent = "Robot is start at: " + time.ctime()

token = 'hyC9fWKj6RY6z5jeNmGoQhSvoWou0BntxYjU9aBhnBx'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': f'Bearer {token}'
}
url = 'https://notify-api.line.me/api/notify'

###############################################################################################################
speed = 20
speed_multiplier = 3
state_beep = True
time_for_beep = time.time()
def beep(lamp = 24):
    global state_beep
    state_beep = not state_beep
    GPIO.output(lamp,state_beep)
    #print("beep")
    
time_befor = time.time()
turn_left = False
turn_right = False
turn_forward = False
lock_forward = False
turn_reverse = False

def left_turn():
    global time_befor
    global turn_left
    global turn_right
    global turn_forward
    global lock_forward
    global turn_reverse
    #print("<")
    turn_left = True
    turn_right = False
    turn_forward = False
    turn_reverse = False
    lock_forward = False
    time_befor = time.time()

def right_turn():
    global time_befor
    global turn_left
    global turn_right
    global turn_forward
    global lock_forward
    global turn_reverse
    #print(">")
    turn_left = False
    turn_right = True
    turn_forward = False
    turn_reverse = False
    lock_forward = False
    time_befor = time.time()
    
def forward():
    global time_befor
    global turn_left
    global turn_right
    global turn_forward
    global lock_forward
    global turn_reverse
    #print("^")
    turn_left = False
    turn_right = False
    turn_forward = True
    turn_reverse = False
    lock_forward = False
    time_befor = time.time()
    
def forward_turn():
    global time_befor
    global turn_left
    global turn_right
    global turn_forward
    global lock_forward
    global turn_reverse
    #print("⟰")
    turn_left = False
    turn_right = False
    turn_forward = False
    turn_reverse = False
    lock_forward = not lock_forward
    time_befor = time.time()
    
def reverse_turn():
    global time_befor
    global turn_left
    global turn_right
    global turn_forward
    global lock_forward
    global turn_reverse
    #print("˅")
    turn_left = False
    turn_right = False
    turn_forward = False
    turn_reverse = True
    lock_forward = False
    time_befor = time.time()
    
def condition_manual():
    global time_befor
    global turn_left
    global turn_right
    global turn_forward
    global lock_forward
    global turn_reverse
    global time_for_beep
    global speed
    global speed_multiplier
    global Bt4
    if((time.time() - time_for_beep) > 1):
        time_for_beep = time.time()
        GPIO.output(22,False)   #yellow
        GPIO.output(23,True)   #green
        GPIO.output(27,True)   #red
        beep(24)
    if turn_left :
        if((time.time() - time_befor) < 1):
            pwm1.ChangeDutyCycle(0)#left pwm
            pwm3.ChangeDutyCycle(speed*speed_multiplier)#left2 pwm
            pwm2.ChangeDutyCycle(speed*speed_multiplier)#right pwm
            pwm4.ChangeDutyCycle(0)#right2 pwm
            #print("left")
            Bt4.configure(bg="#ABC456")
        else :
            turn_left = False
            turn_right = False
            turn_forward = False
            lock_forward = False
            turn_reverse = False
            pwm1.ChangeDutyCycle(0)#left pwm
            pwm3.ChangeDutyCycle(0)#left2 pwm
            pwm2.ChangeDutyCycle(0)#right pwm
            pwm4.ChangeDutyCycle(0)#right2 pwm
    elif turn_right :
        if((time.time() - time_befor) < 1):
            pwm1.ChangeDutyCycle(speed*speed_multiplier)#left pwm
            pwm3.ChangeDutyCycle(0)#left2 pwm
            pwm2.ChangeDutyCycle(0)#right pwm
            pwm4.ChangeDutyCycle(speed*speed_multiplier)#right2 pwm
            #print("right")
            Bt4.configure(bg="#ABC456")
        else :
            turn_left = False
            turn_right = False
            turn_forward = False
            lock_forward = False
            turn_reverse = False
            pwm1.ChangeDutyCycle(0)#left pwm
            pwm3.ChangeDutyCycle(0)#left2 pwm
            pwm2.ChangeDutyCycle(0)#right pwm
            pwm4.ChangeDutyCycle(0)#right2 pwm
    elif turn_forward :
        if((time.time() - time_befor) < 1):
            pwm1.ChangeDutyCycle(speed*speed_multiplier)#left pwm
            pwm3.ChangeDutyCycle(0)#left2 pwm
            pwm2.ChangeDutyCycle(speed*speed_multiplier)#right pwm
            pwm4.ChangeDutyCycle(0)#right2 pwm
            #print("forward")
            Bt4.configure(bg="#ABC456")
        else :
            turn_left = False
            turn_right = False
            turn_forward = False
            lock_forward = False
            turn_reverse = False
            pwm1.ChangeDutyCycle(0)#left pwm
            pwm3.ChangeDutyCycle(0)#left2 pwm
            pwm2.ChangeDutyCycle(0)#right pwm
            pwm4.ChangeDutyCycle(0)#right2 pwm
    elif turn_reverse :
        if((time.time() - time_befor) < 1):
            pwm1.ChangeDutyCycle(0)#left pwm
            pwm3.ChangeDutyCycle(speed*speed_multiplier)#left2 pwm
            pwm2.ChangeDutyCycle(0)#right pwm
            pwm4.ChangeDutyCycle(speed*speed_multiplier)#right2 pwm
            #print("reverse")
            Bt4.configure(bg="#ABC456")
        else :
            turn_left = False
            turn_right = False
            turn_forward = False
            lock_forward = False
            turn_reverse = False
            pwm1.ChangeDutyCycle(0)#left pwm
            pwm3.ChangeDutyCycle(0)#left2 pwm
            pwm2.ChangeDutyCycle(0)#right pwm
            pwm4.ChangeDutyCycle(0)#right2 pwm
    elif lock_forward :
            pwm1.ChangeDutyCycle(speed*speed_multiplier)#left pwm
            pwm3.ChangeDutyCycle(0)#left2 pwm
            pwm2.ChangeDutyCycle(speed*speed_multiplier)#right pwm
            pwm4.ChangeDutyCycle(0)#right2 pwm
            #print("lock forward")
            
            Bt4.configure(bg="red")
    else :
        turn_left = False
        turn_right = False
        turn_forward = False
        lock_forward = False
        turn_reverse = False
        pwm1.ChangeDutyCycle(0)#left pwm
        pwm3.ChangeDutyCycle(0)#left2 pwm
        pwm2.ChangeDutyCycle(0)#right pwm
        pwm4.ChangeDutyCycle(0)#right2 pwm
        
        Bt4.configure(bg="#ABC456")

left = 0
right = 0
left2 = 0
right2 = 0
track_left = False
track_right = False
time_for_forward_in_track_line = time.time()
def codition_track_line():
    global left
    global right
    global track_left
    global track_right
    global time_for_forward_in_track_line
    global time_for_beep
    global mode
    global speed
    global speed_multiplier
    if((time.time() - time_for_beep) > 1):
        time_for_beep = time.time()
        GPIO.output(22,True)   #yellow
        GPIO.output(23,False)   #green
        GPIO.output(27,True)   #red
        beep(24)
    if track_left :
        if((time.time() - time_for_forward_in_track_line) < 5.5):
            pwm1.ChangeDutyCycle(25)#left pwm
            pwm3.ChangeDutyCycle(0)#left2 pwm
            pwm2.ChangeDutyCycle(25)#right pwm
            pwm4.ChangeDutyCycle(0)#right2 pwm
            #print("forward")
        elif(right < 100):
            pwm1.ChangeDutyCycle(0)#left pwm
            pwm3.ChangeDutyCycle(8)#left2 pwm
            pwm2.ChangeDutyCycle(8)#right pwm
            pwm4.ChangeDutyCycle(0)#right2 pwm    
        else :
            track_left = False
            pwm1.ChangeDutyCycle(0)#left pwm
            pwm3.ChangeDutyCycle(0)#left2 pwm
            pwm2.ChangeDutyCycle(0)#right pwm
            pwm4.ChangeDutyCycle(0)#right2 pwm
    elif track_right :
        if((time.time() - time_for_forward_in_track_line) < 4):
            pwm1.ChangeDutyCycle(speed*speed_multiplier)#left pwm
            pwm3.ChangeDutyCycle(0)#left2 pwm
            pwm2.ChangeDutyCycle(speed*speed_multiplier)#right pwm
            pwm4.ChangeDutyCycle(0)#right2 pwm
            #print("forward")
        elif(left < 100):
            pwm1.ChangeDutyCycle(10)#left pwm
            pwm3.ChangeDutyCycle(0)#left2 pwm
            pwm2.ChangeDutyCycle(0)#right pwm
            pwm4.ChangeDutyCycle(10)#right2 pwm    
        else :
            track_right = False
            pwm1.ChangeDutyCycle(0)#left pwm
            pwm3.ChangeDutyCycle(0)#left2 pwm
            pwm2.ChangeDutyCycle(0)#right pwm
            pwm4.ChangeDutyCycle(0)#right2 pwm
        
    elif((left > 100) and (right < 100) and (left2 > 100) and (right2 < 100)):
        track_left = True
        time_for_forward_in_track_line = time.time()
    elif((left < 100) and (right > 100) and (left2 < 100) and (right2 > 100)):
        track_right = True
        time_for_forward_in_track_line = time.time()
    elif((left > 100) and (right < 100)):
        pwm1.ChangeDutyCycle(0)#left pwm
        pwm3.ChangeDutyCycle(0)#left2 pwm
        pwm2.ChangeDutyCycle(25)#right pwm
        pwm4.ChangeDutyCycle(0)#right2 pwm
    elif((left < 100) and (right > 100)):
        pwm1.ChangeDutyCycle(25)#left pwm
        pwm3.ChangeDutyCycle(0)#left2 pwm
        pwm2.ChangeDutyCycle(0)#right pwm
        pwm4.ChangeDutyCycle(0)#right2 pwm
    else:
        pwm1.ChangeDutyCycle(speed*speed_multiplier)#left pwm
        pwm3.ChangeDutyCycle(0)#left2 pwm
        pwm2.ChangeDutyCycle(speed*speed_multiplier)#right pwm
        pwm4.ChangeDutyCycle(0)#right2 pwm

def unknown():
    pass
def Select_mode_1():
    global Mode
    global Bt1
    global Bt2
    global Bt3
    Bt1.place_forget()
    Bt2.place_forget()
    Bt3.place_forget()
    Bt4.place_forget()
    Bt6.place_forget()
    Mode = 1

def Select_mode_2():
    global Mode
    global Bt1
    global Bt2
    global Bt3
    global lock_forward
    lock_forward = False
    Bt1.place(x=200,y=800)
    Bt2.place(x=575,y=720)
    Bt3.place(x=950,y=800)
    Bt4.place(x=575,y=600)
    Bt6.place(x=575,y=820)
    Mode = 2
    
h1 = 18
s1 = 40
v1 = 20
h2 = 22
s2 = 255
v2 = 255

def enter_hsv():
    global h1
    global s1
    global v1
    global h2
    global s2
    global v2
    if(E1.get().isnumeric()):
        h1 = int(E1.get())
    else:
        message =  'Please enter number for hsv'+"\nกรุณาป้อนค่า HSV เป็นตัวเลขเท่านั้น "
        r = requests.post(url=url, headers=headers, data={'message': message})
    if(E2.get().isnumeric()):
        s1 = int(E2.get())
    else:
        message =  'Please enter number for hsv'+"\nกรุณาป้อนค่า HSV เป็นตัวเลขเท่านั้น "
        r = requests.post(url=url, headers=headers, data={'message': message})
    if(E3.get().isnumeric()):
        v1 = int(E3.get())
    else:
        message =  'Please enter number for hsv'+"\nกรุณาป้อนค่า HSV เป็นตัวเลขเท่านั้น "
        r = requests.post(url=url, headers=headers, data={'message': message})
    if(E4.get().isnumeric()):
        h2 = int(E4.get())
    else:
        message =  'Please enter number for hsv'+"\nกรุณาป้อนค่า HSV เป็นตัวเลขเท่านั้น "
        r = requests.post(url=url, headers=headers, data={'message': message})
    if(E5.get().isnumeric()):
        s2 = int(E5.get())
    else:
        message =  'Please enter number for hsv'+"\nกรุณาป้อนค่า HSV เป็นตัวเลขเท่านั้น "
        r = requests.post(url=url, headers=headers, data={'message': message})
    if(E6.get().isnumeric()):
        v2 = int(E6.get())
    else:
        message =  'Please enter number for hsv'+"\nกรุณาป้อนค่า HSV เป็นตัวเลขเท่านั้น "
        r = requests.post(url=url, headers=headers, data={'message': message})
    if(h1 > 180):
        h1 = 180
    elif(h1 < 0):
        h1 = 0
    if(s1 > 255):
        s1 = 255
    elif(s1 < 0):
        s1 = 0
    if(v1 > 255):
        v1 = 255
    elif(v1 < 0):
        v1 = 0
    if(h2 > 180):
        h2 = 180
    elif(h2 < 0):
        h2 = 0
    if(s2 > 255):
        s2 = 255
    elif(s2 < 0):
        s2 = 0
    if(v2 > 255):
        v2 = 255
    elif(v2 < 0):
        v2 = 0
    E1.delete(0, 100)
    E1.insert(0, h1)
    E2.delete(0, 100)
    E2.insert(0, s1)
    E3.delete(0, 100)
    E3.insert(0, v1)
    E4.delete(0, 100)
    E4.insert(0, h2)
    E5.delete(0, 100)
    E5.insert(0, s2)
    E6.delete(0, 100)
    E6.insert(0, v2)

def quit_():
    global win
    GPIO.output(22,True)   #yellow
    GPIO.output(23,True)   #green
    GPIO.output(24,True)   #buzz
    GPIO.output(27,False)   #red
    pwm1.ChangeDutyCycle(0)#left pwm
    pwm3.ChangeDutyCycle(0)#left2 pwm
    pwm2.ChangeDutyCycle(0)#right pwm
    pwm4.ChangeDutyCycle(0)#right2 pwm
    emailSubject = "Robot is stop"
    emailContent = "Robot is stop at: " + time.ctime()
    sender.sendmail(sendTo, emailSubject, emailContent)
    message =  'Stop at : ' + time.ctime() +"\nหุ่นยนต์หยุดทำงาน ณ เวลา " + time.ctime()
    r = requests.post(url=url, headers=headers, data={'message': message})
    time.sleep(2)
    os._exit(os.EX_OK)

##############################################################################################
def scaleup(val):
    global speed
    global speed_multiplier
    speed_multiplier = scale.get()
    #print(speed*speed_multiplier)
##############################################################################################
# Create an instance of TKinter Window or frame
win = Tk()
win.title("Project")
win.geometry("1280x1024")
#win.attributes('-fullscreen',True)
# Create a Label to capture the Video frames
label =Label(win)
label.place(x=64,y=100)
label2 =Label(win)
label2.place(x=704,y=100)
Label1 = Label(win,text="SWEEPER ROBOTIC",fg="#FFFFFF",font=('Times New Roman',60),bg="#ABC456").pack()

Bt1 = Button(win,text=" ⇦ ",fg="#FFFFFF",font=('Times New Roman',60),bg="#ABC456",command=left_turn)
Bt2 = Button(win,text=" ⇧ ",fg="#FFFFFF",font=('Times New Roman',60),bg="#ABC456",command=forward)
Bt3 = Button(win,text=" ⇨ ",fg="#FFFFFF",font=('Times New Roman',60),bg="#ABC456",command=right_turn)
Bt4 = Button(win,text=" ⟰ ",fg="#FFFFFF",font=('Times New Roman',60),bg="#ABC456",command=forward_turn)
Bt5 = Button(win,text=" X ",fg="#FFFFFF",font=('Times New Roman',20),bg="red",command=quit_)
Bt5.place(x=1215,y=0)
Bt6 = Button(win,text=" ⇩ ",fg="#FFFFFF",font=('Times New Roman',60),bg="#ABC456",command=reverse_turn)

R1 = Button(text="AUTO",font=('Times New Roman',60),bg="green",command=Select_mode_1)
R1.place(x=230,y=600)
R2 = Button(text="MANUAL",font=('Times New Roman',60),bg="white",command=Select_mode_2)
R2.place(x=800,y=600)

E1 = Entry(win, bd =5 ,	width = 3)
E2 = Entry(win, bd =5 ,	width = 3)
E3 = Entry(win, bd =5 ,	width = 3)
E4 = Entry(win, bd =5 ,	width = 3)
E5 = Entry(win, bd =5 ,	width = 3)
E6 = Entry(win, bd =5 ,	width = 3)

E1.delete(0, 3)
E1.insert(0, h1)
E2.delete(0, 3)
E2.insert(0, s1)
E3.delete(0, 3)
E3.insert(0, v1)
E4.delete(0, 3)
E4.insert(0, h2)
E5.delete(0, 3)
E5.insert(0, s2)
E6.delete(0, 3)
E6.insert(0, v2)

E1.place(x=704,y=520)
E2.place(x=754,y=520)
E3.place(x=804,y=520)
E4.place(x=894,y=520)
E5.place(x=944,y=520)
E6.place(x=984,y=520)
Label_to = Label(win,text="to",fg="green",font=('Times New Roman',20))
Label_to.place(x=855,y=515)
Label_hsv = Label(win,text="H     S     V          H     S     V",fg="green",font=('Times New Roman',20))
Label_hsv.place(x=704,y=485)
button_hsv = Button(text="Enter",font=('Times New Roman',30),command=enter_hsv)
button_hsv.place(x=1060,y=500)

Mode = 0

scale = Scale(
    win,from_=0,to=4,bd = 20,fg = "white",
    length=400,
    bg = "chartreuse4",
    highlightbackground = "white",
    troughcolor = "CadetBlue1",
    orient=VERTICAL,
    command=scaleup,
    font=('Times New Roman', 30)
)
scale.set(3)
scale.place(x=10,y=500)

Mode = 1
def Mode_show():
    global Mode
    global R1
    global R2
    global left
    global right
    global left2
    global right2
    if(Mode == 1):
        R1.configure(bg="green")
        R2.configure(bg="white")
        codition_track_line()
        #print(str(left2)+"  "+str(left)+"  "+str(right)+"  "+str(right2))
    elif(Mode == 2):
        R1.configure(bg="white")
        R2.configure(bg="green")
        condition_manual()
##############################################################################################
stop_robot = False
detect = 0
times_for_stop_robot = 0
sent_line = 0
# Connect to device and start pipeline
emailSubject = "Robot is start"
emailContent = "Robot is start at : " + time.ctime()
sender.sendmail(sendTo, emailSubject, emailContent)
message =  'Start at : ' + time.ctime() +"\nหุ่นยนต์เริ่มทำงาน ณ เวลา " + time.ctime()
r = requests.post(url=url, headers=headers, data={'message': message})
time.sleep(5)
with dai.Device(pipeline) as device:

    # Output queue will be used to get the disparity frames from the outputs defined above
    q = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)
    video = device.getOutputQueue(name="video", maxSize=1, blocking=False)
    count = 0
    fps = []
    while True:
        time_fps = time.time()
        inDisparity = q.get()  # blocking call, will wait until a new data has arrived
        frame = inDisparity.getFrame()
        # Normalization for better visualization
        frame = (frame * (255 / depth.initialConfig.getMaxDisparity())).astype(np.uint8)
        resize = cv2.resize(frame, (512, 384))
        resize = cv2.threshold(resize, 170, 255, cv2.THRESH_BINARY)[1]
        detect = np.count_nonzero(resize == 255)
        #print(detect)
        videoIn = video.get()
        videoIn = videoIn.getCvFrame()
        resize2 = cv2.resize(videoIn, (512, 384))
        resize2 = cv2.cvtColor(resize2, cv2.COLOR_BGR2RGB)
        resize2_hsv = cv2.cvtColor(resize2, cv2.COLOR_RGB2HSV)
        inr = cv2.inRange(resize2_hsv,np.array([h1,s1,v1] ),np.array([h2,s2,v2]))
        p1 = [ 97,328,150,381]
        p2 = [177,328,230,381]
        p3 = [332,328,385,381]
        p4 = [412,328,462,381]
        cv2.rectangle(inr,(p1[0],p1[1]),(p1[2],p1[3]),(255,255,255),2)
        cv2.rectangle(inr,(p2[0],p2[1]),(p2[2],p2[3]),(255,255,255),2)
        cv2.rectangle(inr,(p3[0],p3[1]),(p3[2],p3[3]),(255,255,255),2)
        cv2.rectangle(inr,(p4[0],p4[1]),(p4[2],p4[3]),(255,255,255),2)
        left2_count  = inr[p1[1]+2:p1[3]-1,p1[0]+2:p1[2]-1]
        left_count   = inr[p2[1]+2:p2[3]-1,p2[0]+2:p2[2]-1]
        right_count  = inr[p3[1]+2:p3[3]-1,p3[0]+2:p3[2]-1]
        right2_count = inr[p4[1]+2:p4[3]-1,p4[0]+2:p4[2]-1]
        left2  = np.count_nonzero(left2_count  == 255)
        left   = np.count_nonzero(left_count   == 255)
        right  = np.count_nonzero(right_count  == 255)
        right2 = np.count_nonzero(right2_count == 255)
        #print(str(left2)+"  "+str(left)+"  "+str(right)+"  "+str(right2))
        img = Image.fromarray(resize2)
        img2 = Image.fromarray(inr)
        imgtk = ImageTk.PhotoImage(image = img)
        imgtk2 = ImageTk.PhotoImage(image = img2)
        # Update the left label with the new frame
        label.imgtk = imgtk
        label.configure(image=imgtk)
        # Update the right label with the new frame
        label2.imgtk = imgtk2
        label2.configure(image=imgtk2)
        win.update()
        fps.append(time.time() - time_fps)
        if(len(fps) >= 50):
            Label3 = Label(win,text="FPS = "+str(int(1/(sum(fps)/len(fps)))),fg="green",font=('Times New Roman',15)).place(x=10,y=10)
            #print("FPS = ",int(1/(sum(fps)/len(fps))))
            fps.clear()
        if(detect > 10000):
            turn_forward = False
            condition_manual()
            
        if((detect > 10000) and (stop_robot == False)):
            stop_robot = True
            times_for_stop_robot = time.time()
            pwm1.ChangeDutyCycle(0)#left pwm
            pwm3.ChangeDutyCycle(0)#left2 pwm
            pwm2.ChangeDutyCycle(0)#right pwm
            pwm4.ChangeDutyCycle(0)#right2 pwm
            sent_line = sent_line + 1
        elif((time.time() - times_for_stop_robot) < 5):
            #print(time.time() - times_for_stop_robot)
            if((time.time() - time_for_beep) > 1):
                #time_for_beep = time.time()
                GPIO.output(22,True)   #yellow
                GPIO.output(23,True)   #green
                GPIO.output(27,False)   #red
                #beep(24)
        elif(stop_robot == True):
            stop_robot = False
        else :
            sent_line = 0
            Mode_show()
        if(sent_line == 1):
            sent_line = sent_line + 1
            message =  'Detect object at : ' + time.ctime() +"\nตรวจพบสิ่งกีดขวาง ณ เวลา " + time.ctime()
            r = requests.post(url=url, headers=headers, data={'message': message})
        elif((sent_line > 1) and (detect < 1500)):
            sent_line = 0
            message =  'Robot is working : ' + time.ctime()+"\nหุ่นยนต์กลับมาทำงาน ณ เวลา " + time.ctime()
            r = requests.post(url=url, headers=headers, data={'message': message})
        #print(str(detect)+"   "+str(stop_robot))
