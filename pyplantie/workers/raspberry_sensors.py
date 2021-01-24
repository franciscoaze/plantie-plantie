"""
Contains all the arduino workers sensors definitions
"""
import copy
import json

try:
    import RPi.GPIO as GPIO
    from gpiozero import CPUTemperature as _CPUTemperature
except ModuleNotFoundError:
    import Mock.GPIO as GPIO

    class _CPUTemperature:
        temperature = 99


class _RaspberrySensor(object):

    def __init__(self, mqtt_client, logger):
        self.client = mqtt_client
        self.logger = logger

    def send_mqtt(self, msg, qos=0):
        self.client.publish(
            topic=self.pub_topic,
            payload=json.dumps(msg),
            qos=qos)

        self.logger.info(f'Sending mqtt to topic {self.pub_topic}: {msg}')


class InternalTemp(_RaspberrySensor):
    pub_topic = 'sensors/rpi/IntTemp'
    sub_topic = "sensors/requests/IntTemp"
    pub_format = {"temperature": 0}

    def execute(self, data: dict, client, logger,  qos=0) -> None:
        """
        Execute worker and send to topic
        """
        cpu = _CPUTemperature()
        alt_msg = copy.deepcopy(self.pub_format)
        alt_msg['temperature'] = cpu.temperature

        self.send_mqtt(alt_msg)


class LimitSwitch(_RaspberrySensor):
    pub_topic = 'sensors/rpi/LimitSwitch'
    sub_topic = "sensors/requests/LimitSwitch"
    pub_format = "Switch: #state#"
    pin = 15

    def __init__(self, mqtt_client, logger):
        super().__init__(mqtt_client, logger)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pin 10 to be an input pin and set initial value to be pulled low (off)
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.rising_callback, bouncetime=1)

    def rising_callback(self, channel):
        self.execute({}, self.client, self.logger)

    def execute(self, data: dict, client, logger,  qos=0) -> None:
        """
        Execute worker and send to topic
        """
        new_state = GPIO.input(self.pin)
        alt_msg = copy.deepcopy(self.pub_format)
        alt_msg = alt_msg.replace(f"#state#", str(new_state))

        self.send_mqtt(alt_msg)
