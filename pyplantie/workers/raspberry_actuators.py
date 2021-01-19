"""
Contains all the rpi workers actuators definitions
"""
try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)


class _RPIActuator(object):
    def __init__(self, mqtt_client, logger):
        self.client = mqtt_client
        self.logger = logger


class WhiteLED(_RPIActuator):
    sub_topic = "actions/whiteled"
    pin = 17

    def __init__(self, mqtt_client, logger):
        super().__init__(mqtt_client, logger)
        GPIO.setup(self.pin, GPIO.OUT)

    def execute(self, data: dict, logger):
        new_state = data.get('value')
        if new_state == 'ON':
            GPIO.output(self.pin, GPIO.HIGH)
        elif new_state == 'OFF':
            GPIO.output(self.pin, GPIO.LOW)
        self.logger.info(f'White Led is now {new_state}')


# class Webcam(_RPIActuator):
#     sub_topic = "actions/webcam"

