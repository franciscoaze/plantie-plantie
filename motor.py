from time import sleep
import RPi.GPIO as GPIO


class motor:

    CW = 1  # Clockwise Rotation
    CCW = 0  # Counterclockwise Rotation
    SPR = 400


    def __init__(self):
        self.EN = 16

        self.DIR = 20   # Direction GPIO Pin
        self.STEP = 21  # Step GPIO Pin
        self.LED = 17  # Step GPIO Pin

        self.stop_motor = False

        GPIO.cleanup()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.DIR, GPIO.OUT)
        GPIO.setup(self.STEP, GPIO.OUT)
        #GPIO.setup(self.LED, GPIO.OUT)
        GPIO.setup(self.EN, GPIO.OUT)
        GPIO.output(self.DIR, self.CW)

    def spin(self,dr = 1,step_count = SPR,speed=1000):
        GPIO.output(self.DIR, dr)
        delay = 1.0/speed

        GPIO.output(self.EN, GPIO.LOW)

        #GPIO.output(self.LED, GPIO.HIGH)
        for x in range(step_count):
            GPIO.output(self.STEP, GPIO.HIGH)
            sleep(delay)
            GPIO.output(self.STEP, GPIO.LOW)
            sleep(delay)
        #GPIO.output(self.LED, GPIO.LOW)
        GPIO.output(self.EN, GPIO.HIGH)

    def move(self, err, speed = 4000):
        steps = 0
        direction = 1

        if err != 0:
            steps = abs(err)
            direction = bool((err+steps)/2*steps)
        delay = 1.0/speed

        GPIO.output(self.EN, GPIO.LOW)

        GPIO.output(self.DIR, direction)

        for x in range(steps):
            GPIO.output(self.STEP, GPIO.HIGH)
            sleep(delay)
            GPIO.output(self.STEP, GPIO.LOW)
            sleep(delay)
        GPIO.output(self.EN, GPIO.HIGH)

    def move_cont(self,direction=1):
        GPIO.output(self.EN, GPIO.LOW)
        GPIO.output(self.DIR, direction)
        delay = 1.0/4000
        while not self.stop_motor:
            GPIO.output(self.STEP, GPIO.HIGH)
            sleep(delay)
            GPIO.output(self.STEP, GPIO.LOW)
            sleep(delay)

    def stop(self):
        self.stop_motor = True
        GPIO.output(self.EN, GPIO.HIGH)

    def clean(self):
        GPIO.output(self.EN, GPIO.HIGH)
        GPIO.cleanup()

if __name__ == '__main__':

    m = motor()