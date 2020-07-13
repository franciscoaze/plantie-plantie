#! /home/pi/.virtualenvs/cv/bin/python

import cv2 as cv
import numpy as np
import RPi.GPIO as GPIO
from configs import params
import imutils
from imutils.video import WebcamVideoStream
from motor import motor
from cv2 import aruco
import time
from keyboard_input import TextWindow,KeyTeleop
import curses
import threading
import serial

def centeroidnp(arr):
    length = arr.shape[1]
    sum_x = np.sum(arr[0, :])
    sum_y = np.sum(arr[1, :])
    return sum_x/length, sum_y/length


class Session:
    def __init__(self):
        self.prev = []
        self.found = False
        self.time_in_section = 5
        self.started_section = time.perf_counter()
        self.mode = 'move'

class Agent:

    # PINS
    LED = 17
    BUTTON = 15

    def __init__(self,mode = 'Ar'):

        self.mode = mode

        self.motor = motor()

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.LED,GPIO.OUT)

        # BLOB
        self.blob_detector = cv.SimpleBlobDetector_create(params)

        # ARUCO
        self.aruco_parameters = aruco.DetectorParameters_create()
        self.dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_6X6_250)
        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)

        # Serial
        try:
            self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
            self.ser.flush()
        except:
            self.ser = None

        # Button
        GPIO.setup(self.BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
        GPIO.add_event_detect(self.BUTTON,GPIO.BOTH,callback=self.rising_callback) # Setup event on pin 10 rising edge

        self.limit_switch = False

        self.tr = None

    def rising_callback(self, channel):
        if GPIO.input(self.BUTTON):
            self.limit_switch = True
            self.motor.stop()
        else:
            self.limit_switch = False


    def detect_aruco(self,gray_frame,frame,sess):
        try:
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray_frame, self.aruco_dict, parameters=self.aruco_parameters)
            frame = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
            centroid = centeroidnp(corners[0].transpose())

            #print(f'Id: {ids}, Pos: {centroid}')

            err = int(centroid[0] - 160 / 2)

            if ids[0]:
                id1 = ids[0][0]
                if id1 not in sess.prev:
                    sess.found = True
                    sess.prev.append(id1)
                else:
                    sess.found = False
            #print(f'Stored ids:{sess.prev}')

        except Exception as e:
            #print('ArUco Failed.'+ str(e))
            err = 0
            ids = [[]]
        return frame, err, sess

    def detect_blob(self,frame):
        try:
            keypoints = self.detector.detect(frame)
            for k in keypoints:
                print(f'Position: {k.pt}, Size: {k.size}')
            err= round(keypoints[0].pt[0]-160/2)
            frame = cv.drawKeypoints(frame, keypoints, np.array([]),(0,0,255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        except:
            print('Blob detection failed.')
            err = 0

        return frame, err

    def run(self,teleop):
        add_text="Starting"
        sess = Session()
        vs = WebcamVideoStream(src=-1).start()
        teleop._running = True

        grow_led = False
        while True:
            # Get inputs
            keycode = teleop._interface.read_key()
            if keycode:
                if teleop._key_pressed(keycode):
                    teleop._publish(add_text)
            else:
                teleop._publish(add_text)

            if teleop.LED:
                GPIO.output(self.LED,GPIO.HIGH)
            else:
                GPIO.output(self.LED,GPIO.LOW)

            if teleop.growLED != grow_led:
                if teleop.growLED:
                    val = 200
                else:
                    val = 0
                self.ser.write(f"<LED,{val}\n>".encode('utf-8'))
                line = self.ser.readline().decode('utf-8').rstrip().split(',')
                if line[0][0] == 'T':
                    temp = float(line[0][1:])/100.0;
                    hum = float(line[1][1:])/100.0;
                    teleop.update_values(temp,hum)
                grow_led = not grow_led



            frame = vs.read()
            frame = imutils.resize(frame, width=teleop.img_res)
            frame = cv.flip(frame,0)
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

            if self.mode == 'Ar':
                frame, err, ids = self.detect_aruco(gray, frame,sess)

            elif self.mode == 'blob':
                frame, err = self.detect_blob(frame)

            if teleop.go_home == True:
                if teleop.home_cmd and not self.limit_switch:
                    tr = threading.Thread(target = self.motor.move_cont)
                    tr.start()
                    add_text = "Going home"
                if self.limit_switch:
                    self.motor.stop_motor = False
                    teleop.go_home=False
                    add_text = "Got home"

                teleop.home_cmd = False

            if teleop.move_single == True:
                # move motor x steps
                steps= teleop.mov_steps
                add_text=f"Moving {steps} steps"
                if steps > 0 and self.limit_switch:
                    pass
                else:
                    self.tr = threading.Thread(target = self.motor.move,args=(teleop.mov_steps,teleop.motor_speed))
                    self.tr.start()
                #self.motor.move(teleop.mov_steps,teleop.motor_speed)
                teleop.move_single= False

            if teleop.servo_pos[1] and self.ser is not None:
                # move servo motor
                self.ser.write(f"<SERVO,{teleop.servo_pos[0]}\n>".encode('utf-8'))
                line = self.ser.readline().decode('utf-8').rstrip().split(',')
                if line[0][0] == 'T':
                    temp = float(line[0][1:])/100.0;
                    hum = float(line[1][1:])/100.0;
                    teleop.update_values(temp,hum)
                teleop.servo_pos[1]=False

            teleop.limit_switch = self.limit_switch

            if sess.found:
                # initialize timer
                sess.started_section = time.perf_counter()
                sess.mode = 'stay'
                sess.found = False
                add_text ='Stopping'

            if sess.mode == 'stay':
                obj = err
                #check time
                if time.perf_counter()-sess.started_section>=sess.time_in_section:
                    sess.mode = 'move'
                    add_text = 'Moving'
            elif sess.mode == 'move':
                obj = -30

            #if abs(obj)>10:
             #   self.motor.move(obj)

            # Display the resulting frame
            h,w,_ = frame.shape
            h=int(h)
            cv.line(frame, (0, int(h/2)), (w, int(h/2)), (0, 0, 0), 1)
            cv.line(frame, (int(w/2), h), (int(w/2), 0), (0, 0, 0), 1)
            cv.imshow('frame', frame)
            if cv.waitKey(1) == ord('q'):
                break
            if teleop._running == False:
                break
        # When everything done, release the capture
        vs.stop()
        GPIO.output(self.LED,GPIO.LOW)
        cv.destroyAllWindows()

def main(stdscr):
    teleop = KeyTeleop(TextWindow(stdscr))
    rp = Agent()
    rp.run(teleop)

if __name__ == '__main__':
    curses.wrapper(main)